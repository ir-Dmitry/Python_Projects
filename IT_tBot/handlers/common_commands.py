from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards import all_keyboards
    
async def send_welcome(message: types.Message, *keyboards: InlineKeyboardMarkup):
    # combined_keyboard = InlineKeyboardMarkup()   
    help_keyboard = all_keyboards.create_keyboard(
        [
            ("Help", "help"), 
            ("Help me please", "you_fucking_slave")
        ])

    buttons_config = all_keyboards.load_buttons_config("./keyboards/buttons_config.json")

    # Выбираем кнопки для нескольких категорий
    selected_keyboard = all_keyboards.create_keyboard_from_file(buttons_config, ["general", "settings"], 3)

    await message.reply("Welcome! I'm your EchoBot.\nHow can I assist you?", reply_markup=selected_keyboard)
    # await message.reply("Welcome! I'm your EchoBot.\nHow can I assist you?", reply_markup=help_keyboard)


    # await message.reply("Welcome! I'm your EchoBot.\nHow can I assist you?", reply_markup=get_help_keyboard()+get_agro_keyboard())
    # await message.reply("Welcome! I'm your EchoBot.")


async def alt_code_handler(message: types.Message):
    try:
        with open('AltCode.txt', 'r', encoding='utf-8') as file:
            content = file.read()
        await message.answer(f"```\n{content}\n```", parse_mode="MarkdownV2")
    except FileNotFoundError:
        await message.answer("Файл AltCode.txt не найден.")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")



# def register_common_commands_handler(dp: Dispatcher):
#     dp.register_message_handler(
#         lambda message: send_welcome(message, 
#                                     get_help_keyboard(), get_agro_keyboard()
#                                     ),
#             commands=['start']
#     )
#     dp.register_message_handler(alt_code_handler, commands=['AltCode'])



def register_common_commands_handler(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_message_handler(alt_code_handler, commands=['AltCode'])
