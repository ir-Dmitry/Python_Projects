# handlers/webinar_handlers.py
import os
from aiogram import types
from datetime import datetime
from aiogram.types import ParseMode

from ..logger import get_logger
from ..reminder import stop_reminders, start_reminders
from .admin_handlers import admin_only


logger = get_logger("common", "common.log")


async def update_webinar_link(message: types.Message):
    """Обработчик команды /update_webinar_link для изменения ссылки на вебинар."""

    if not await admin_only(message):
        return
    try:
        # Получаем новую ссылку из текста команды
        new_link = message.get_args().strip()

        # Проверка на пустое значение
        if not new_link:
            await message.reply(
                "❌ Пожалуйста, укажите ссылку. Пример: `/update_webinar_link https://example.com/webinar`"
            )
            return

        # Заменяем значение переменной в файле .env
        with open(".env", "r", encoding="utf-8") as file:
            lines = file.readlines()

        with open(".env", "w", encoding="utf-8") as file:
            found = False
            for line in lines:
                if line.startswith("WEBINAR_LINK="):
                    file.write(f'WEBINAR_LINK="{new_link}"\n')
                    found = True
                else:
                    file.write(line)
            if not found:
                file.write(f'WEBINAR_LINK="{new_link}"\n')  # Добавляем, если не было

        # Обновляем переменную окружения
        os.environ["WEBINAR_LINK"] = new_link

        # Перезапускаем напоминание
        await stop_reminders()
        await start_reminders(message.bot)

        await message.reply(
            f"✅ Ссылка на вебинар успешно обновлена:\n{new_link}",
            parse_mode=ParseMode.MARKDOWN,
        )

    except Exception as e:
        await message.reply(f"❌ Произошла ошибка при обновлении ссылки: {e}")


async def update_webinar_datetime(message: types.Message):
    """Обработчик команды /update_webinar_datetime для изменения даты и времени вебинара."""

    if not await admin_only(message):
        return
    try:
        # Получаем новое время из текста команды
        new_datetime_str = message.get_args().strip()

        # Проверка на пустое значение
        if not new_datetime_str:
            await message.reply(
                "❌ Пожалуйста, укажите дату и время в формате 'YYYY-MM-DD HH:MM:SS'. Пример: `/update_webinar_datetime 2025-08-06 12:00:00`"
            )
            return

        # Проверка на правильность формата даты
        try:
            new_webinar_datetime = datetime.strptime(
                new_datetime_str, "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            await message.reply(
                "❌ Неверный формат даты и времени. Используйте формат 'YYYY-MM-DD HH:MM:SS'."
            )
            return

        # Заменяем значение переменной в файле .env
        with open(".env", "r") as file:
            lines = file.readlines()

        # Открываем файл для записи
        with open(".env", "w") as file:
            for line in lines:
                if line.startswith("WEBINAR_DATETIME="):
                    # Заменяем старое значение на новое
                    file.write(
                        f"""WEBINAR_DATETIME="{new_webinar_datetime.strftime('%Y-%m-%d %H:%M:%S')}"\n"""
                    )
                else:
                    file.write(line)

        # Обновляем переменную окружения
        os.environ["WEBINAR_DATETIME"] = new_webinar_datetime.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        # Перезапуск напоминания
        await stop_reminders()
        await start_reminders(message.bot)

        # Подтверждение успешного обновления
        await message.reply(
            f"✅ Дата и время вебинара успешно обновлены на: {new_webinar_datetime.strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode=ParseMode.MARKDOWN,
        )

    except Exception as e:
        await message.reply(f"❌ Произошла ошибка при обновлении даты и времени: {e}")


async def stop_reminders_command(message: types.Message):
    if not await admin_only(message):
        return
    await stop_reminders()
    await message.reply("❌ Напоминание остановлено.")
