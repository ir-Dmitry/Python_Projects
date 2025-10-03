# handlers/startup.py
import logging
import asyncio
from aiogram import types
from aiogram.dispatcher import Dispatcher
from .users import add_user
from ..logger import get_logger

logger = get_logger("startup", "startup.log")


async def on_startup_common(dp: Dispatcher):
    """Обрабатываем пропущенные сообщения и пропускаем их для polling"""
    try:
        # Получаем все пропущенные обновления
        updates = await dp.bot.get_updates(limit=100, timeout=1)

        if updates:
            user_ids = set()
            for update in updates:
                if update.message:
                    user_ids.add(update.message.from_user.id)

            # Отправляем уведомление
            for user_id in user_ids:
                try:
                    await dp.bot.send_message(
                        user_id,
                        "🔧 Извините, бот был перезагружен.\n"
                        "Пожалуйста, повторите ваш запрос.",
                    )
                except Exception as e:
                    logging.error(f"Не удалось отправить {user_id}: {e}")
                await asyncio.sleep(0.05)

            print(f"⚠️ Уведомлено {len(user_ids)} пользователей о перезагрузке.")

            # ——— КЛЮЧЕВАЯ СТРОКА ———
            # Указываем, что все обновления до этого — обработаны
            last_update_id = updates[-1].update_id
            await dp.bot.get_updates(offset=last_update_id + 1, limit=1, timeout=0)
            # Это "подтверждает" приём обновлений — Telegram не пришлёт их снова

        else:
            print("✅ Нет пропущенных сообщений.")

    except Exception as e:
        logging.error(f"Ошибка в on_startup: {e}")

    print("✅ Бот запущен и готов к работе.")


# Обработчик /start
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    print(f"User: ID={user_id}, Username=@{username}")

    # Добавляем пользователя в файл all_users.json
    added = add_user(user_id, username)
    if added:
        print(f"✅ Привет! Твой ID сохранён: {user_id}")
    else:
        print(f"✅ С возвращением! Ты уже в базе: {user_id}")
