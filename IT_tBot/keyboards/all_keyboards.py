import json
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def load_buttons_config(path: str) -> list[dict]:
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)["buttons"]


def create_keyboard(buttons: list[tuple[str, str]], row_width: int = 1) -> InlineKeyboardMarkup:
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


def create_keyboard_from_file(buttons: list[dict], categories: list[str], row_width: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=row_width)
    for button in buttons:
        if button.get("category") in categories:
            keyboard.add(InlineKeyboardButton(button["text"], callback_data=button["callback"]))
    return keyboard

# def get_help_keyboard():
#     keyboard = InlineKeyboardMarkup(row_width=1)
#     keyboard.add(InlineKeyboardButton("Help", callback_data="help"))
#     return keyboard

# def get_agro_keyboard():
#     keyboard = InlineKeyboardMarkup(row_width=1)
#     keyboard.add(InlineKeyboardButton("Help me please", callback_data="you fucking slave"))
#     return keyboard

