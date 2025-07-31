import re
import logging
from aiogram import types
from aiogram.types import ParseMode
from config_loader import ConfigLoader


logger = logging.getLogger(__name__)

# --- Инициализация ConfigLoader ---
config_loader = ConfigLoader()


def escape_specific_markdown(text: str) -> str:
    """Экранирует специальные символы MarkdownV2, кроме * и _."""
    escape_chars = r">#+-=|.{}!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


def get_section_summaries(filename: str) -> list[tuple[int, str]]:
    """
    Парсит файл и извлекает краткое описание каждой секции.

    Args:
        filename: Путь к файлу.

    Returns:
        Список кортежей, где первый элемент - номер секции, а второй - ее краткое описание.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        sections = re.findall(
            r"# --- SECTION (\d+) ---\n(.*?)(?=# --- SECTION|\Z)", content, re.DOTALL
        )

        summaries = []
        for section_number, section_content in sections:
            # Разделяем контент на строки и берем первую строку, как краткое описание
            first_line = section_content.strip().split("\n")[0]
            summaries.append((int(section_number), first_line))

        return summaries

    except FileNotFoundError:
        print(f"Файл '{filename}' не найден.")
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return []


async def send_sections_list(message: types.Message, filename: str):
    """Отправляет список доступных секций в Telegram."""
    section_summaries = get_section_summaries(filename)

    if section_summaries:
        text = "Доступные секции:\n"
        for section_number, summary in section_summaries:
            text += f"- [/sec_]{section_number}: {escape_specific_markdown(summary)}\n"
        await message.reply(
            text, parse_mode=ParseMode.MARKDOWN
        )  # Отправляем в Telegram
    else:
        await message.reply("Секции не найдены.")


async def send_file_section(
    message: types.Message, filename: str, section: int = 1, parse_mode=None
):
    """Отправляет содержимое секции файла."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        sections = content.split("# --- SECTION {} ---".format(section))

        if len(sections) > 1:
            text = (
                sections[1].split("# --- SECTION {} ---".format(section + 1))[0].strip()
            )  # Split to get content until next section
            # if not parse_mode:
            text = escape_specific_markdown(
                text
            )  # Escape specific MarkdownV2 special characters

            await message.answer(
                f"{text}", parse_mode=parse_mode
            )  # Отправляем как отформатированный текст

        else:
            await message.reply("Секция не найдена.")

    except FileNotFoundError:
        await message.reply(f"Файл '{filename}' не найден.")
    except Exception as e:
        logger.exception(f"Ошибка при чтении файла: {e}")
        await message.reply(f"Ошибка при чтении файла: {e}")


async def send_commands_list(message: types.Message):
    """Отправляет список команд из JSON файла в Telegram."""
    commands_data = config_loader.load_commands_config()
    # logging.info(commands_data)

    text = "Список команд:\n"
    for (
        command_name,
        command_details,
    ) in commands_data.items():  # Использование .items()
        text += f"- [/{escape_specific_markdown(command_name)}]"
        try:
            text += f": {escape_specific_markdown(command_details['info'])}\n"
        except:
            text += ": info не указан"

    text += "\n\n❌Внимание!❌\nСпециальные команды находятся в процессе разработки. Возможны ошибки."

    await message.reply(text, parse_mode=ParseMode.MARKDOWN)


async def delete_command(message: types.Message, command_name: str):
    """Удаляет команду из файла конфигурации команд."""
    try:
        commands_data = config_loader.load_commands_config()

        # Проверяем, существует ли команда
        if command_name in commands_data:  # Исправлено: доступ к "command"
            del commands_data[command_name]  # Удаляем команду
            config_loader.save_commands_config(commands_data)  # Сохраняем изменения
            await message.reply(
                f"Команда `{command_name}` успешно удалена.",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await message.reply(
                f"Команда `{command_name}` не найдена.", parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.exception(f"Ошибка при удалении команды: {e}")
        await message.reply(f"Произошла ошибка при удалении команды: {e}")
