from aiogram import types
from aiogram.dispatcher import Dispatcher
from keyboards import all_keyboards

buttons_config = all_keyboards.load_buttons_config("./keyboards/buttons_config.json")


async def handle_callback(callback_query: types.CallbackQuery):
    """
    Обработчик callback-запросов от inline-кнопок.

    Эта функция принимает объект `CallbackQuery`, извлекает данные callback,
    ищет соответствующую конфигурацию в файле `buttons_config.json` и отправляет ответ пользователю.

    Args:
        callback_query: Объект `CallbackQuery`, содержащий информацию о callback-запросе.
    """
    callback_data = callback_query.data
    for button in buttons_config:
        if button["callback"] == callback_data:
            await callback_query.answer()
            await callback_query.message.answer(button["answer"])
            return
    await callback_query.answer("Unknown callback data.")


def register_callback_handlers(dp: Dispatcher):
    """
    Регистрирует обработчик callback-запросов в диспетчере.

    Эта функция регистрирует функцию `handle_callback` как обработчик всех callback-запросов.

    Args:
        dp: Объект `Dispatcher`, используемый для регистрации обработчиков.
    """
    dp.register_callback_query_handler(handle_callback)
