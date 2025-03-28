from aiogram import types
from aiogram.dispatcher import Dispatcher
from keyboards import all_keyboards

buttons_config = all_keyboards.load_buttons_config("./keyboards/buttons_config.json") 

async def handle_callback(callback_query: types.CallbackQuery):
    callback_data = callback_query.data
    for button in buttons_config:
        if button["callback"] == callback_data:
            await callback_query.answer()
            await callback_query.message.answer(button["answer"])
            return
    await callback_query.answer("Unknown callback data.")

def register_callback_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(handle_callback)



# async def process_help_button(callback_query: types.CallbackQuery):
#     await callback_query.answer()  # Чтобы Telegram знал, что запрос обработан
#     await callback_query.message.answer("Sorry, I can’t help you with that yet. But you can ask /AltCode")

# async def process_agro_button(callback_query: types.CallbackQuery):
#     await callback_query.answer()  # Чтобы Telegram знал, что запрос обработан
#     await callback_query.message.answer("Shut up you fucking slave. Motherfucker.")


# def register_callback_handlers(dp: Dispatcher):
#     dp.register_callback_query_handler(process_help_button, lambda c: c.data == 'help')
#     dp.register_callback_query_handler(process_agro_button, lambda c: c.data == 'you fucking slave')
