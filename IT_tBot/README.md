# IT_tBot

IT_tBot - это Telegram-бот, созданный для упрощения работы с Python скриптами в работе.

## Особенности

- **Динамическая настройка команд:** Команды и их обработчики настраиваются с помощью JSON-файлов, что упрощает добавление и изменение функциональности без изменения кода.
- **Обработка различных типов ответов:** Бот поддерживает отправку текстовых сообщений, клавиатур и других типов ответов на основе конфигурации.
- **Модульная структура:** Код разделен на модули, что облегчает его понимание, поддержку и расширение.
- **Обработка кнопок:** Бот умеет обрабатывать нажатия на кнопки и выполнять соответствующие действия.
- **Использование файлов конфигурации:** Для хранения настроек используются JSON файлы.

## Требования

- Python 3.7+
- Библиотеки, перечисленные в `requirements.txt`

## Установка

1. По причине того, что в репозитории находится множество проектов, необходимо конкретные папки для скачивания.

Включите режим разреженного вывода:

```bash
git sparse-checkout init --cone
```

Укажите папки, которые вы хотите скачать. Например, если вам нужна папка `my_folder`:

```bash
git sparse-checkout set my_folder
```

Теперь выполните обычную команду `git clone`:

```bash
git remote add origin https://github.com/ir-Dmitry/Python_Projects.git

git pull origin master
```

2.  Создайте и активируйте виртуальное окружение:

```python
python3 -m venv <имя_окружения>
<имя_окружения>\Scripts\activate
```

3.  Установите зависимости:

```python
pip install -r requirements.txt
```

4.  Создайте файл `.env` в корне проекта и добавьте токен вашего бота:

```
BOT_TOKEN=YOUR_BOT_TOKEN
```

Замените `YOUR_BOT_TOKEN` на токен, полученный от BotFather.

## Запуск

Запустите бота с помощью команды:

```bash
python main.py
```
