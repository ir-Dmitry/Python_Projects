# config_loader.py
import json
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Класс для загрузки конфигураций из JSON файлов."""

    COMMANDS_CONFIG_PATH = "./handlers/commands_config.json"
    BUTTONS_CONFIG_PATH = "./keyboards/buttons_config.json"

    def __init__(self):
        pass  # No need to pass paths anymore

    def load_commands_config(self) -> dict:
        """Загружает конфигурацию команд из JSON файла."""
        try:
            with open(self.COMMANDS_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data["commands"]  # Assumes commands are under "commands" key
        except FileNotFoundError:
            logger.error(f"Файл конфигурации не найден: {self.COMMANDS_CONFIG_PATH}")
            return {}
        except json.JSONDecodeError:
            logger.error(
                f"Ошибка декодирования JSON в файле: {self.COMMANDS_CONFIG_PATH}"
            )
            return {}
        except KeyError:
            logger.error(
                f"Корневой ключ 'commands' не найден в файле: {self.COMMANDS_CONFIG_PATH}"
            )
            return {}

    def load_buttons_config(self) -> dict:
        """Загружает конфигурацию кнопок из JSON файла."""
        try:
            with open(self.BUTTONS_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data["buttons"]  # Added ["buttons"]
        except FileNotFoundError:
            logger.error(f"Файл конфигурации не найден: {self.BUTTONS_CONFIG_PATH}")
            return {}
        except json.JSONDecodeError:
            logger.error(
                f"Ошибка декодирования JSON в файле: {self.BUTTONS_CONFIG_PATH}"
            )
            return {}
        except KeyError:
            logger.error(
                f"Корневой ключ 'buttons' не найден в файле: {self.BUTTONS_CONFIG_PATH}"
            )
            return {}
