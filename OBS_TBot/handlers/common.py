# handlers/common.py
import os
import re
import json
import logging
import asyncio
from aiogram import types
from datetime import datetime
from aiogram.types import ParseMode
from config_loader import ConfigLoader
from aiogram.dispatcher import Dispatcher
from .file_reader import load_jsons
from .common_button import send_keyboard
from .reminder import stop_reminder, start_reminder
from .common_file import (  # Import the functions from file_utils.py
    send_file_section,
    send_sections_list,
    send_commands_list,
    delete_command,
)
from .registration import cmd_reg, process_full_name, Registration, process_email

logger = logging.getLogger(__name__)

# --- Инициализация ConfigLoader ---
config_loader = ConfigLoader()


async def send_text_from_description(message: types.Message, description: str):
    """Отправляет описание команды, соответствующей тексту сообщения."""
    if description:
        await message.reply(description)
    else:
        await message.reply("Описание для данной команды не найдено.")


async def echo(message: types.Message):
    """Обработчик для эхо-сообщений."""
    # await message.answer(
    #     "Неизвестная команда. Введите /start."
    # )  # Сообщение без клавиатуры.

    tmp_msg = "Неизвестная команда, если вы хотите зарегестрироваться на вебинар - нажмите кнопку ниже ⬇️"
    await send_keyboard(message, tmp_msg, "registration")


def create_command_handler(command_config: dict):
    """Фабрика для создания обработчиков на основе command_config."""

    async def handler(message: types.Message):
        try:
            if command_config["response_type"] == "text":
                await send_text_from_description(message, command_config["description"])
            elif command_config["response_type"] == "keyboard":
                await send_keyboard(
                    message, command_config["description"], command_config["category"]
                )
            elif (
                command_config["response_type"] == "file_section"
            ):  # Отправка содержимого секции
                section = 1  # Default section

                if "file_section" in command_config:

                    logging.info(
                        f'Нашли webinar_ = {int(command_config["file_section"])}'
                    )
                    section = int(command_config["file_section"])
                    # logger.info(f"ЕСТЬ [file_section] !")
                else:
                    logger.info(f"Нету [file_section]")

                # Extract section number from command text
                match = re.match(r"/sec_(\d+)", message.text)

                # logging.info(match)
                if match:
                    logging.info(f"Нашли sec_ = {int(match.group(1))}")

                    section = int(match.group(1))

                parse_mode = command_config.get(
                    "parse_mode",
                    # ParseMode.MARKDOWN_V2
                )  # Default to Markdown if not specified
                await send_file_section(
                    message, command_config["filename"], section, parse_mode
                )
            elif (
                command_config["response_type"] == "file_sections"
            ):  # Отправка списка секций
                await send_sections_list(message, command_config["filename"])
            elif (
                command_config["response_type"] == "file_commands"
            ):  # Отправка списка секций
                await send_commands_list(message)
            elif command_config["response_type"] == "":  # Отправка списка секций
                await send_sections_list(message, command_config["filename"])
            else:
                logger.warning(
                    f"Неизвестный response_type: {command_config['response_type']}"
                )
                await message.reply("Неизвестный тип ответа.")
        except KeyError as e:
            logger.error(f"Отсутствует необходимый ключ в конфигурации: {e}")
            await message.reply("Ошибка в конфигурации команды.")
        except Exception as e:
            logger.exception(f"Ошибка при обработке команды: {e}")
            await message.reply("Произошла ошибка при обработке запроса.")

    return handler


async def delete_command_handler(message: types.Message):
    """Обработчик команды /delete_command."""
    try:
        # Извлекаем имя команды из сообщения.  Предполагаем, что команда вводится как:
        # /delete_command /command_name
        command_name = message.text.split()[1]  # Получаем второй элемент (имя команды)
        print("command_name = " + command_name)
        await delete_command(message, command_name)
    except IndexError:
        await message.reply(
            "Пожалуйста, укажите имя команды для удаления.  Пример: `/delete_command /command_name`",
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as e:
        logger.exception(f"Ошибка в обработчике команды /delete_command: {e}")
        await message.reply(f"Произошла ошибка при обработке команды: {e}")


async def remove_all_registrations(message: types.Message):
    """Обработчик команды /remove_all_registrations для очистки списка зарегистрированных пользователей."""
    try:
        # Загружаем текущих пользователей
        users = load_jsons("data/users.json")

        if not users:
            await message.reply("📭 Список пользователей уже пуст.")
            return

        # Очищаем список пользователей
        users.clear()

        # Сохраняем изменения в файл
        with open("data/users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

        # Подтверждаем успешное выполнение
        await message.reply(
            "✅ Список зарегистрированных пользователей успешно очищен."
        )

    except Exception as e:
        logger.exception(f"Ошибка в обработчике команды /remove_all_registrations: {e}")
        await message.reply(f"❌ Произошла ошибка при очистке списка: {e}")


async def create_new_command(message: types.Message):
    """Обработчик команды /create_command."""
    try:
        # Разделяем сообщение на строки
        lines = message.text.split("\n")

        # Получаем имя команды (предполагаем, что оно первое)
        command_name = lines[0].split(" ")[1].strip()

        # Создаем словарь для хранения параметров команды
        command_params = {}

        # Обрабатываем остальные строки (параметры)
        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)  # Разделяем только по первому ":"
                key = key.strip()
                value = value.strip()
                command_params[key] = value

        # Load existing commands
        commands = config_loader.load_commands_config()

        # Add the new command
        commands[command_name] = command_params

        # Save the updated commands
        config_loader.save_commands_config(commands)

        await message.reply(
            f"Команда `{command_name}` успешно создана.", parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        logger.exception(f"Ошибка при создании команды: {e}")
        await message.reply(f"Произошла ошибка при создании команды: {e}")


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


async def update_webinar_link(message: types.Message):
    """Обработчик команды /update_webinar_link для изменения ссылки на вебинар."""

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
        await stop_reminder()
        await start_reminder(message.bot)

        await message.reply(
            f"✅ Ссылка на вебинар успешно обновлена:\n{new_link}",
            parse_mode=ParseMode.MARKDOWN,
        )

    except Exception as e:
        await message.reply(f"❌ Произошла ошибка при обновлении ссылки: {e}")


async def update_webinar_datetime(message: types.Message):
    """Обработчик команды /update_webinar_datetime для изменения даты и времени вебинара."""

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
        await stop_reminder()
        await start_reminder(message.bot)

        # Подтверждение успешного обновления
        await message.reply(
            f"✅ Дата и время вебинара успешно обновлены на: {new_webinar_datetime.strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode=ParseMode.MARKDOWN,
        )

    except Exception as e:
        await message.reply(f"❌ Произошла ошибка при обновлении даты и времени: {e}")


async def stop_reminder_command(message: types.Message):
    await stop_reminder()
    await message.reply("❌ Напоминание остановлено.")


def register_common_handler(dp: Dispatcher):
    commands = config_loader.load_commands_config()

    for command_name, command_config in commands.items():
        handler = create_command_handler(command_config)

        dp.register_message_handler(handler, commands=[command_name])

    for command_name, command_config in commands.items():
        if command_name == "sec_":
            # Register the handler with a regular expression to match /sec_<number>
            dp.register_message_handler(
                create_command_handler(command_config), regexp_commands=[f"sec_(\d+)"]
            )

    dp.register_message_handler(cmd_reg, commands=["reg"])
    dp.register_message_handler(
        process_full_name, state=Registration.waiting_for_full_name
    )
    dp.register_message_handler(process_email, state=Registration.waiting_for_email)

    dp.register_message_handler(
        remove_all_registrations, commands=["remove_all_registrations"]
    )
    dp.register_message_handler(
        update_webinar_datetime, commands=["update_webinar_datetime"]
    )
    dp.register_message_handler(update_webinar_link, commands=["update_webinar_link"])

    dp.register_message_handler(stop_reminder_command, commands=["stop_reminder"])
    dp.register_message_handler(create_new_command, commands=["create_command"])
    dp.register_message_handler(delete_command_handler, commands=["delete_command"])
    dp.register_message_handler(echo)
