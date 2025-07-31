import requests
from bs4 import BeautifulSoup
import re


def read_links_from_file(filename):
    links = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            stripped_line = line.strip()
            if stripped_line:  # игнорируем пустые строки
                links.append(stripped_line)
    return links


# Пример использования:
filename = "links.txt"  # замени на имя твоего файла
links = read_links_from_file(filename)


headers = {"User-Agent": "Mozilla/5.0"}

# for i, link in enumerate(links, start=1):
#     try:
#         response = requests.get(link, headers=headers, timeout=10)
#         response.raise_for_status()

#         # Явно указываем кодировку UTF-8
#         response.encoding = "utf-8"

#         soup = BeautifulSoup(response.text, "html.parser")

#         # Ищем нужный div
#         abstract_div = soup.find("div", class_="abstract")

#         if abstract_div:
#             text = abstract_div.get_text(" ")
#             text = re.sub(r"[\n\r\t\xa0\u200b]", " ", text)
#             text = re.sub(r" +", " ", text)
#             text = text.strip()
#         else:
#             text = "Не найден текст в указанном div."

#     except Exception as e:
#         text = f"Ошибка: {e}"

#     print(f"Ссылка {i}: {link}")
#     print(text)
#     print("")
# print("-" * 80)

# Сохраняем в файл
#     filename = f"doc{i}.txt"
#     with open(filename, "w", encoding="utf-8") as file:
#         file.write(text)

# print("=" * 80)

for i, link in enumerate(links, start=1):

    print(f"Патент {i}: {link}")
    print("")
    print("")
