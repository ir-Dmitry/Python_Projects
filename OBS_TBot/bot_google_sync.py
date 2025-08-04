import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Путь к твоему JSON-файлу
CREDENTIALS_FILE = "credentials.json"

# Области доступа (не меняй)
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# Авторизация
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(credentials)

# Открываем таблицу по названию
spreadsheet = client.open("Регистрация на вебинар")  # ← замени на реальное имя

# Выбираем лист (например, "Лист1")
worksheet = spreadsheet.sheet1  # или: spreadsheet.worksheet("Лист1")

# Прочитать все строки
data = worksheet.get_all_records()
print(data)

worksheet.append_row(["user_id", "full_name", "email", "registered_at"])

# worksheet.append_row(
#     [
#         "1127371080",
#         "Муслимов Дмитрий Николаевич",
#         "s@sd.w",
#         "2025-04-05 12:00:00",
#     ]
# )

# worksheet.clear()
# worksheet.update('A1', 'Новое значение')
