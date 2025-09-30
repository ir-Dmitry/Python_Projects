# handlers/registration.py
import re
import os
import json
import logging
from typing import Union  # ← добавь этот импорт
from aiogram import types
from datetime import datetime
from zoneinfo import ZoneInfo  # работает только с Python 3.9+
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from .google_sheets import send_data_to_google_sheets
from .file_reader import load_jsons, get_webinar_time

# Логи
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("logs/registration.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

moscow_time = datetime.now(ZoneInfo("Europe/Moscow"))
print(f"Московское время: {moscow_time}")

ERROR_MESSAGES = {
    "timeout": "⚠️ Данные не отправлены в Google Таблицу (таймаут).",
    "connection_error": "⚠️ Нет подключения к Google Таблице.",
    "api_error": "⚠️ Ошибка Google API.",
    "unknown_error": "⚠️ Неизвестная ошибка при сохранении в Google Таблицу.",
}


def format_registration_message(tmp_time, gs_result="success") -> str:
    msg = (
        "✅ <b>Регистрация завершена!</b>\n\n"
        f"🗓 Дата вебинара: {tmp_time.date()}.\n"
        f"🕰 Время: {tmp_time.strftime('%H:%M')}.\n"
        "Напоминание о вебинаре придет вовремя."
    )
    if gs_result != "success":
        msg += "\n\n" + ERROR_MESSAGES.get(gs_result, "⚠️ Неизвестная ошибка.")
    return msg


def load_users(path="data/users.json") -> list:
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    return load_jsons(path)


def save_users(users: list, path="data/users.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def add_user(user_id: int, path="data/users.json") -> dict:
    users = load_users(path)
    if any(u["user_id"] == user_id for u in users):
        return None  # уже зарегистрирован
    user = {
        "user_id": user_id,
        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "available": True,
    }
    users.append(user)
    save_users(users, path)
    return user


async def process_simple_reg(obj: Union[types.Message, types.CallbackQuery]):
    user_id = obj.from_user.id
    logger.info(f"process_simple_reg: ID={user_id}, Username=@{obj.from_user.username}")

    response = save_registration_without_full_name(user_id)

    target = obj.message if isinstance(obj, types.CallbackQuery) else obj
    if isinstance(obj, types.CallbackQuery):
        await obj.answer()
    await target.answer(response, parse_mode="HTML")


def save_registration_without_full_name(user_id: int) -> str:
    try:
        user = add_user(user_id)
        if user is None:
            return (
                "⚠️ <b>Вы уже зарегистрированы</b> на вебинар.\n\n"
                "Не волнуйтесь — напоминание придет вовремя!"
            )

        tmp_time = get_webinar_time()
        gs_result = send_data_to_google_sheets(user)
        return format_registration_message(tmp_time, gs_result)

    except (AttributeError, OSError, json.JSONDecodeError) as e:
        logger.error(
            f"Ошибка при сохранении данных пользователя {user_id}: {e}", exc_info=True
        )
        return (
            "❌ Ошибка при сохранении данных.\n"
            "Попробуйте позже или свяжитесь с поддержкой."
        )
    except Exception as e:
        logger.exception(f"Непредвиденная ошибка для пользователя {user_id}: {e}")
        return (
            "❌ Произошла непредвиденная ошибка.\n"
            "Пожалуйста, попробуйте позже или свяжитесь с поддержкой."
        )
