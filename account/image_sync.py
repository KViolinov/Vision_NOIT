import os
import re
import time
import json
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Vision/account
ACCOUNT_FILE = os.path.join(BASE_DIR, "user_settings.json")
USER_PFP = os.path.join(BASE_DIR, "..", "ui", "assets", "user_pfp.png")
USER_PFP = os.path.abspath(USER_PFP)  # normalize to absolute path


def sync_user_photo():
    try:
        with open(ACCOUNT_FILE, "r", encoding="utf-8") as f:
            user = json.load(f)
        data = user.get("data", user)
        email = data.get("Email")
        if not email:
            print("[⚠] No user email — skipping cloud sync.")
            return False

        safe_email = re.sub(r'[^a-zA-Z0-9]', '_', email.lower())
        cloud_url = f"https://kvb-bg.com/Vision/uploads/{safe_email}_pfp.png"

        # ✅ Check if user_pfp.png already exists and is recent
        if os.path.exists(USER_PFP):
            file_age = time.time() - os.path.getmtime(USER_PFP)
            if file_age < 86400:  # less than 24 hours old
                print("[ℹ] Local user photo is recent — skipping download.")
                return True

        print(f"[☁] Checking cloud image for {email}...")
        r = requests.get(cloud_url, timeout=10)
        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("image/"):
            with open(USER_PFP, "wb") as f:
                f.write(r.content)
            print("[✅] User photo downloaded and saved locally.")
            return True
        else:
            print("[ℹ] No photo found in the cloud — using default.")
            return False
    except Exception as e:
        print(f"[⚠] Error syncing photo: {e}")
        return False