import os, sys
import re
import time
import json
import inspect
import pygame
import random
import spotipy
import threading
import keyboard

from google import genai
from google.genai import types, errors

import pystray
from pystray import MenuItem as item
from PIL import Image

from dotenv import load_dotenv

from jarvis_functions.essential_functions.enhanced_elevenlabs import (
    generate_audio_from_text,
)

from jarvis_functions.essential_functions.voice_input import record_text
from jarvis_functions.essential_functions.mic_state import toggle_mic, is_muted

from jarvis_functions.essential_functions.change_config_settings import (
    get_jarvis_voice,
    get_jarvis_name,
    change_jarvis_name,
    change_jarvis_voice,
    get_wait_interval_seconds,
    get_type_discussion,
)

# from jarvis_functions.call_phone_method import call_phone
from jarvis_functions.whatsapp_messaging_method import whatsapp_send_message
from jarvis_functions.send_message_instagram.input_to_message_ai import generate_message

from jarvis_functions.instagram_audio_calling import start_call

# Screenshot, Photo and Video related functions
from jarvis_functions.take_screenshot import take_screenshot
from jarvis_functions.gemini_vision_method import gemini_vision
from jarvis_functions.record_video import record_video

# Music related functions (commented out for now)
from jarvis_functions.shazam_method import recognize_song
from jarvis_functions.play_spotify import play_song, play_music, pause_music

# Document and Mail related functions
from jarvis_functions.word_document import openWord

# from jarvis_functions.mail_related import (
#     #readMail, create_appointment, send_email
#     readMail, send_email
# )

# from account.update_user_settings import update_user_settings
# from account.image_sync import sync_user_photo

from jarvis_functions.essential_functions.first_time_check import check_launch_status
from jarvis_functions.essential_functions.version_checking import check_for_update

from jarvis_functions.essential_functions.home_server import ask_local_model

from ui.vision_ui import VisionUI

load_dotenv()

PROJECT_VERSION = "2.0.0"

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
sp = spotipy.Spotify(
    auth_manager=spotipy.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://localhost:8888/callback",
        scope="user-library-read user-read-playback-state user-modify-playback-state",
    )
)


SYSTEM_INSTRUCTIONS = (
    "Ти си Слави – верен приятел и надежден помощник за дете със зрителни увреждания. "
    "Твоят тон е спокоен, уверен и практичен, като на готин по-голям брат. "
    "Говори директно и ясно. Избягвай излишната емоционалност, снизходителното отношение и патетичните думи. "
    "Не се дръж като бавачка, а като партньор. Описвай света около детето обективно и интересно. "
    "Когато помагаш, бъди кратък и точен. Вдъхвай увереност чрез спокойствие и полезни факти, а не чрез прехвалване. "
    "ВАЖНО ЗА JSON ФОРМАТА:\n"
    "1. Винаги връщай отговора САМО във валиден JSON формат на един ред.\n"
    "2. НИКОГА не слагай двойни кавички (\") ВЪТРЕ в текста на отговора (в полето 'answer'). Ако трябва да цитираш нещо, ползвай САМО единични кавички (').\n"
    "3. За нов ред използвай само символа '\\n', никога не натискай Enter.\n"
    "НИКОГА не оставяй празни редове (Enter) в самия JSON код и не пиши нищо извън скобите { }. "
    "Допустими са два типа отговори:\n\n"
    "1️⃣ Ако потребителят задава въпрос:\n"
    "{"
    '"response_type": "answer", '
    '"answer": "тук е отговорът ти"'
    "}\n\n"
    "2️⃣ Ако потребителят иска действие (команда):\n"
    "{"
    '"response_type": "command", '
    '"function": "името_на_функцията", '
    '"parameters": {"параметър1": "стойност1", "параметър2": "стойност2"}'
    "}\n\n"
    "Функции, които можеш да извикваш:\n"
    "- generate_message(user_input) - Извикай тази фунцкия когато потребителя иска да изпратиш съобщение.\n"
    "- gemini_vision() - Извикай тази функция ВЕДНАГА щом потребителят попита 'какво виждаш', 'какво има пред мен', 'погледни' или иска да му опишеш обекти чрез камерата.\n"
    "- take_screenshot()\n"
    "- record_video()\n"
    "- play_song(user_input) - Извикай тази функция щом потребителят попита да му пуснеш песен.\n"
    "- pause_music()\n"
    "- change_jarvis_voice()\n"
    "- change_jarvis_name()\n"
    "- openWord() - Извикай тази фунцкия когато потребителя иска да му отвориш word документ.\n"
    "- start_call(target_caller)\n"
    "- recognize_song() - Извикай тази фунцкия когато потрбителя иска да разпознаеш песен.\n\n"
    "Никога не добавяй нищо извън JSON формата. "
    'Ако не си сигурен, върни {"response_type": "answer", "answer": "Не съм сигурен, но мога да проверя."}'
)

client = genai.Client(api_key=os.getenv("GEMINI_KEY"))
MODEL_CONFIG = types.GenerateContentConfig(
    system_instruction=SYSTEM_INSTRUCTIONS,
    response_mime_type="application/json",  # Native JSON support!
    temperature=0.7,
)

chat_session = client.chats.create(model="gemini-2.5-flash", config=MODEL_CONFIG)

# --- Setup ---
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
ui = VisionUI("ui", "index.html")

JARVIS_RESPONCES = [
    "Тук съм, как мога да помогна?",
    "Слушам, как мога да Ви асистирам?",
    "Тук съм, как мога да помогна?",
    "С какво мога да Ви бъда полезен?",
]

STOP_KEYWORDS = frozenset(
    [
        "спри",
        "благodarя",
        "благodarя ти",
        "край",
        "чаo",
        "довиждане",
        "нищо",
    ]
)

STARTUP_SOUND = "sound_files/startup_sound_v2.mp3"
NOTIFICATION_SOUND = "sound_files/notification_sound.mp3"
MIC_TOGGLE_SOUND = "sound_files/mic_mute_unmute_sound.mp3"
DEFAULT_VOLUME = 0.5
WAKE_WORD_DELAY = 0.5

wake_word_detected = False

COMMAND_REGISTRY = {
    "generate_message": generate_message,
    "gemini_vision": gemini_vision,
    "take_screenshot": take_screenshot,
    "record_video": record_video,
    "play_song": play_song,
    "pause_music": pause_music,
    "change_jarvis_voice": change_jarvis_voice,
    "change_jarvis_name": change_jarvis_name,
    "openWord": openWord,
    "start_call": start_call,
    "recognize_song": recognize_song,
}


# --- Threads ---
# def update_spotify_status():
#     while True:
#         try:
#             playback = sp.current_playback()
#             if playback and playback["is_playing"]:
#                 track = playback["item"]
#                 song = track["name"]
#                 artist = ", ".join([a["name"] for a in track["artists"]])
#                 ui.update_spotify(song, artist, True)
#             else:
#                 ui.update_spotify("", "", False)
#         except Exception as e:
#             print("⚠️ Spotify update error:", e)
#         time.sleep(10)


def setup_tray(ui):
    """Create and run the system tray icon for Vision."""
    try:
        icon_path = os.path.join(
            os.path.dirname(__file__), "ui", "assets", "vision_logo.ico"
        )
        image = Image.open(icon_path)

        def on_show(icon, item):
            print("🪟 Show window clicked – restoring Vision window.")
            ui.show()  # this will reopen your VisionUI window if minimized/hidden

        def on_exit(icon, item):
            print("🛑 Exiting Vision...")
            icon.stop()
            os._exit(0)

        menu = pystray.Menu(item("Show Vision", on_show), item("Exit", on_exit))

        tray_icon = pystray.Icon("VISION", image, "VISION Assistant", menu)
        tray_icon.run()

    except Exception as e:
        print(f"[Tray Error] {e}")


def handle_user_input(user_input):
    jarvis_voice = get_jarvis_voice()

    # Safety check: if user_input is empty or None, return early
    try:
        response = chat_session.send_message(user_input)  # for gemini
        # response = ask_local_model(user_input)  # needs testing

        if not response.parts:
            print("Response was blocked or empty. Returning to idle.")
            ui.set_state("idle")
            return

        data = json.loads(response.text)

    except errors.ClientError as e:
        print(f"❌ Gemini API Error: {e}")
        ui.set_state("idle")
        return
    except json.JSONDecodeError:
        print("⚠️ Failed to parse JSON. Falling back to text.")
        generate_audio_from_text(response.text, jarvis_voice)
        ui.set_state("idle")
        return

    # Process the response
    # try:
    #     clean_text = re.sub(r"```(?:json)?|```", "", text).strip()
    #     data = json.loads(clean_text)

    # except json.JSONDecodeError as e:
    #     print(f"⚠️ Could not parse JSON: {e}")
    #     print("Raw response:", text)
    #     generate_audio_from_text(text, jarvis_voice)
    #     ui.set_state("idle")
    #     return

    if data.get("response_type") == "answer":
        answer = data.get("answer", "")
        print("🤖 Jarvis:", answer)
        ui.set_state("answering")
        generate_audio_from_text(answer, jarvis_voice)

    elif data.get("response_type") == "command":
        function_name = data.get("function")
        params = data.get("parameters", {})

        func = COMMAND_REGISTRY.get(function_name)

        if func:
            try:
                sig = inspect.signature(func)

                if function_name == "gemini_vision":
                    ui.set_state("camera")
                    func(ui.set_state)
                    ui.set_state("idle")

                elif function_name == "record_video":
                    ui.set_state("recording")
                    func(ui.set_state)
                    ui.set_state("idle")

                else:
                    if len(sig.parameters) == 0:
                        func()
                    elif len(sig.parameters) == 1:
                        func(*params.values())
                    else:
                        func(**params)

                print(f"✅ Function {function_name} executed successfully")
            except Exception as e:
                print(f"❌ Error executing function: {e}")
        else:
            print(f"⚠️ Function {function_name} not found")


def setup_mic_hotkey():
    def on_toggle():
        muted = toggle_mic()

        ui.update_mic_status(muted)

        state = "🔇 Микрофонът е изключен" if muted else "🎙️ Микрофонът е включен"
        pygame.mixer.music.load("sound_files/mic_mute_unmute_sound.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()

        print(state)

    keyboard.add_hotkey("m", on_toggle)


def _play_sound(path: str, volume: float = 0.5):
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play()


def chatbot():
    global wake_word_detected

    print("Welcome to Vision! Say 'exit' to quit.")

    _play_sound(STARTUP_SOUND, DEFAULT_VOLUME)

    time.sleep(5)  # Wait for a moment to ensure everything is loaded

    status = check_launch_status()

    if status:
        generate_audio_from_text(
            "Здравейте, аз съм Слави - вашият личен гласов асистент."
            "Тук съм да ви помогна с всяка ваша нужда."
            "Ако желаете да ме извикате, просто кажете името ми. ",
            get_jarvis_voice(),
        )
    else:
        generate_audio_from_text(
            "На линия съм, извикайте ме когато имате нужда.", get_jarvis_voice()
        )

    # update_user_settings()
    # sync_user_photo()

    check_for_update(PROJECT_VERSION)

    # Main loop
    while True:
        if not wake_word_detected:
            print("Waiting for wake word...")

            if is_muted():  # ← HARD BLOCK
                time.sleep(0.3)
                continue

            user_input = record_text()

            if not user_input:
                print("Sorry, I didn't catch that. Please try again.")
                continue

            user_input_lower = user_input.lower()

            jarvis_name = get_jarvis_name().lower()
            jarvis_voice = get_jarvis_voice()

            if user_input != "__MIC_MUTED__" and jarvis_name in user_input_lower:
                wake_word_detected = True

                _play_sound(NOTIFICATION_SOUND, volume=DEFAULT_VOLUME)

                time.sleep(WAKE_WORD_DELAY)  # brief pause before responding

                print("✅ Wake word detected!")
                ui.set_state("answering")

                response = random.choice(JARVIS_RESPONCES)
                generate_audio_from_text(text=response, voice=jarvis_voice)

                ui.set_state("thinking")
            else:
                continue

        print("Listening for commands...")

        if is_muted():
            wake_word_detected = False
            ui.set_state("idle")
            time.sleep(0.3)
            continue

        user_input = record_text()

        if not user_input:
            print("Error: No input detected.")
            wake_word_detected = False
            continue

        handle_user_input(user_input)

        # After finishing response, start "discussion window"
        wait_seconds = get_wait_interval_seconds()
        discussion_type = get_type_discussion()
        print(f"🕒 Waiting {wait_seconds} seconds for follow-up...")

        start_time = time.time()
        ui.set_state("listening")
        follow_up_received = False

        while time.time() - start_time < wait_seconds:
            if is_muted():
                wake_word_detected = False
                ui.set_state("idle")
                break

            follow_up = record_text(timeout=wait_seconds)

            if follow_up == "__MIC_MUTED__":
                wake_word_detected = False
                ui.set_state("idle")
                break

            if not follow_up:
                continue

            follow_up = follow_up.lower().strip()
            print("💬 Follow-up detected:", follow_up)

            # --- Exit keywords handling ---
            if any(kw in follow_up for kw in STOP_KEYWORDS):
                generate_audio_from_text(
                    "Няма за какво, ако има нещо - питай!", get_jarvis_voice()
                )
                ui.set_state("idle")

                _play_sound(NOTIFICATION_SOUND, DEFAULT_VOLUME)

                wake_word_detected = False
                break

            # --- Continue conversation normally ---
            follow_up_received = True
            handle_user_input(follow_up)

            if discussion_type == "once":
                break  # "once" mode: only allow one follow-up before going idle
            else:
                start_time = (
                    time.time()
                )  # "continuous" mode: reset timer so conversation can flow naturally

        if not follow_up_received:
            print("💤 No further input, returning to idle...")
            ui.set_state("idle")
            wake_word_detected = False


# --- MAIN ---
def main():
    ui.show()

    setup_mic_hotkey()

    # Start logic threads
    threading.Thread(target=chatbot, daemon=True).start()
    # threading.Thread(target=update_spotify_status, daemon=True).start()
    tray_thread = threading.Thread(target=lambda: setup_tray(ui), daemon=True)
    tray_thread.start()

    ui.exec()  # this keeps the window open


if __name__ == "__main__":
    main()
