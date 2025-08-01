import logging
from aiogram import executor
from create_bot import dp
from handlers import register_all_handlers, on_startup


logging.basicConfig(level=logging.INFO)
register_all_handlers(dp)

# Запускаем polling — он будет работать с update_id > последнего
if __name__ == "__main__":
    executor.start_polling(
        dp,
        on_startup=on_startup,
        skip_updates=False,  # False — чтобы мы могли обработать вручную
    )
