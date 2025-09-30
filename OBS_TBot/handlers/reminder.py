# handlers/reminder.py
import os
import json
import asyncio
from aiogram import Bot
from datetime import datetime, timedelta
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, UserDeactivated
from .google_sheets import send_data_to_google_sheets
from .file_reader import (
    save_jsons,
    load_jsons,
    get_webinar_time,
    get_timezone,
    get_webinar_link,
)

active_tasks = {}


def calculate_reminder_time(webinar_time: datetime, relative_time: str) -> datetime:
    """
    Рассчитывает точное время для напоминания на основе времени вебинара и относительного времени.
    """
    time_map = {
        "days": timedelta(days=1),
        "hours": timedelta(hours=1),
        "minutes": timedelta(minutes=1),
        "seconds": timedelta(seconds=1),
    }

    amount, unit = relative_time.split()
    amount = int(amount)

    # Используем словарь для получения timedelta и вычисляем время напоминания
    return webinar_time - time_map[unit] * amount


async def update_user_block_status(bot: Bot):
    """
    Один раз обновляет статус available для всех пользователей.
    """
    users = load_jsons("data/users.json")
    if not users:
        print("📭 Нет пользователей для обновления статуса.")
        return

    updated_count = 0
    for user in users:
        user_id = user.get("user_id")
        if not user_id:
            continue

        try:
            await bot.send_chat_action(user_id, "choose_sticker")
            user["available"] = True
            print(f"✅ Доступен: {user_id}")
        except (BotBlocked, ChatNotFound, UserDeactivated) as e:
            user["available"] = False
            print(f"❌ Не доступен: {user_id} | {e}")
        except Exception as e:
            print(f"⚠️ Some ошибка {user_id}: {type(e).__name__}: {e}")
            continue  # Переходим к следующему

        # 🔄 сразу отправляем обновлённого пользователя в Google Sheets
    try:
        send_data_to_google_sheets(users)
    except Exception as e:
        print(f"⚠️ Ошибка отправки в Google Sheets: {e}")

        updated_count += 1
        await asyncio.sleep(0.05)  # Анти-лимит от Telegram

    save_jsons("data/users.json", users)
    print(f"📊 Статус обновлён для {updated_count} пользователей.")


async def send_reminder_to_users(bot: Bot, text: str, include_link: bool = False):
    """
    Отправляет сообщение только активным пользователям (не заблокировали бота).
    """
    users = load_jsons("data/users.json")
    if not users:
        print("📭 Нет пользователей для рассылки.")
        return 0

    sent_count = 0
    full_text = text + (get_webinar_link() if include_link else "")

    for user in users:
        user_id = user.get("user_id")
        if not user_id or user.get("available", True):
            continue

        try:
            await bot.send_message(chat_id=user_id, text=full_text, parse_mode="HTML")
            print(f"✅ Отправлено: {user_id}")
            sent_count += 1
        except Exception as e:
            print(f"❌ Ошибка отправки {user_id}: {e}")
        await asyncio.sleep(0.05)  # анти-спам

    return sent_count


async def schedule_webinar_reminder(bot: Bot):
    """
    Планирует напоминания до вебинара.
    Перед первой рассылкой обновляет статус блокировки.
    """
    webinar_time = get_webinar_time()
    reminders = load_jsons("data/reminders.json")

    if not reminders:
        print("📭 Нет напоминаний для планирования.")
        return

    now = datetime.now(get_timezone())

    for reminder in reminders:
        delay = (
            calculate_reminder_time(webinar_time, reminder["time"]) - now
        ).total_seconds()

        if delay <= 0:
            print(f"⏭ Пропущено: '{reminder['label']}' (устарело)")
            continue

        print(f"⏳ Напоминание '{reminder['label']}' через {delay:.0f} сек")
        await asyncio.sleep(delay)

        # Обновляем статус — актуально для этого момента
        await update_user_block_status(bot)

        # Отправляем с учётом свежих данных
        sent = await send_reminder_to_users(
            bot=bot, text=reminder["text"], include_link=bool(reminder.get("last"))
        )

        print(f"📬 '{reminder['label']}' отправлено {sent} пользователям.")

        # Обновляем текущее время для следующей итерации
        now = datetime.now(get_timezone())


async def periodic_task(bot, interval: int = 60):
    """
    Периодическая задача с фиксированной задержкой (например, раз в минуту).
    """
    while True:
        print(f"⏰ Периодическая задача {datetime.now()}")
        # тут твоя логика (например, проверка или обновление статусов)
        await update_user_block_status(bot)
        await asyncio.sleep(interval)  # ждать фиксированное время


async def start_reminder(bot):
    """Запускает рассылку напоминаний, если она ещё не запущена."""
    if "webinar_reminder" in active_tasks:
        print("Напоминание уже запущено.")
        return

    task = asyncio.create_task(schedule_webinar_reminder(bot))
    active_tasks["webinar_reminder"] = task
    task = asyncio.create_task(periodic_task(bot, 60))
    active_tasks["periodic_task"] = task

    print("✅ Напоминание запущено.")


async def stop_reminder():
    """Останавливает активную задачу напоминания."""
    task = active_tasks.pop("webinar_reminder", None)
    if task:
        task.cancel()
        try:
            await task  # Дожидаемся отмены, чтобы подавить CancelledError
        except asyncio.CancelledError:
            pass  # Игнорируем — это ожидаемо
        print("❌ Напоминание отменено.")


async def on_startup_reg(dp):
    """Функция, вызываемая при старте бота."""
    bot = dp.bot
    print("Бот запущен. Запускаем напоминание...")
    await start_reminder(bot)
