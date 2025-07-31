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

load_dotenv()
moscow_time = datetime.now(ZoneInfo("Europe/Moscow"))
print(f"Московское время: {moscow_time}")


TOKEN = BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

# bot = Bot(
#     token=TOKEN,
#     default=DefaultBotProperties(parse_mode=ParseMode.HTML)
# )


# dp = Dispatcher()


@dp.message_handler()
async def reminder_handler(message: types.Message):
    text = message.text.strip().lower()
    print(f"[{datetime.now()}] Получено сообщение: {text}")

    if text.startswith("через"):
        try:
            parts = text.split(" ", 2)
            minutes = int(parts[1])
            reminder_text = parts[2]

            print(
                f"[{datetime.now()}] Установлено напоминание через {minutes} минут: {reminder_text}"
            )
            await message.answer(
                f"⏰ Напоминание через {minutes} мин: <b>{reminder_text}</b>"
            )
            asyncio.create_task(
                set_reminder(message.from_user.id, minutes, reminder_text)
            )  # <--- *60 вернул
        except Exception as e:
            print(f"[{datetime.now()}] Ошибка при обработке 'через': {e}")

    else:
        try:
            parts = text.split(" ", 3)
            date_part = parts[0]
            time_part = parts[1]
            reminder_text = parts[3]

            reminder_dt = datetime.strptime(
                f"{date_part} {time_part}", "%d.%m.%Y %H:%M"
            )
            now = datetime.now()
            delay = (reminder_dt - now).total_seconds()

            if delay <= 0:
                print(f"[{datetime.now()}] Введено прошедшее время: {reminder_dt}")
                await message.answer("❗ Это время уже прошло!")
                return

            print(
                f"[{datetime.now()}] Установлено напоминание на {reminder_dt}: {reminder_text}"
            )
            await message.answer(
                f"📅 Напоминание в {reminder_dt.strftime('%d.%m.%Y %H:%M')}: <b>{reminder_text}</b>"
            )
            asyncio.create_task(
                set_reminder(message.from_user.id, delay, reminder_text)
            )
        except Exception as e:
            print(f"[{datetime.now()}] Ошибка при обработке даты: {e}")
            now_moscow = datetime.now(ZoneInfo("Europe/Moscow")) + timedelta(minutes=1)

            formatted = now_moscow.strftime("%d.%m.%Y %H:%M")
            await message.answer(
                f"⚠️ Неверный формат. \nПример: \n<code>{formatted} напомни что-то</code> \n<code>через 10 напомни сделать зарядку</code>"
            )


async def set_reminder(user_id, delay, text):
    print(f"[{datetime.now()}] Ждём {delay} секунд для чата {user_id} — {text}")
    await asyncio.sleep(delay)
    print(f"[{datetime.now()}] Напоминание сработало для чата {user_id}: {text}")
    await bot.send_message(user_id, f"🔔 Напоминаю: <b>{text}</b>")


async def start_bot():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(start_bot())
