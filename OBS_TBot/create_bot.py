import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage

load_dotenv()

API_TOKEN = BOT_TOKEN = os.getenv("BOT_TOKEN")
# ——— Хранилище и бот ———
storage = MemoryStorage()

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
