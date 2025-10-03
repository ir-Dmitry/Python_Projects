import asyncio
from datetime import datetime
from aiogram import Bot
from ..scheduler import TaskScheduler
from .time_utils import calculate_reminder_time
from .users import update_user_block_status, send_reminder_to_users
from ..file_reader import load_json, get_webinar_time, get_timezone

scheduler = TaskScheduler()


async def schedule_webinar_reminder(bot: Bot):
    webinar_time = get_webinar_time()
    reminders = load_json("data/reminders.json", [])

    if not reminders:
        print("📭 Нет напоминаний для планирования.")
        return

    now = datetime.now(get_timezone())

    for reminder in reminders:
        delay = (
            calculate_reminder_time(webinar_time, reminder["time"]) - now
        ).total_seconds()

        if delay <= 0:
            print(f"⏭ Пропущено: '{reminder['label']}' (устарело)")
            continue

        print(f"⏳ Напоминание '{reminder['label']}' через {delay:.0f} сек")
        await asyncio.sleep(delay)

        await update_user_block_status(bot)
        sent = await send_reminder_to_users(
            bot, reminder["text"], bool(reminder.get("last"))
        )

        print(f"📬 '{reminder['label']}' отправлено {sent} пользователям.")
        now = datetime.now(get_timezone())


async def schedule_periodic_task(bot: Bot, interval: int = 10):
    while True:
        print(f"⏰ Периодическая задача {datetime.now()}")
        await update_user_block_status(bot)
        await asyncio.sleep(interval)


async def start_reminders(bot: Bot):
    scheduler.add_task("webinar_reminder", schedule_webinar_reminder, bot)
    scheduler.add_task("periodic_task", schedule_periodic_task, bot, 86400)


async def stop_reminders():
    await scheduler.stop_all()


async def on_startup_reg(dp):
    bot = dp.bot
    print("Бот запущен. Запускаем напоминания...")
    await start_reminders(bot)
