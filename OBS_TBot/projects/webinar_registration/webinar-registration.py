def main(user_inputs=None):
    if user_inputs is None:
        user_inputs = []

    a = user_inputs[0] if len(user_inputs) > 0 else ""
    registration = a + "Регистрация на вебинар"
    return registration
