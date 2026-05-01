import json
import os
from functools import wraps

from functions.essential_functions.enhanced_elevenlabs import (
    generate_audio_from_text,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNT_FILE = os.path.join(BASE_DIR, "user_settings.json")


def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Try to load account data
        try:
            with open(ACCOUNT_FILE, "r", encoding="utf-8") as f:
                user_data = json.load(f)
        except FileNotFoundError:
            from functions.essential_functions.config import (
                get_jarvis_voice,
            )

            print("❌ No account file found — please create an account first.")
            generate_audio_from_text(
                "Нямате достъп до тази функция понеже нямате акаунт или не сте се логнали"
                "За да използвате тази фунция, моля логнете се",
                get_jarvis_voice(),
            )

            return None
        except json.JSONDecodeError:
            print("❌ Account file corrupted — please log in again.")
            return None

        # Extract inner data if wrapped
        data = user_data.get("data", user_data)
        email = data.get("Email")
        password = data.get("Password")

        if not email or not password:
            from functions.essential_functions.config import (
                get_jarvis_voice,
            )  # 👈 moved here

            print("❌ You are not logged in — this action requires an account.")
            generate_audio_from_text(
                "Нямате достъп до тази функция понеже нямате акаунт или не сте се логнали"
                "За да използвате тази фунция, моля логнете се",
                get_jarvis_voice(),
            )
            return None

        print(f"[🔐 Logged in as: {email}]")
        return func(*args, **kwargs)

    return wrapper
