# handlers/registration.py
import re
import json
from aiogram import types
from datetime import datetime
from zoneinfo import ZoneInfo  # работает только с Python 3.9+
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from .google_sheets import send_to_google_sheets
from .file_reader import load_jsons, get_webinar_time

moscow_time = datetime.now(ZoneInfo("Europe/Moscow"))
print(f"Московское время: {moscow_time}")

# Включаем хранилище состояний (в памяти)
storage = MemoryStorage()

# где-то глобально

# Регулярные выражения
NAME_PATTERN = r"[a-zA-Zа-яА-ЯёЁ\s\-']+"
EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


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
    if not re.fullmatch(NAME_PATTERN, full_name):
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
    pattern = EMAIL_PATTERN
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
    users = load_jsons("data/users.json")

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
        with open("data/users.json", "w", encoding="utf-8") as f:
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
