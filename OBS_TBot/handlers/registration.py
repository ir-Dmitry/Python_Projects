import requests
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.types import ParseMode
from aiogram.utils import executor
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # работает только с Python 3.9+
import os
from dotenv import load_dotenv
import logging
import json
from typing import List
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
# Путь к твоему JSON-файлу
CREDENTIALS_FILE = "credentials.json"

# Области доступа (не меняй)
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

moscow_time = datetime.now(ZoneInfo("Europe/Moscow"))
print(f"Московское время: {moscow_time}")

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyDvcZmwUWDY3CzrPCMJvCPfTprH4g9iIVOnKKSvhHGUVfbbiEMSTZEIfLjENT68aLxMQ/exec"

TOKEN = BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBINAR_DATETIME = os.getenv("WEBINAR_DATETIME")
TIMEZONE = os.getenv("TIMEZONE")

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

# ///////////////////////////Обработчик регистрации///////////////////////////
import json
import re
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# Включаем хранилище состояний (в памяти)
storage = MemoryStorage()


# ——— FSM: состояния ———
class Registration(StatesGroup):
    waiting_for_full_name = State()  # Состояние: ждём ФИО
    waiting_for_email = State()  # Состояние: ждём email


async def cmd_reg(message: types.Message):
    await message.answer("📝 Начинаем регистрацию!\n\nВведите ваше ФИО:")
    await Registration.waiting_for_full_name.set()  # Устанавливаем состояние


async def process_full_name(message: types.Message, state: FSMContext):
    full_name = message.text.strip()

    # Проверка длины
    if len(full_name) < 2 or len(full_name) > 100:
        await message.answer("❌ ФИО должно быть не менее 2 символов и не больше 100.")
        return

    # Разрешаем только: буквы (рус/англ), пробел, дефис, апостроф
    if not re.fullmatch(r"[a-zA-Zа-яА-ЯёЁ\s\-']+", full_name):
        await message.answer(
            "❌ ФИО может содержать только:\n"
            "• Буквы (русские и английские)\n"
            "• Пробел\n"
            "• Дефис (-)\n"
            "• Апостроф (')"
        )
        return

    # ✅ Всё ок — сохраняем
    await state.update_data(full_name=full_name)
    await message.answer("📧 Теперь введите ваш email:")
    await Registration.waiting_for_email.set()


def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()

    if not is_valid_email(email):
        await message.answer("❌ Неверный формат email.\nПопробуйте ещё раз:")
        return

    # Сохраняем email
    await state.update_data(email=email)

    # Получаем все данные
    data = await state.get_data()
    full_name = data["full_name"]
    user_id = message.from_user.id

    # 💾 Здесь сохраняй в JSON, БД и т.п.
    success = save_registration(user_id, full_name, email)

    await message.answer(success, parse_mode="HTML")

    # 🧹 Выходим из состояния
    await state.finish()


def send_to_google_sheets(pers: dict):
    """
    Отправляет данные в Google Таблицу через Google Apps Script.
    """
    data = pers

    # Авторизация
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE, scope
    )
    client = gspread.authorize(credentials)

    # Открываем таблицу по названию
    spreadsheet = client.open("Регистрация на вебинар")  # ← замени на реальное имя

    # Выбираем лист (например, "Лист1")
    worksheet = spreadsheet.sheet1  # или: spreadsheet.worksheet("Лист1")

    # Прочитать все строки
    # data = worksheet.get_all_records()
    # print(data)

    worksheet.append_row([*data.values()])


def save_registration(user_id: int, full_name: str, email: str):
    """
    Сохраняет пользователя и возвращает HTML-сообщение для отправки пользователю.
    """
    try:
        with open("users.json", "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                users = []  # пустой файл → считаем, что []
            else:
                users = json.loads(content)  # парсим JSON
    except FileNotFoundError:
        users = []
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        return (
            "❌ Произошла ошибка при сохранении данных.\n"
            "Пожалуйста, попробуйте позже."
        )

    # Проверка на дубликат
    if any(user["user_id"] == user_id for user in users):
        return (
            "⚠️ <b>Вы уже зарегистрированы</b> на вебинар.\n\n"
            "Не волнуйтесь — напоминание придет вовремя!"
        )

    # Добавляем нового пользователя
    pers = {
        "user_id": user_id,
        "full_name": full_name,
        "email": email,
        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    users.append(pers)

    # 🚀 Отправляем данные в Google Таблицу
    send_to_google_sheets(pers)

    try:
        tmp_time = get_webinar_time()
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return (
            "✅ <b>Регистрация завершена!</b>\n\n"
            f"📌 ФИО: {full_name}\n"
            f"✉️ Email: {email}\n\n"
            f"🗓 Дата вебинара: {tmp_time.date()}. \n🕰 Время: {tmp_time.strftime('%H:%M')}.\nНапоминание о вебинаре придет вовремя."
        )
    except Exception as e:
        print(f"Ошибка записи в файл: {e}")
        return (
            "❌ Не удалось сохранить данные.\n"
            "Пожалуйста, попробуйте ещё раз или свяжитесь с поддержкой."
        )


# ///////////////////////////Обработчик регистрации///////////////////////////


def get_webinar_time():

    dt_str = WEBINAR_DATETIME
    tz_name = TIMEZONE

    naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    aware_dt = naive_dt.replace(tzinfo=ZoneInfo(tz_name))

    return aware_dt


def load_user_ids_from_json(filename: str = "users.json") -> List[int]:
    """
    Загружает список user_id из JSON-файла.
    Возвращает пустой список, если файл не найден или ошибка.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [user["user_id"] for user in data if "user_id" in user]
    except FileNotFoundError:
        print(f"⚠️ Файл {filename} не найден.")
        return []
    except Exception as e:
        print(f"❌ Ошибка при чтении {filename}: {e}")
        return []


async def schedule_webinar_reminder(bot: Bot):
    """
    Запускает три напоминания до вебинара:
    - за 2 дня
    - за 2 часа
    - за 10 минут
    """
    webinar_time = get_webinar_time()
    now = datetime.now(ZoneInfo(TIMEZONE))

    # Определяем временные точки напоминаний days/hours/minutes
    reminders = [
        {
            "time": webinar_time - timedelta(days=2),
            "text": (
                "📅 <b>Напоминание: вебинар через 2 дня!</b>\n\n"
                "Подготовьте вопросы, зарядитесь энергией!\n"
            ),
            "label": "за 2 дня",
        },
        {
            "time": webinar_time - timedelta(hours=2),
            "text": (
                "⏰ <b>Внимание: вебинар начнётся через 2 часа!</b>\n\n"
                "Не пропустите — уже скоро!\n"
            ),
            "label": "за 2 часа",
        },
        {
            "time": webinar_time - timedelta(minutes=10),
            "text": (
                "🔥 <b>Вебинар скоро начнется!</b>\n\n"
                "Уже через 10 минут мы стартуем!\n"
            ),
            "label": "за 10 минут",
        },
        {
            "time": webinar_time - timedelta(seconds=10),
            "text": (
                "🔥 <b>Вебинар начинается СЕЙЧАС!</b>\n\n"
                "👉 Присоединяйтесь: https://example.com/webinar"
            ),
            "label": "за 10 минут",
        },
    ]

    # Фильтруем только будущие напоминания
    future_reminders = [r for r in reminders if r["time"] > now]

    if not future_reminders:
        print("⚠️ Все напоминания уже в прошлом.")
        # await bot.send_message(
        #     chat_id=1127371080,
        #     text="⚠️ Все напоминания уже в прошлом.",
        #     parse_mode="HTML",
        # )
        return

    for reminder in future_reminders:
        send_time = reminder["time"]
        delay = (send_time - now).total_seconds()

        msg = f"⏳ Напоминание {reminder['label']} запланировано на {send_time} (через {delay:.0f} сек)"

        print(msg)
        # await bot.send_message(
        #     chat_id=1127371080,
        #     text=msg,
        #     parse_mode="HTML",
        # )
        await asyncio.sleep(delay)

        user_ids = load_user_ids_from_json()
        if not user_ids:
            print("📭 Нет зарегистрированных пользователей.")
            continue

        msg = f"📨 Рассылка {reminder['label']} для {len(user_ids)} пользователей..."
        # await bot.send_message(
        #     chat_id=1127371080,
        #     text=msg,
        #     parse_mode="HTML",
        # )
        print(msg)
        for user_id in user_ids:
            try:
                await bot.send_message(
                    chat_id=user_id, text=reminder["text"], parse_mode="HTML"
                )
                print(f"✅ Отправлено: {user_id}")
            except Exception as e:
                print(f"❌ Ошибка для {user_id}: {e}")
            await asyncio.sleep(0.05)  # анти-спам

        # Обновляем текущее время после сна
        now = datetime.now(ZoneInfo(TIMEZONE))


async def on_startup_reg(dp):  # ← параметр — dp (диспетчер)
    bot = dp.bot  # ← получаем бота из диспетчера
    print("Бот запущен. Запускаем напоминание...")
    asyncio.create_task(schedule_webinar_reminder(bot))


if __name__ == "__main__":

    # Запускаем бота и передаём on_startup
    executor.start_polling(
        dp,  # диспетчер
        on_startup=on_startup_reg,  # функция, которая запустится при старте
        skip_updates=True,  # пропустить старые обновления
    )
