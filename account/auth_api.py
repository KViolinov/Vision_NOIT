import psycopg2
import bcrypt
import json
import os

DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:IZqVUkqAdSQZbnXqpWEVumimZLFRtPFW@hopper.proxy.rlwy.net:16266/railway",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNT_FILE = os.path.join(BASE_DIR, "user_settings.json")


def get_connection():
    return psycopg2.connect(DB_URL)


def sign_up(email: str, password: str, profile_pic_url: str = None):
    """Register a new user. Returns (success: bool, message: str)."""
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (email, password_hash, profile_pic_url)
            VALUES (%s, %s, %s, %s)
            RETURNING id, email
            """,
            (email, hashed_pw, profile_pic_url),
        )
        row = cur.fetchone()
        conn.commit()

        user_data = {"UserID": str(row[0]), "Email": row[1]}
        _save_user_settings(user_data, password)

        print(f"[✅ Auth] Registered: {email}")
        return True, "Акаунтът е създаден успешно!"

    except psycopg2.IntegrityError:
        return False, "Потребител с този имейл вече съществува."
    except Exception as e:
        print(f"[❌ Auth] sign_up error: {e}")
        return False, f"Грешка: {e}"
    finally:
        if conn:
            cur.close()
            conn.close()


def login(email: str, password: str):
    """Validate credentials. Returns (success: bool, message: str, user_data: dict|None)."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, email, password_hash FROM users WHERE email = %s",
            (email,),
        )
        row = cur.fetchone()

        if not row:
            return False, "Потребителят не е намерен.", None

        user_id, db_email, stored_hash = row

        if not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
            return False, "Грешна парола.", None

        user_data = {
            "UserID": str(user_id),
            "Email": db_email,
        }
        _save_user_settings(user_data, password)

        print(f"[✅ Auth] Logged in: {email}")
        return True, "Успешен вход!", user_data

    except Exception as e:
        print(f"[❌ Auth] login error: {e}")
        return False, f"Грешка: {e}", None
    finally:
        if conn:
            cur.close()
            conn.close()


def _save_user_settings(user_data: dict, plain_password: str):
    """Persist logged-in user to user_settings.json (never stores bcrypt hash here)."""
    payload = {
        "status": "success",
        "message": "Login successful.",
        "data": {**user_data, "PlainPassword": plain_password},
    }
    with open(ACCOUNT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"[💾 Auth] Saved user_settings.json for {user_data.get('Email')}")
