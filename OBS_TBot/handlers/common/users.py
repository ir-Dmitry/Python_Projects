from ..file_reader import load_json, save_json, init_json

ALL_USERS_FILE = "data/all_users.json"


def init_users_file():
    init_json(ALL_USERS_FILE, [])


def load_all_users():
    return load_json(ALL_USERS_FILE, [])


def add_user(user_id: int, username: str) -> bool:
    users = load_all_users()
    if not any(u["id"] == user_id for u in users):
        users.append({"id": user_id, "username": username, "admin": False})
        save_json(ALL_USERS_FILE, users, [])
        return True
    return False


def add_admin(user_id: int) -> bool:
    users = load_all_users()
    user = next(
        (u for u in users if u["id"] == user_id and not u.get("admin", False)), None
    )
    if user:
        user["admin"] = True
        save_json(ALL_USERS_FILE, users, [])
        return True
    return False


def remove_admin(user_id: int) -> bool:
    users = load_all_users()
    user = next(
        (u for u in users if u["id"] == user_id and u.get("admin", False)), None
    )
    if user:
        user["admin"] = False
        save_json(ALL_USERS_FILE, users, [])
        return True
    return False


def is_admin(user_id: int) -> bool:
    users = load_all_users()
    user = next((u for u in users if u["id"] == user_id), None)
    return user and user.get("admin", False)
