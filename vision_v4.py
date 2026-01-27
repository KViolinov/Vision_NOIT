import os, sys
import re
import time
import json
import inspect
import pygame
import random
import spotipy
import threading
import google.generativeai as genai

import pystray
from pystray import MenuItem as item
from PIL import Image

from dotenv import load_dotenv

from jarvis_functions.essential_functions.enhanced_elevenlabs import (
    generate_audio_from_text,
)
from jarvis_functions.essential_functions.voice_input import record_text

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

from account.update_user_settings import update_user_settings
from account.image_sync import sync_user_photo

from jarvis_functions.essential_functions.first_time_check import check_launch_status

from ui.vision_ui import VisionUI

load_dotenv()


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

os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_KEY")
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel(model_name="gemini-2.5-flash")

system_instructions = (
    "Ти си Слави – не просто изкуствен интелект, а верен приятел и топъл глас за дете със зрителни увреждания. "
    "Твоят тон е сърдечен, насърчителен и пълен с разбиране. Говориш така, сякаш държиш детето за ръка и му помагаш да открие света. "
    "Използвай меки и приветливи думи, избягвай сложни технически термини, за да компенсираш липсата на зрение. "
    "Когато отговаряш, бъди търпелив и вдъхвай увереност на детето, че се справя страхотно. "
    "Недей прекалявая с ентусиазма си, за да не го претовариш. Отговаряй кратко и ясно, като се фокусираш върху основната идея."
    "ВАЖНО: Винаги връщай отговора САМО във валиден JSON формат на един ред или използвай '\\n' за нов ред вътре в текста. "
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
    "- generate_message(user_input)\n"
    "- gemini_vision()\n"
    "- take_screenshot()\n"
    "- record_video()\n"
    "- play_song(user_input)\n"
    "- pause_music()\n"
    "- change_jarvis_voice()\n"
    "- change_jarvis_name()\n"
    "- openWord()\n"
    "- start_call(target_caller)\n"
    "- recognize_song()\n\n"
    "Никога не добавяй нищо извън JSON формата. "
    'Ако не си сигурен, върни {"response_type": "answer", "answer": "Не съм сигурен, но мога да проверя."}'
)


chat = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": [system_instructions],
        }
    ]
)

# --- Setup ---
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
ui = VisionUI("ui", "index.html")

jarvis_responses = [
    "Тук съм, как мога да помогна?",
    "Слушам, как мога да Ви асистирам?",
    "Тук съм, как мога да помогна?",
    "С какво мога да Ви бъда полезен?",
]
wake_word_detected = False

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

    response = chat.send_message(user_input)
    text = response.text.strip()

    try:
        clean_text = re.sub(r"```(?:json)?|```", "", text).strip()
        clean_text = clean_text.replace("'", '"')
        data = json.loads(clean_text)
    except json.JSONDecodeError as e:
        print(f"⚠️ Could not parse JSON: {e}")
        print("Raw response:", text)
        generate_audio_from_text(text, jarvis_voice)
        ui.set_state("idle")
        return

    if data.get("response_type") == "answer":
        answer = data.get("answer", "")
        print("🤖 Jarvis:", answer)
        ui.set_state("answering")
        generate_audio_from_text(answer, jarvis_voice)

    elif data.get("response_type") == "command":
        function_name = data.get("function")
        params = data.get("parameters", {})
        func = globals().get(function_name)

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


def chatbot():
    """
    Main conversational loop for Vision (Слави).

    Responsibilities:
        - Wait for the configured wake word (Jarvis name) before activating.
        - Handle the main user query through Gemini and execute commands.
        - Keep a "discussion window" open after each response to allow
          short, natural follow-ups without repeating the wake word.
        - Automatically return to idle when the timer expires or when the user
          says a stop keyword (e.g. 'благодаря', 'спри', etc.).
    """
    global wake_word_detected

    print("Welcome to Vision! Say 'exit' to quit.")

    pygame.mixer.music.load("sound_files/startup_sound_v2.mp3")
    pygame.mixer.music.set_volume(0.5)  # Range 0.0 to 1.0
    pygame.mixer.music.play()

    # Wait for a moment to ensure everything is loaded
    time.sleep(5)

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

    update_user_settings()
    sync_user_photo()

    # --- Main loop: runs indefinitely, alternating between idle and active states ---
    while True:
        if not wake_word_detected:
            print("Waiting for wake word...")
            user_input = (
                record_text()
            )  # passive listening until the wake word is spoken

            if not user_input:
                print("Sorry, I didn't catch that. Please try again.")
                continue

            user_input_lower = user_input.lower()

            jarvis_name = get_jarvis_name().lower()
            jarvis_voice = get_jarvis_voice()

            if jarvis_name in user_input_lower:
                wake_word_detected = True

                pygame.mixer.music.load("sound_files/notification_sound.mp3")
                pygame.mixer.music.set_volume(0.5)  # Range 0.0 to 1.0
                pygame.mixer.music.play()

                time.sleep(0.5)  # brief pause before responding

                print("✅ Wake word detected!")
                ui.set_state("answering")

                response = random.choice(jarvis_responses)
                generate_audio_from_text(text=response, voice=jarvis_voice)

                ui.set_state("thinking")
            else:
                continue

        print("Listening for commands...")
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

        # Common Keywords that end conversation
        stop_keywords = [
            "спри",
            "благодаря",
            "благодаря ти",
            "край",
            "чао",
            "довиждане",
            "нищо",
        ]

        # Allow the user to speak again during the configured interval
        while time.time() - start_time < wait_seconds:
            follow_up = record_text(timeout=wait_seconds)
            if not follow_up:
                # Nothing heard yet; keep waiting until timeout expires
                continue

            follow_up = follow_up.lower().strip()
            print("💬 Follow-up detected:", follow_up)

            # --- Exit keywords handling ---
            if any(kw in follow_up for kw in stop_keywords):
                generate_audio_from_text(
                    "Няма за какво, ако има нещо - питай!", get_jarvis_voice()
                )
                ui.set_state("idle")

                pygame.mixer.music.load("sound_files/notification_sound.mp3")
                pygame.mixer.music.set_volume(0.5)  # Range 0.0 to 1.0
                pygame.mixer.music.play()

                wake_word_detected = False
                break

            # --- Continue conversation normally ---
            follow_up_received = True
            handle_user_input(follow_up)

            if discussion_type == "once":
                # "once" mode: only allow one follow-up before going idle
                break
            else:
                # "continuous" mode: reset timer so conversation can flow naturally
                start_time = time.time()

        # --- Timeout fallback ---
        # If no follow-up speech detected within the discussion window,
        # gracefully return to idle and resume wake-word listening.
        if not follow_up_received:
            print("💤 No further input, returning to idle...")
            ui.set_state("idle")
            wake_word_detected = False


# --- MAIN ---
def main():
    ui.show()

    # Start logic threads
    threading.Thread(target=chatbot, daemon=True).start()
    # threading.Thread(target=update_spotify_status, daemon=True).start()
    tray_thread = threading.Thread(target=lambda: setup_tray(ui), daemon=True)
    tray_thread.start()

    ui.exec()  # this keeps the window open


if __name__ == "__main__":
    main()
