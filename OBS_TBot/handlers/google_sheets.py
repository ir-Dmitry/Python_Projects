# handlers/google_sheets.py
import time
import gspread
from typing import Union, List, Dict
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


FIELDS_ORDER = ["user_id", "registered_at", "available"]


def send_data_to_google_sheets(data: Union[dict, list[dict]]):
    """
    Универсальная функция для отправки данных в Google Sheets.
    Обновляет существующие строки по user_id и добавляет новые.
    Принимает словарь или список словарей.
    """
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
            print(f"🔄 Обновлено: user_id={uid}")
        else:
            new_rows.append(row_data)

    for row in new_rows:
        worksheet.append_row(row)
    if new_rows:
        print(f"✅ Добавлено {len(new_rows)} новых строк")

    # def send_users_to_google_sheets(users: list[dict]):
    #     """
    #     Массовая синхронизация пользователей с Google Sheets.
    #     Полностью перезаписывает данные (кроме шапки).
    #     """
    #     global CLIENT
    #     if CLIENT is None or not is_google_sheets_connected():
    #         print("Проверка соединения с Google Sheets.")
    #         authorize_google_sheets()

    #     worksheet = CLIENT.open("Регистрация на вебинар").sheet1

    #     # готовим список строк
    #     rows = [[u.get(field, "") for field in FIELDS_ORDER] for u in users]

    #     # очищаем всё кроме заголовков и расширяем под новые данные
    #     worksheet.resize(len(rows) + 1)  # +1 строка под заголовки

    #     # записываем массив (со второй строки)
    #     if rows:
    #         worksheet.update(f"A2:C{len(rows)+1}", rows)

    #     print(f"✅ Обновлено {len(rows)} строк в Google Sheets")


# def send_to_google_sheets(pers: dict):
#     max_attempts = 3
#     for attempt in range(max_attempts):
#         try:
#             global CLIENT
#             if CLIENT is None or not is_google_sheets_connected():
#                 print("Проверка соединения с Google Sheets.")
#                 authorize_google_sheets()

#             spreadsheet = CLIENT.open("Регистрация на вебинар")
#             worksheet = spreadsheet.sheet1

#             # ищем user_id в таблице
#             records = worksheet.get_all_records()
#             row_index = None
#             for i, row in enumerate(records, start=2):
#                 if str(row.get("user_id")) == str(pers["user_id"]):
#                     row_index = i
#                     break

#             row_data = [pers.get(field, "") for field in FIELDS_ORDER]

#             if row_index:
#                 worksheet.update(f"A{row_index}:C{row_index}", [row_data])
#                 print(f"🔄 Данные обновлены для user_id={pers['user_id']}")
#             else:
#                 worksheet.append_row(row_data)
#                 print("✅ Добавлена новая строка")

#             break

#         except (HTTPError, GoogleAuthError) as e:
#             print(
#                 f"Ошибка при отправке данных: {e}. Попытка {attempt + 1} из {max_attempts}"
#             )
#             if attempt == max_attempts - 1:
#                 raise
#             time.sleep(2)


# def send_to_google_sheets(pers: dict):
#     max_attempts = 3
#     for attempt in range(max_attempts):
#         try:
#             global CLIENT
#             if CLIENT is None or not is_google_sheets_connected():
#                 print("Проверка соединения с Google Sheets.")
#                 authorize_google_sheets()

#             spreadsheet = CLIENT.open("Регистрация на вебинар")
#             worksheet = spreadsheet.sheet1
#             worksheet.append_row([*pers.values()])
#             print("Отправка данных в гугл таблицу прошла успешно! ✅")
#             break
#         except (HTTPError, GoogleAuthError) as e:
#             print(
#                 f"Ошибка при отправке данных: {e}. Попытка {attempt + 1} из {max_attempts}"
#             )
#             if attempt == max_attempts - 1:
#                 raise
#             time.sleep(2)


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
