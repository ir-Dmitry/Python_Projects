from aiogram import types
from aiogram.dispatcher import Dispatcher
import json
import logging
from .common_button import send_keyboard
from config_loader import ConfigLoader
from aiogram.types import ParseMode
from aiogram.utils.markdown import escape_md
from .common_file import (  # Import the functions from file_utils.py
    send_file_section,
    send_sections_list,
    send_commands_list,
    delete_command,
)
import re

logger = logging.getLogger(__name__)

# --- Инициализация ConfigLoader ---
config_loader = ConfigLoader()


async def send_text_from_file(message: types.Message, description: str):
    """Отправляет описание команды, соответствующей тексту сообщения."""
    if description:
        await message.reply(description)
    else:
        await message.reply("Описание для данной команды не найдено.")


async def echo(message: types.Message):
    """Обработчик для эхо-сообщений."""
    await message.answer(
        "Те че надо? Жмакай кнопки. Используй /start или /commands"
    )  # Сообщение без клавиатуры.


def create_command_handler(command_config: dict):
    """Фабрика для создания обработчиков на основе command_config."""

    async def handler(message: types.Message):
        try:
            if command_config["response_type"] == "text":
                await send_text_from_file(message, command_config["description"])
            elif command_config["response_type"] == "keyboard":
                await send_keyboard(
                    message, command_config["description"], command_config["category"]
                )
            elif (
                command_config["response_type"] == "file_section"
            ):  # Отправка содержимого секции
                section = 1  # Default section
                # Extract section number from command text
                match = re.match(r"/sec_(\d+)", message.text)
                # logging.info(match)
                if match:
                    section = int(match.group(1))

                parse_mode = command_config.get(
                    "parse_mode", ParseMode.MARKDOWN_V2
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
    dp.register_message_handler(create_new_command, commands=["create_command"])
    dp.register_message_handler(delete_command_handler, commands=["delete_command"])
    dp.register_message_handler(echo)
