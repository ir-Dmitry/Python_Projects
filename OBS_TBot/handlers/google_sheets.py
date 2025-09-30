# handlers/google_sheets.py
import os
import gspread
import logging
from typing import Union
from requests.exceptions import HTTPError
from google.auth.exceptions import GoogleAuthError
from google.oauth2.service_account import Credentials

# Логи
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("logs/google_sheets.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

CREDENTIALS_FILE = "data/credentials.json"
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CLIENT = None
FIELDS_ORDER = ["user_id", "registered_at", "available"]


def authorize_google_sheets():
    global CLIENT
    if CLIENT is None:
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=scope
        )
        CLIENT = gspread.authorize(credentials)
        logger.info("Авторизация Google Sheets выполнена успешно.")


def is_google_sheets_connected():
    try:
        global CLIENT
        spreadsheet = CLIENT.open("Регистрация на вебинар")
        logger.info("Подключение к Google Sheets успешно.")
        return True
    except (HTTPError, GoogleAuthError) as e:
        logger.error(f"Ошибка подключения к Google Sheets: {e}", exc_info=True)
        CLIENT = None
        return False


def send_data_to_google_sheets(data: Union[dict, list[dict]]):
    """
    Универсальная функция для отправки данных в Google Sheets.
    Обновляет существующие строки по user_id и добавляет новые.
    Принимает словарь или список словарей.
    """
    try:
        global CLIENT
        if CLIENT is None or not is_google_sheets_connected():
            authorize_google_sheets()

        worksheet = CLIENT.open("Регистрация на вебинар").sheet1

        if isinstance(data, dict):
            data = [data]

        records = worksheet.get_all_records()
        id_to_row = {str(r.get("user_id")): i + 2 for i, r in enumerate(records)}

        new_rows = []
        for user in data:
            row_data = [user.get(f, "") for f in FIELDS_ORDER]
            uid = str(user.get("user_id"))
            if uid in id_to_row:
                worksheet.update(f"A{id_to_row[uid]}:C{id_to_row[uid]}", [row_data])
                logger.info(f"Обновлена запись в Google Sheets: user_id={uid}")
            else:
                new_rows.append(row_data)

        if new_rows:
            worksheet.append_rows(new_rows)
            logger.info(f"Добавлено {len(new_rows)} новых строк в Google Sheets")

    except TimeoutError as e:
        logger.error(f"TimeoutError при работе с Google Sheets: {e}", exc_info=True)
        return "timeout"
    except ConnectionError as e:
        logger.error(f"ConnectionError при работе с Google Sheets: {e}", exc_info=True)
        return "connection_error"
    except (HTTPError, GoogleAuthError) as e:
        logger.error(f"Ошибка Google API: {e}", exc_info=True)
        return "api_error"
    except Exception as e:
        logger.exception(f"Неизвестная ошибка при работе с Google Sheets: {e}")
        return "unknown_error"


# dov = {
#     "user_id": 1,
#     "full_name": "фы",
#     "email": "s@s.s",
#     "registered_at": "2025-08-04 11:16:03",
# }

# send_to_google_sheets(dov)

# dov = {
#     "user_id": 2,
#     "full_name": "фы",
#     "email": "s@s.s",
#     "registered_at": "2025-08-04 11:16:03",
# }

# send_to_google_sheets(dov)
