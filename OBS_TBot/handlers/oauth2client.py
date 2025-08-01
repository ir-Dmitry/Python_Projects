# URL вашего Google Apps Script веб-хука


# ——— В обработчике email ———
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()

    if not is_valid_email(email):
        await message.answer("❌ Неверный формат email.\nПопробуйте ещё раз:")
        return

    # Сохраняем email
    await state.update_data(email=email)
    data = await state.get_data()
    full_name = data["full_name"]
    user_id = message.from_user.id
    registered_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Сохраняем в JSON
    success = save_registration(user_id, full_name, email)
    await message.answer(success, parse_mode="HTML")

    # 🚀 Отправляем данные в Google Таблицу
    send_to_google_sheets(user_id, full_name, email, registered_at)

    # Завершаем состояние
    await state.finish()
