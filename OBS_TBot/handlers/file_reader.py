# handlers/file_reader.py
import os
import json
from pathlib import Path
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


def init_json(file_path="data/default.json", default=None):
    """
    Создаёт JSON-файл, если его нет, и записывает значение по умолчанию.
    :param file_path: путь к файлу JSON
    :param default: значение, которое будет записано, если файл не существует
    :return: путь к файлу как Path
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)  # создаём папку, если её нет

    if not path.exists():
        if default is None:
            default = ""  # по умолчанию пустой список
        with open(path, "w", encoding="utf-8") as f:
            f.write(default)
    return path


def load_json(file_path="data/default.json", default=None):
    """
    Загружает данные из JSON файла.
    :param file_path: Путь к JSON файлу.
    :param default: Что вернуть, если файл пустой или не существует.
    :return: Данные (dict | list | примитив) или default.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                return default
            return json.loads(content)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        print(f"Ошибка: файл '{file_path}' имеет неверный формат JSON.")
        return default
    except Exception as e:
        print(f"Произошла ошибка при загрузке файла: {e}")
        return default


def save_json(filename, data, default=None):
    """
    Сохраняет данные в JSON файл.
    :param filename: Куда сохранить.
    :param data: Что сохранять (если None → default).
    :param default: Что подставить, если data = None.
    """
    try:
        if data is None:
            data = default
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ Данные сохранены в {filename}")
    except Exception as e:
        print(f"❌ Ошибка записи {filename}: {e}")
