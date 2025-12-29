import os
import json
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNT_FILE = os.path.join(BASE_DIR, "user_settings.json")
LOGIN_API_URL = "https://kvb-bg.com/Vision/api/login_api.php"


def update_user_settings():
    try:
        with open(ACCOUNT_FILE, "r", encoding="utf-8") as f:
            user_json = json.load(f)
    except Exception as e:
        print(f"[⚠] Failed to read user_settings.json: {e}")
        return False

    # ✅ handle nested 'data'
    data = user_json.get("data", user_json)

    email = data.get("Email")
    password = data.get("PlainPassword") or data.get("Password")

    if not email or not password:
        print("[⚠] Missing credentials in user_settings.json")
        return False

    payload = {"email": email, "password": password}

    try:
        response = requests.post(LOGIN_API_URL, json=payload, timeout=10)
        response.raise_for_status()
        api_response = response.json()
        print(
            f"[ℹ] API status: {api_response.get('status')}, message: {api_response.get('message')}"
        )

        if api_response.get("status") != "success" or "data" not in api_response:
            print("[⚠] Login failed or invalid API response.")
            return False

        # merge new data and keep plain password
        user_data = api_response["data"]
        user_data["PlainPassword"] = password

        new_json = {
            "status": "success",
            "message": "Login successful.",
            "data": user_data,
        }

        with open(ACCOUNT_FILE, "w", encoding="utf-8") as f:
            json.dump(new_json, f, indent=2, ensure_ascii=False)

        print("[✔] User info updated successfully.")
        return True

    except requests.RequestException as e:
        print(f"[⚠] Login request failed: {e}")
        return False
    except json.JSONDecodeError:
        print("[⚠] Invalid JSON response from API.")
        return False


if __name__ == "__main__":
    update_user_settings()
