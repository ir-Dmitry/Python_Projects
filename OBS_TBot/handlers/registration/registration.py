# handlers/registration.py
import json
from typing import Union  # ← добавь этот импорт
from aiogram import types

from ..logger import get_logger
from .users import add_user
from ..file_reader import get_webinar_time
from ..google_sheets import send_data_to_google_sheets
from .messages import format_registration_message

logger = get_logger("registration", "registration.log")


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
