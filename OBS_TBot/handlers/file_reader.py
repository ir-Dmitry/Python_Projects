# handlers/file_reader.py
import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo  # работает только с Python 3.9+
from dotenv import load_dotenv


def get_timezone() -> ZoneInfo:
    """
    Возвращает объект временной зоны из переменной окружения TIMEZONE.
    """
    load_dotenv()  # загружаем .env при каждом вызове
    tz_name = os.getenv("TIMEZONE")
    if not tz_name:
        print(ValueError("TIMEZONE не указана в .env"))
        return "Europe/Moscow"
    return ZoneInfo(tz_name)


def get_webinar_link():
    """
    Возвращает объект временной зоны из переменной окружения WEBINAR_LINK.
    """
    load_dotenv()  # загружаем .env при каждом вызове
    link_name = os.getenv("WEBINAR_LINK")
    if not link_name:
        print(ValueError("WEBINAR_LINK не указана в .env"))
        return "https://example.com"
    return link_name


def get_webinar_time() -> datetime:
    """
    Возвращает объект datetime с учётом временной зоны, считанный из переменной окружения WEBINAR_DATETIME.
    """
    load_dotenv()  # загружаем .env при каждом вызове
    dt_str = os.getenv("WEBINAR_DATETIME")
    if not dt_str:
        print(ValueError("WEBINAR_DATETIME не указана в .env"))
        return "2025-08-08 11:28:00"

    try:
        naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        tz = get_timezone()
        return naive_dt.replace(tzinfo=tz)
    except ValueError as e:
        raise ValueError(f"Ошибка разбора даты из .env: {e}")


def load_jsons(file_path="data/default.json"):
    """
    Загружает данные из JSON файла.
    :param file_path: Путь к JSON файлу.
    :return: Данные в виде словаря или списка.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                data = []  # пустой файл → считаем, что []
            else:
                data = json.loads(content)  # парсим JSON

        return data
    except FileNotFoundError:
        print(f"Ошибка: файл '{file_path}' не найден.")
        return None
    except json.JSONDecodeError:
        print(f"Ошибка: файл '{file_path}' имеет неверный формат JSON.")
        return None
    except Exception as e:
        print(f"Произошла ошибка при загрузке файла: {e}")
        return None
