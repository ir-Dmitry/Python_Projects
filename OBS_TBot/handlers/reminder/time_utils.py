from datetime import datetime, timedelta

TIME_MAP = {
    "days": timedelta(days=1),
    "hours": timedelta(hours=1),
    "minutes": timedelta(minutes=1),
    "seconds": timedelta(seconds=1),
}


def calculate_reminder_time(webinar_time: datetime, relative_time: str) -> datetime:
    amount, unit = relative_time.split()
    return webinar_time - TIME_MAP[unit] * int(amount)
