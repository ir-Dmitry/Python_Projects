ERROR_MESSAGES = {
    "timeout": "⚠️ Данные не отправлены в Google Таблицу (таймаут).",
    "connection_error": "⚠️ Нет подключения к Google Таблице.",
    "api_error": "⚠️ Ошибка Google API.",
    "unknown_error": "⚠️ Неизвестная ошибка при сохранении в Google Таблицу.",
}


def format_registration_message(tmp_time, gs_result="success") -> str:
    if gs_result == "success":
        return (
            "✅ <b>Регистрация завершена!</b>\n\n"
            f"🗓 Дата вебинара: {tmp_time.date()}.\n"
            f"🕰 Время: {tmp_time.strftime('%H:%M')}.\n"
            "Напоминание о вебинаре придет вовремя."
        )
    else:
        return ERROR_MESSAGES.get(gs_result, "❌ Неизвестная ошибка при регистрации.")
