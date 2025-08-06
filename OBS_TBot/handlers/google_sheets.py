# handlers/google_sheets.py
import time
import gspread
from requests.exceptions import HTTPError
from google.auth.exceptions import GoogleAuthError
from google.oauth2.service_account import Credentials

CREDENTIALS_FILE = "data/credentials.json"
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CLIENT = None


def authorize_google_sheets():
    global CLIENT
    if CLIENT is None:
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=scope
        )
        CLIENT = gspread.authorize(credentials)


def is_google_sheets_connected():
    try:
        global CLIENT
        spreadsheet = CLIENT.open("Регистрация на вебинар")
        return True
    except (HTTPError, GoogleAuthError) as e:
        print(f"Ошибка подключения: {e}")
        CLIENT = None
        return False


def send_to_google_sheets(pers: dict):
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            global CLIENT
            if CLIENT is None or not is_google_sheets_connected():
                print("Проверка соединения с Google Sheets.")
                authorize_google_sheets()

            spreadsheet = CLIENT.open("Регистрация на вебинар")
            worksheet = spreadsheet.sheet1
            worksheet.append_row([*pers.values()])
            print("Отправка данных в гугл таблицу прошла успешно! ✅")
            break
        except (HTTPError, GoogleAuthError) as e:
            print(
                f"Ошибка при отправке данных: {e}. Попытка {attempt + 1} из {max_attempts}"
            )
            if attempt == max_attempts - 1:
                raise
            time.sleep(2)


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
