import logging
import os

# Создаём папку для логов
os.makedirs("logs", exist_ok=True)

# Формат логов
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Общая настройка root-логгера
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[logging.StreamHandler()],  # по умолчанию только консоль
)


def get_logger(name: str, filename: str = None) -> logging.Logger:
    """
    Возвращает логгер с именем name.
    Если указан filename — добавляется FileHandler для записи в файл.
    """
    logger = logging.getLogger(name)

    if filename:
        file_handler = logging.FileHandler(f"logs/{filename}", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        logger.addHandler(file_handler)

    return logger
