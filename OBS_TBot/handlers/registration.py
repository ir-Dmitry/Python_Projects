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

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

moscow_time = datetime.now(ZoneInfo("Europe/Moscow"))
print(f"Московское время: {moscow_time}")


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
    users.append(
        {
            "user_id": user_id,
            "full_name": full_name,
            "email": email,
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )

    try:
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return (
            "✅ <b>Регистрация завершена!</b>\n\n"
            f"📌 ФИО: {full_name}\n"
            f"✉️ Email: {email}\n\n"
            "🔔 Напоминание о вебинаре придет вовремя."
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
    Ждёт до времени вебинара и рассылает напоминание ВСЕМ зарегистрированным.
    user_id берётся из users.json.
    """
    webinar_time = get_webinar_time()

    first_message = webinar_time - timedelta(minutes=1440)
    second_message = webinar_time - timedelta(minutes=120)
    last_message = webinar_time - timedelta(minutes=10)

    now = datetime.now(ZoneInfo(TIMEZONE))

    if webinar_time <= now:
        print("⚠️ Вебинар уже прошёл. Напоминание не требуется.")
        return

    delay = (webinar_time - now).total_seconds()
    print(f"⏳ Напоминание запланировано через {delay:.0f} секунд ({webinar_time})")

    # Ждём
    await asyncio.sleep(delay)

    # После задержки — читаем user_id из файла
    user_ids = load_user_ids_from_json()

    if not user_ids:
        print("📭 Нет зарегистрированных пользователей для рассылки.")
        return

    print(f"📨 Начинаем рассылку напоминания {len(user_ids)} пользователям...")

    # Рассылка
    for user_id in user_ids:
        try:
            await bot.send_message(
                chat_id=user_id,
                text="🔔 Вебинар начинается СЕЙЧАС! АЭАЭАЭА! Быстро блять!!!\n\n"
                "👉 Присоединяйтесь: https://example.com/webinar",
                parse_mode="HTML",
            )
            print(f"✅ Напоминание отправлено: {user_id}")
        except Exception as e:
            print(f"❌ Не удалось отправить {user_id}: {e}")
        await asyncio.sleep(0.05)  # анти-спам задержка


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
