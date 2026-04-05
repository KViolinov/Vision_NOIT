import os
import requests
from dotenv import load_dotenv

load_dotenv()


def request_new_feature(command_name, user_notes=""):
    url = "https://kvb-bg.com/Vision/request_new_feature.php"

    data = {
        "api_key": os.getenv("EMAIL_SECRET_KEY"),
        "subject": command_name,
        "context": user_notes,
        "user_id": "User_12345",
    }

    try:
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            print("Successfully sent request to developer!")
        else:
            print(f"Server error: {response.status_code}")
    except Exception as e:
        print(f"Connection failed: {e}")
