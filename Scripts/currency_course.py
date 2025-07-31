import requests
import xml.etree.ElementTree as ET

API_URL = "http://www.cbr.ru/scripts/XML_daily.asp"


def get_currency_rate(currency_code):
    """Получает курс валюты по ее коду из API ЦБ РФ."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        response.encoding = "windows-1251"
        root = ET.fromstring(response.text)

        for valute in root.findall("Valute"):
            if valute.find("CharCode").text == currency_code:
                value = valute.find("Value").text
                nominal = valute.find("Nominal").text
                return float(value.replace(",", ".")) / float(nominal)

        return None  # Если валюта не найдена

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return None
    except ET.ParseError as e:
        print(f"Ошибка при обработке XML: {e}")
        return None


# Получаем курсы валют
currencies = ["USD", "EUR", "CNY", "BYN", "TRY", "INR"]
rates = {code: get_currency_rate(code) for code in currencies}

# Выводим результаты
print("Курсы валют ЦБ РФ:")
for currency, rate in rates.items():
    if rate is not None:
        print(f"{currency}: {rate:.4f} руб.")
    else:
        print(f"{currency}: не удалось получить курс")
