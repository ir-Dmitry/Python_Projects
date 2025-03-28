from aiogram import types
from aiogram.dispatcher import Dispatcher


async def echo(message: types.Message):
    await message.answer(message.text + ' loфывl')


def register_common_handler(dp: Dispatcher):
    dp.register_message_handler(echo) 
