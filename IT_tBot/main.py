import logging
from aiogram import executor
from create_bot import dp
from handlers import register_callback_handlers, register_common_commands_handler, register_common_handler

from background import keep_alive

logging.basicConfig(level=logging.INFO)
# Регистрируем обработчик
register_callback_handlers(dp)
register_common_commands_handler(dp)
register_common_handler(dp)

keep_alive()
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
