import os
import json
from datetime import datetime
from typing import Optional, Dict
from ..file_reader import load_jsons


def load_users(path="data/users.json") -> list:
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    return load_jsons(path)


def save_users(users: list, path="data/users.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def add_user(user_id: int, path="data/users.json") -> Optional[Dict]:
    users = load_users(path)
    if any(u["user_id"] == user_id for u in users):
        return None  # уже зарегистрирован
    user = {
        "user_id": user_id,
        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "available": True,
    }
    users.append(user)
    save_users(users, path)
    return user
