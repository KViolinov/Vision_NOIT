import requests
from typing import Dict

home_server_url = "http://100.113.130.25:8000/chat"


def ask_local_model(user_input: str) -> Dict:
    try:
        r = requests.post(home_server_url, json={"prompt": user_input})
        r.raise_for_status()  # raises HTTPError if status != 200
        return r.json()
    except requests.RequestException as e:
        print("Request failed:", e)
        return {"error": str(e)}
    except ValueError as e:  # JSON decoding error
        print("Failed to parse response:", e, r.text)
        return {"error": "Invalid JSON from server"}
