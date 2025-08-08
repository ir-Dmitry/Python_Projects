# handlers/reminder.py
import asyncio
from aiogram import Bot
from datetime import datetime, timedelta
from .file_reader import load_jsons
from .file_reader import load_jsons, get_webinar_time, get_timezone, get_webinar_link

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


async def schedule_webinar_reminder(bot: Bot):
    """
    Запускает напоминания до вебинара, используя данные из JSON.
    """
    webinar_time = get_webinar_time()
    now = datetime.now(get_timezone())
    reminders = load_jsons("data/reminders.json")  # Загружаем напоминания из JSON файла

    for reminder in reminders:
        reminder_time = calculate_reminder_time(webinar_time, reminder["time"])
        delay = (reminder_time - now).total_seconds()

        if delay > 0:

            msg = f"⏳ Напоминание {reminder['label']} запланировано на {reminder_time} (через {delay:.0f} сек)"
            print(msg)

            await asyncio.sleep(delay)  # Ожидание до времени напоминания

            users = load_jsons("data/users.json")
            if users is None:
                print("Ошибка при загрузке данных пользователей.")
                continue

            user_ids = [user["user_id"] for user in users if "user_id" in user]

            if not user_ids:
                print("📭 Нет зарегистрированных пользователей.")
                continue

            print(
                f"📨 Рассылка {reminder['label']} для {len(user_ids)} пользователей..."
            )

            if reminder["last"] == True:
                print("Ссылка: ", get_webinar_link())
            else:
                print("Пусто")

            for user_id in user_ids:
                try:
                    await bot.send_message(
                        chat_id=user_id,
                        text=(
                            reminder["text"] + get_webinar_link()
                            if reminder["last"] == True
                            else ""
                        ),
                        parse_mode="HTML",
                    )
                    print(f"✅ Отправлено: {user_id}")
                except Exception as e:
                    print(f"❌ Ошибка для {user_id}: {e}")
                await asyncio.sleep(0.05)  # анти-спам

            # Обновляем текущее время после сна
            now = datetime.now(get_timezone())
            print(f"Напоминание '{reminder['label']}' отправлено.")
        else:
            print(
                f"Напоминание '{reminder['label']}' пропущено, так как время уже прошло."
            )


async def start_reminder(bot):
    if "webinar_reminder" in active_tasks:
        print("Напоминание уже запущено.")
        return
    task = asyncio.create_task(schedule_webinar_reminder(bot))
    active_tasks["webinar_reminder"] = task

    print("✅ Напоминание запущено.")


async def stop_reminder():
    task = active_tasks.get("webinar_reminder")
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            print("❌ Напоминание отменено.")
        del active_tasks["webinar_reminder"]


async def on_startup_reg(dp):  # ← параметр — dp (диспетчер)
    bot = dp.bot  # ← получаем бота из диспетчера
    print("Бот запущен. Запускаем напоминание...")
    await start_reminder(bot)
    # asyncio.create_task(schedule_webinar_reminder(bot))
