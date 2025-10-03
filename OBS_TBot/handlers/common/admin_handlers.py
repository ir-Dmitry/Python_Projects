import json
from aiogram import types
from ..file_reader import load_json

from ..logger import get_logger
from ..common.users import (
    is_admin,
    add_admin,
    remove_admin,
    load_all_users,
)

logger = get_logger("common", "common.log")


async def add_admin_by_nickname(message: types.Message):
    if not await admin_only(message):
        return
    try:
        # Разбираем никнейм из команды
        nickname = message.text.split()[1]  # @username
        print(f"Команда получена: /add_admin с никнеймом @{nickname}")

        # Убираем @, если оно есть
        if nickname.startswith("@"):
            nickname = nickname[1:]
        print(f"Никнейм после удаления @: {nickname}")

        # Ищем пользователя по никнейму в базе всех пользователей
        users = load_all_users()
        print(f"Загружено {len(users)} пользователей из базы.")
        user_info = next((user for user in users if user["username"] == nickname), None)

        if user_info:
            user_id = user_info["id"]
            print(f"Пользователь @{nickname} найден с ID: {user_id}")
            # Добавляем его как администратора
            added = add_admin(user_id)
            if added:
                print(f"Пользователь @{nickname} добавлен в админы.")
                await message.answer(f"✅ Админ @{nickname} добавлен.")
            else:
                print(f"Пользователь @{nickname} уже является администратором.")
                await message.answer(
                    f"⚠️ Этот пользователь уже является администратором."
                )
        else:
            print(f"Пользователь @{nickname} не найден в базе всех пользователей.")
            await message.answer(
                f"❌ Не удалось найти пользователя с никнеймом @{nickname}."
            )

    except IndexError:
        print("Ошибка: Никнейм не был указан в команде.")
        await message.answer(
            "⚠️ Пожалуйста, укажите никнейм пользователя, например: /add_admin @username"
        )
    except Exception as e:
        print(f"Ошибка при добавлении админа: {str(e)}")
        await message.answer(
            f"❌ Ошибка при добавлении админа: {str(e)}"
        )  # handlers/common.py


async def remove_admin_by_nickname(message: types.Message):
    if not await admin_only(message):
        return  # Если пользователь не админ, прерываем выполнение

    try:
        # Разбираем никнейм из команды
        nickname = message.text.split()[1]  # @username
        print(f"Команда получена: /remove_admin с никнеймом @{nickname}")

        # Убираем @, если оно есть
        if nickname.startswith("@"):
            nickname = nickname[1:]
        print(f"Никнейм после удаления @: {nickname}")

        # Ищем пользователя по никнейму в базе всех пользователей
        users = load_all_users()
        print(f"Загружено {len(users)} пользователей из базы.")
        user_info = next((user for user in users if user["username"] == nickname), None)

        if user_info:
            user_id = user_info["id"]
            print(f"Пользователь @{nickname} найден с ID: {user_id}")

            # Удаляем права администратора
            removed = remove_admin(user_id)
            if removed:
                await message.answer(f"✅ Администратор @{nickname} удален.")
            else:
                await message.answer(
                    f"❌ Пользователь @{nickname} не был администратором."
                )
        else:
            await message.answer(
                f"❌ Не удалось найти пользователя с никнеймом @{nickname}."
            )

    except IndexError:
        await message.answer(
            "❗ Пожалуйста, укажите никнейм пользователя, например: /remove_admin @username"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при удалении админа: {str(e)}")


async def remove_all_registrations(message: types.Message):
    """Обработчик команды /remove_all_registrations для очистки списка зарегистрированных пользователей."""

    if not await admin_only(message):
        return
    try:
        # Загружаем текущих пользователей
        users = load_json("data/users.json", [])

        if not users:
            await message.reply("📭 Список пользователей уже пуст.")
            return

        # Очищаем список пользователей
        users.clear()

        # Сохраняем изменения в файл
        with open("data/users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

        # Подтверждаем успешное выполнение
        await message.reply(
            "✅ Список зарегистрированных пользователей успешно очищен."
        )

    except Exception as e:
        logger.exception(f"Ошибка в обработчике команды /remove_all_registrations: {e}")
        await message.reply(f"❌ Произошла ошибка при очистке списка: {e}")


# Обработчик для команд, доступных только админам
async def admin_only(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("❌ Эта команда доступна только администраторам.")
        return False
    return True
