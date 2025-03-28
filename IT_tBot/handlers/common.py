from aiogram import types
from aiogram.dispatcher import Dispatcher
import json
from keyboards import create_keyboard_from_file, load_buttons_config
import logging
from .common_button import send_keyboard

logger = logging.getLogger(__name__)

# --- Константы и пути ---
COMMANDS_CONFIG_PATH = "./handlers/commands_config.json"
BUTTONS_CONFIG_PATH = "./keyboards/buttons_config.json"


# --- Вспомогательные функции ---
def load_commands_config(filepath: str) -> dict:
    """Загружает конфигурацию команд из JSON файла."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["commands"]
    except FileNotFoundError:
        logger.error(f"Файл конфигурации не найден: {filepath}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Ошибка декодирования JSON в файле: {filepath}")
        return {}


async def send_text_from_file(message: types.Message, description: str):
    """Отправляет описание команды, соответствующей тексту сообщения."""
    if description:
        await message.reply(description)
    else:
        await message.reply("Описание для данной команды не найдено.")


async def echo(message: types.Message):
    """Обработчик для эхо-сообщений."""
    await message.answer(
        "Те че надо? Жмакай кнопки. Используй /start"
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
            # elif command_config["response_type"] == "file":
            #     await send_file(message, command_config["filename"])
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


def register_common_handler(dp: Dispatcher):
    commands = load_commands_config(COMMANDS_CONFIG_PATH)

    for command_name, command_config in commands.items():
        handler = create_command_handler(command_config)

        dp.register_message_handler(handler, commands=[command_name])
    dp.register_message_handler(echo)


# def register_common_handler(dp: Dispatcher):
#     dp.register_message_handler(
#         start_command, commands=["start"]
#     )  # Correctly registers /start

#     dp.register_message_handler(
#         start_command, commands=["AltCode"]
#     )  # Correctly registers /start

#     dp.register_message_handler(echo)  # Registers echo
