# handlers/common_button.py
import os
import logging
import importlib.util
from typing import Union
from aiogram import types
from config_loader import ConfigLoader
from aiogram.dispatcher import Dispatcher
from .registration import cmd_reg, process_simple_reg
from keyboards import create_keyboard_from_file

logger = logging.getLogger(__name__)

# --- Инициализация ConfigLoader ---
config_loader = ConfigLoader()


async def execute_script(
    script_path: str, output_type: str = "text"
) -> Union[str, types.InputFile]:
    """
    Выполняет скрипт, импортируя его как модуль, и возвращает результат.
    """
    try:
        module_name = os.path.splitext(os.path.basename(script_path))[
            0
        ]  # Get module name
        spec = importlib.util.spec_from_file_location(
            module_name, script_path
        )  # Load the module

        if spec is None:
            logger.error(f"Could not load module from {script_path}")
            return "Не удалось загрузить модуль."

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Call the main() function from the loaded module
        try:
            result = module.main()
        except AttributeError:
            logger.error(f"No 'main' function found in script: {script_path}")
            return "В скрипте не найдена функция 'main'."

        if output_type == "text":
            if isinstance(result, str):
                logger.info(f"Output (text): {result}")
                return result
            else:
                logger.warning(
                    f"Expected string output, but got {type(result)}.  Returning string representation: {str(result)}."
                )
                return str(result)  # Convert to string if needed

        elif output_type == "file":
            if isinstance(result, str):  # Assume result is a file path
                file_path = result.strip()
                if not os.path.exists(file_path):
                    logger.error(f"File not found: {file_path}")
                    return "Файл не найден после выполнения скрипта."

                try:
                    # return types.InputFile(file_path)
                    return file_path
                except Exception as e:
                    logger.exception(f"Error sending file: {e}")
                    return f"Ошибка при отправке файла: {e}"
            else:
                logger.error(
                    f"Expected file path string, but got {type(result)} for file output."
                )
                return "Ожидался путь к файлу, но получен другой тип данных."
        else:
            logger.warning(f"Unknown output type: {output_type}")
            return "Неизвестный тип вывода."

    except FileNotFoundError:
        logger.error(f"Script '{script_path}' not found.")
        return "Скрипт не найден."
    except Exception as e:
        logger.exception(f"Error executing script '{script_path}': {e}")
        return f"Произошла ошибка при выполнении скрипта: {e}"


async def send_keyboard(message: types.Message, description: str, category: str):
    """Отправляет клавиатуру с описанием."""
    try:
        buttons_config = config_loader.load_buttons_config()
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
    buttons_config = config_loader.load_buttons_config()

    for button in buttons_config:
        if button["callback"] == callback_data:
            await callback_query.answer()

            try:

                if button.get("response_type") == "keyboard":
                    categories = button["categories"]
                # If categories are provided, create a keyboard from categories
                if categories:
                    new_keyboard = create_keyboard_from_file(
                        buttons_config, categories, row_width
                    )
                    await callback_query.message.answer(
                        "Выберите опцию:", reply_markup=new_keyboard
                    )

                elif button.get("response_type") == "reg":
                    # await cmd_reg(callback_query.message)
                    await process_simple_reg(callback_query)

                elif button.get("response_type") == "script":
                    script_path = button["path"]
                    output_type = button.get("output", "text")  # Default to "text"
                    script_result = await execute_script(script_path, output_type)

                    if isinstance(script_result, str) and output_type == "text":
                        await callback_query.message.answer(script_result)  # Send text
                    elif isinstance(script_result, str) and output_type == "file":
                        # await callback_query.message.answer_document(
                        #     document=script_result
                        # )  # Send document
                        logging.info(script_result)
                        try:
                            document = types.InputFile(script_result)
                            await callback_query.message.answer_document(
                                document=document
                            )  # Send document
                            os.remove(script_result)  # Delete the file

                        except Exception as e:
                            logger.exception(f"Error sending/deleting file: {e}")
                            await callback_query.message.answer(
                                f"Произошла ошибка при отправке или удалении файла: {e}"
                            )
                    else:
                        logging.info("Чет не то")

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
