import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = '7720548678:AAF5AricAd_ycswgR7oEwzDn2t2h8038s5U'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# import logging
# from background import keep_alive
# from aiogram import Bot, Dispatcher, executor, types
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# API_TOKEN = '7720548678:AAF5AricAd_ycswgR7oEwzDn2t2h8038s5U'

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# # Initialize bot and dispatcher
# bot = Bot(token=API_TOKEN)
# dp = Dispatcher(bot)

# @dp.message_handler(commands=['start'])
# async def send_welcome(message: types.Message):
#     keyboard = InlineKeyboardMarkup(row_width=2)
#     button_help = InlineKeyboardButton("Help", callback_data="help")
#     keyboard.add(button_help)
#     await message.reply("Welcome! I'm your EchoBot.\nHow can I assist you?", reply_markup=keyboard)

# @dp.callback_query_handler(lambda c: c.data == 'help')
# async def process_help_button(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)  # Ожидание ответа
#     await bot.send_message(callback_query.from_user.id, "Sorry, I can’t help you with that yet. But you can ask /AltCode")

# # @dp.message_handler(commands=['start', 'help'])
# # async def send_welcome(message: types.Message):
# #     """
# #     This handler will be called when user sends `/start` or `/help` command
# #     """
# #     await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")

# @dp.message_handler(commands=['AltCode'])
# async def AltCode(message: types.Message):
#     try:
#         # Открываем и читаем содержимое файла
#         with open('AltCode.txt', 'r', encoding='utf-8') as file:
#             content = file.read()

#         # Отправляем содержимое файла в ответ
#         await message.answer(f"```\n{content}\n```", parse_mode="MarkdownV2")

#     except FileNotFoundError:
#         # Если файл не найден, отправляем сообщение об ошибке
#         await message.answer("Файл AltCode.txt не найден.")
#     except Exception as e:
#         # Обработка других возможных ошибок
#         await message.answer(f"Произошла ошибка: {str(e)}")

# @dp.message_handler()
# async def echo(message: types.Message):
#     # old style:
#     # await bot.send_message(message.chat.id, message.text)

#     await message.answer(message.text+'lol')

# keep_alive()
# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True)
