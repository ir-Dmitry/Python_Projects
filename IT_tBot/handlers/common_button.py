from aiogram import types
from aiogram.dispatcher import Dispatcher
from keyboards import create_keyboard_from_file, load_buttons_config
import logging

logger = logging.getLogger(__name__)

# --- Константы и пути ---
BUTTONS_CONFIG_PATH = "./keyboards/buttons_config.json"


async def send_keyboard(message: types.Message, description: str, category: str):
    """Отправляет клавиатуру с описанием."""
    try:
        buttons_config = load_buttons_config(BUTTONS_CONFIG_PATH)
        keyboard = create_keyboard_from_file(
            buttons_config, category, 1
        )  # Assuming row_width=1
        if keyboard:
            await message.reply(description, reply_markup=keyboard)
        else:
            await message.reply("Ошибка при создании клавиатуры.")
    except Exception as e:
        logger.exception(f"Ошибка при отправке клавиатуры: {e}")
        await message.reply("Произошла ошибка при обработке запроса.")


async def handle_callback(
    callback_query: types.CallbackQuery,
    categories: list[str] = None,
    row_width: int = 2,
):
    """
    Обработчик callback-запросов от inline-кнопок.

    Args:
        callback_query: Объект CallbackQuery.
        categories: Список категорий для фильтрации кнопок (если нужно создать клавиатуру на основе категорий).
        row_width: Ширина ряда кнопок (если нужно создать клавиатуру).
    """
    callback_data = callback_query.data
    buttons_config = load_buttons_config(BUTTONS_CONFIG_PATH)

    for button in buttons_config:
        if button["callback"] == callback_data:
            await callback_query.answer()

            try:
                # If categories are provided, create a keyboard from categories
                if categories:
                    new_keyboard = create_keyboard_from_file(
                        buttons_config, categories, row_width
                    )
                    await callback_query.message.answer(
                        "Выберите опцию:", reply_markup=new_keyboard
                    )
                # Otherwise, send the default answer as text (if present)
                elif "answer" in button:
                    await callback_query.message.answer(button["answer"])
                else:
                    await callback_query.message.answer(
                        "Действие не определено для этой кнопки."
                    )
            except Exception as e:
                logger.exception(f"Ошибка при обработке callback: {e}")
                await callback_query.message.answer(
                    "Произошла ошибка при обработке запроса."
                )
            return

    await callback_query.answer("Неизвестные callback данные.")


def register_callback_handler(dp: Dispatcher):
    """Регистрирует обработчик callback-запросов."""
    # dp.register_callback_query_handler(handle_callback)

    dp.register_callback_query_handler(handle_callback, state="*")


# Example of using handle_callback in main.py (or wherever you register handlers)
# You would also register a message handler and use this callback handler
# to execute a given response. For instance, here are some examples:

# Inside main.py:
# from aiogram import types
# from aiogram.dispatcher import Dispatcher
# import callback_handlers
# def register_all_handlers(dp: Dispatcher):
#     """Register all handlers."""
#     callback_handlers.register_callback_handler(dp)
#     #Example
#     dp.register_callback_query_handler(lambda c: callback_handlers.handle_callback(c, categories=["general", "settings"], row_width=3), text="settings_button")


# from aiogram import types
# from aiogram.dispatcher import Dispatcher
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
# from keyboards import all_keyboards
# import logging

# # Настройка логирования
# # Настройка логирования в файл
# logging.basicConfig(
#     level=logging.INFO,  # Уровень логирования
#     filename="bot.log",  # Имя файла для записи логов
#     filemode="w",  # Режим записи (w - перезапись, a - добавление)
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Формат записи
# )
# logger = logging.getLogger(__name__)


# async def send_message_with_categories(
#     message: types.Message, categories: list[str], row_width: int
# ):
#     """
#     Отправляет сообщение с клавиатурой, созданной на основе категорий из файла конфигурации.

#     Args:
#         message: Объект Message.
#         categories: Список категорий для фильтрации кнопок.
#         row_width: Ширина ряда кнопок.
#     """
#     try:
#         buttons_config = all_keyboards.load_buttons_config(
#             "./keyboards/buttons_config.json"
#         )
#         keyboard = all_keyboards.create_keyboard_from_file(
#             buttons_config, categories, row_width
#         )

#         await message.reply(
#             "Welcome! I'm your EchoBot.\nHow can I assist you?",
#             reply_markup=keyboard,
#         )
#     except Exception as e:
#         logger.exception(f"Ошибка при отправке клавиатуры по категориям: {e}")
#         await message.reply("Произошла ошибка при создании клавиатуры.")


# async def send_file_content(
#     message: types.Message,
#     filename: str,
#     parse_mode: str = "MarkdownV2",
#     syntax_highlighting: str = "",
# ):
#     """
#     Отправляет содержимое указанного файла в чат с возможностью подсветки синтаксиса.

#     Args:
#         message: Объект Message.
#         filename: Имя файла, который нужно отправить.
#         parse_mode: Режим разбора текста (MarkdownV2, HTML или None). По умолчанию "MarkdownV2".
#         syntax_highlighting: Языковой идентификатор для подсветки синтаксиса (например, "python", "java").
#                              Оставьте пустым, если подсветка не требуется.
#     """
#     try:
#         with open(filename, "r", encoding="utf-8") as file:
#             content = file.read()
#         code_block = (
#             f"```{syntax_highlighting}\n{content}\n```"
#             if syntax_highlighting
#             else f"```\n{content}\n```"
#         )
#         await message.answer(code_block, parse_mode=parse_mode)
#     except FileNotFoundError:
#         await message.answer(f"Файл {filename} не найден.")
#         logger.warning(f"Файл {filename} не найден.")
#     except Exception as e:
#         logger.exception(f"Ошибка при чтении файла {filename}: {e}")
#         await message.answer(f"Произошла ошибка при чтении файла {filename}.")


# def register_common_commands_handler(dp: Dispatcher):
#     dp.register_message_handler(
#         lambda message: send_message_with_categories(
#             message, ["general", "settings"], 2
#         ),
#         commands=["start"],
#     )
#     dp.register_message_handler(
#         lambda message: send_file_content(
#             message, "AltCode.txt"
#         ),  # Добавлена подсветка синтаксиса Python
#         commands=["AltCode"],
#     )
