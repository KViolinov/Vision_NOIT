import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(BASE_DIR, "app_data.json")


def check_launch_status() -> bool:
    if not os.path.exists(filename):
        return _first_launch()

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        print("Welcome back!")
        return False  # Returning user

    except json.JSONDecodeError:
        print("Invalid or empty app_data.json — resetting.")
        return _first_launch()


def _first_launch() -> bool:
    data = {"first_launch": False}

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("Welcome! First launch detected.")
    return True  # New user
