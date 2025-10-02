import asyncio
from aiogram import Bot
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, UserDeactivated
from ..google_sheets import send_data_to_google_sheets
from ..file_reader import save_jsons, load_jsons, get_webinar_link


async def update_user_block_status(bot: Bot):
    users = load_jsons("data/users.json")
    if not users:
        print("📭 Нет пользователей для обновления статуса.")
        return

    updated_count = 0
    for user in users:
        user_id = user.get("user_id")
        if not user_id:
            continue

        try:
            await bot.send_chat_action(user_id, "choose_sticker")
            user["available"] = True
            print(f"✅ Доступен: {user_id}")
        except (BotBlocked, ChatNotFound, UserDeactivated) as e:
            user["available"] = False
            print(f"❌ Не доступен: {user_id} | {e}")
        except Exception as e:
            print(f"⚠️ Ошибка {user_id}: {type(e).__name__}: {e}")
            continue

        updated_count += 1
        await asyncio.sleep(0.05)

    try:
        send_data_to_google_sheets(users)
    except Exception as e:
        print(f"⚠️ Ошибка отправки в Google Sheets: {e}")

    save_jsons("data/users.json", users)
    print(f"📊 Статус обновлён для {updated_count} пользователей.")


async def send_reminder_to_users(bot: Bot, text: str, include_link: bool = False):
    users = load_jsons("data/users.json")
    if not users:
        print("📭 Нет пользователей для рассылки.")
        return 0

    sent_count = 0
    full_text = text + (get_webinar_link() if include_link else "")

    for user in users:
        user_id = user.get("user_id")
        if not user_id or not user.get("available", False):
            continue

        try:
            await bot.send_message(user_id, full_text, parse_mode="HTML")
            print(f"✅ Отправлено: {user_id}")
            sent_count += 1
        except Exception as e:
            print(f"❌ Ошибка отправки {user_id}: {e}")
        await asyncio.sleep(0.05)

    return sent_count
