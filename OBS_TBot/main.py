import logging
from aiogram import executor
from create_bot import dp
from handlers import (
    # register_callback_handlers,
    register_callback_handler,
    register_common_handler,
)


logging.basicConfig(level=logging.INFO)
# Регистрируем обработчик
# register_callback_handlers(dp)
register_callback_handler(dp)
register_common_handler(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
