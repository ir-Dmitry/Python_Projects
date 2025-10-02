# config_loader.py
import json
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Класс для загрузки конфигураций из JSON файлов."""

    COMMANDS_CONFIG_PATH = "./data/commands_config.json"
    BUTTONS_CONFIG_PATH = "./data/buttons_config.json"

    def __init__(self):
        pass  # No need to pass paths anymore

    def load_commands_config(self) -> dict:
        """Загружает конфигурацию команд из JSON файла."""
        try:
            with open(self.COMMANDS_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            return data  # Assumes commands are under "commands" key
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

    def save_commands_config(self, commands_data):
        """Сохраняет конфигурацию команд в JSON файл."""
        try:
            with open(self.COMMANDS_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(
                    commands_data, f, indent=2, ensure_ascii=False
                )  # Добавлен indent для читабельности
            print(
                f"Конфигурация команд успешно сохранена в '{self.COMMANDS_CONFIG_PATH}'."
            )
        except Exception as e:
            print(f"Ошибка при сохранении конфигурации команд: {e}")

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
