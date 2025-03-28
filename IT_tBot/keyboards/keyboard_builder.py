import json
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_keyboard(
    buttons: list[tuple[str, str]], row_width: int = 2
) -> InlineKeyboardMarkup:
    """
    Создаёт универсальную клавиатуру.

    :param buttons: Список кнопок в формате [(текст, callback_data), ...].
    :param row_width: Количество кнопок в одной строке.
    :return: Объект InlineKeyboardMarkup.
    """
    keyboard = InlineKeyboardMarkup(row_width=row_width)
    for text, callback_data in buttons:
        keyboard.add(InlineKeyboardButton(text, callback_data=callback_data))
    return keyboard


def create_keyboard_from_file(
    buttons: list[dict], categories: list[str], row_width: int
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=row_width)
    for button in buttons:
        if button.get("category") in categories:
            keyboard.add(
                InlineKeyboardButton(button["text"], callback_data=button["callback"])
            )
    return keyboard
