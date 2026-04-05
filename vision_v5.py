from __future__ import annotations

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
import logging
from dataclasses import dataclass, field
from pathlib import Path

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

from jarvis_functions.essential_functions.config import (
    get_jarvis_voice,
    get_jarvis_name,
    change_jarvis_name,
    change_jarvis_voice,
    get_wait_interval_seconds,
    get_type_discussion,
)

# from jarvis_functions.phone_call import call_phone
from jarvis_functions.whatsapp import whatsapp_send_message
from jarvis_functions.send_message_instagram.message_composer import generate_message

from jarvis_functions.instagram_call import start_call

# Screenshot, Photo and Video related functions
from jarvis_functions.take_screenshot import take_screenshot
from jarvis_functions.vision_camera import gemini_vision
from jarvis_functions.record_video import record_video

# Music related functions (commented out for now)
from jarvis_functions.song_recognition import recognize_song
from jarvis_functions.play_spotify import play_song, play_music, pause_music

# Document and Mail related functions
from jarvis_functions.document_writer import open_word

# from jarvis_functions.mail_related import (
#     #readMail, create_appointment, send_email
#     readMail, send_email
# )

# from account.update_user_settings import update_user_settings
# from account.image_sync import sync_user_photo

from jarvis_functions.essential_functions.launch_state import check_launch_status
from jarvis_functions.essential_functions.version_checking import check_for_update
from jarvis_functions.essential_functions.request_new_feature import request_new_feature

from jarvis_functions.essential_functions.home_server import ask_local_model

from ui.vision_ui import VisionUI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("vision.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("vision")

PROJECT_VERSION = "2.0.0"

REQUIRED_ENV_VARS = ["GEMINI_KEY", "SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET"]

_JARVIS_RESPONSES = [
    "Тук съм, как мога да помогна?",
    "Слушам, как мога да Ви асистирам?",
    "Тук съм, как мога да помогна?",
    "С какво мога да Ви бъда полезен?",
]

_STOP_KEYWORDS = frozenset(
    [
        "спри",
        "благодаря",
        "благодаря ти",
        "край",
        "чао",
        "довиждане",
        "нищо",
    ]
)
_STOP_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(kw) for kw in _STOP_KEYWORDS) + r")\b",
    re.IGNORECASE,
)

COMMAND_REGISTRY: dict[str, callable] = {
    "generate_message": generate_message,
    "gemini_vision": gemini_vision,
    "take_screenshot": take_screenshot,
    "record_video": record_video,
    "play_song": play_song,
    "pause_music": pause_music,
    "change_jarvis_voice": change_jarvis_voice,
    "change_jarvis_name": change_jarvis_name,
    "openWord": open_word,
    "start_call": start_call,
    "recognize_song": recognize_song,
    "request_new_feature": request_new_feature,
}

_UI_STATE_COMMANDS: dict[str, str] = {
    "gemini_vision": "camera",
    "record_video": "recording",
}


@dataclass(frozen=True)
class AudioConfig:
    startup: str = "sound_files/startup_sound_v2.mp3"
    notification: str = "sound_files/notification_sound.mp3"
    mic_toggle: str = "sound_files/mic_mute_unmute_sound.mp3"
    error: str = "sound_files/error_message_sound.mp3"
    default_volume: float = 0.5
    wake_word_delay: float = 0.5


def validate_environment() -> None:  # Check if an API key is missing in the .env
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Please check your .env file."
        )


def load_system_prompt(path: str = "prompts/system_prompt.txt") -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        raise RuntimeError(
            f"System prompt not found at '{path}'. "
            "Create the file or check your working directory."
        )


class SpotifyClient:
    def __init__(self) -> None:
        self._client: spotipy.Spotify | None = None
        self._lock = threading.Lock()

    def _get_client(self) -> spotipy.Spotify:
        with self._lock:
            if self._client is None:
                client_id = os.getenv("SPOTIFY_CLIENT_ID")
                client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
                if not client_id or not client_secret:
                    raise EnvironmentError("Spotify credentials not configured.")
                self._client = spotipy.Spotify(
                    auth_manager=spotipy.SpotifyOAuth(
                        client_id=client_id,
                        client_secret=client_secret,
                        redirect_uri="http://localhost:8888/callback",
                        scope=(
                            "user-library-read "
                            "user-read-playback-state "
                            "user-modify-playback-state"
                        ),
                    )
                )
        return self._client

    def current_playback(self):
        return self._get_client().current_playback()


def setup_tray(ui: VisionUI) -> None:
    try:
        icon_path = Path(__file__).parent / "ui" / "assets" / "vision_logo.ico"
        image = Image.open(icon_path)

        def on_show(icon, item):
            logger.info("Tray: restoring Vision window.")
            ui.show()

        def on_exit(icon, item):
            logger.info("Tray: exit requested.")
            icon.stop()
            os._exit(0)

        menu = pystray.Menu(item("Show Vision", on_show), item("Exit", on_exit))
        tray_icon = pystray.Icon("VISION", image, "VISION Assistant", menu)
        tray_icon.run()

    except Exception as e:
        logger.error("Tray setup failed: %s", e)


def setup_mic_hotkey(ui: VisionUI, audio: AudioConfig) -> None:
    def on_toggle():
        muted = toggle_mic()
        ui.update_mic_status(muted)
        state = "🔇 Muted" if muted else "🎙️ Unmuted"
        logger.info("Mic toggled: %s", state)
        pygame.mixer.music.load(audio.mic_toggle)
        pygame.mixer.music.set_volume(audio.default_volume)
        pygame.mixer.music.play()

    keyboard.add_hotkey("m", on_toggle)


class VisionAssistant:
    def __init__(
        self,
        ui: VisionUI,
        chat_session,
        audio: AudioConfig,
    ) -> None:
        self.ui = ui
        self.chat_session = chat_session
        self.audio = audio
        self._shutdown = threading.Event()

    def run(self) -> None:
        """Main entry point. Call from a dedicated thread."""
        self._play_sound(self.audio.startup)
        time.sleep(5)  # allow UI and pygame to fully initialize

        self._handle_startup_greeting()
        check_for_update(PROJECT_VERSION)

        self._main_loop()

    def shutdown(self) -> None:
        """Signal the assistant to stop cleanly."""
        self._shutdown.set()

    def _main_loop(self) -> None:
        logger.info("Assistant main loop started.")
        while not self._shutdown.is_set():
            if self._await_wake_word():
                self._handle_conversation()

    def _await_wake_word(self) -> bool:
        logger.info("Waiting for wake word...")

        while not self._shutdown.is_set():
            if is_muted():
                time.sleep(0.3)
                continue

            user_input = record_text()

            if not user_input:
                continue

            if get_jarvis_name().lower() in user_input.lower():
                self._on_wake()
                return True

        return False

    def _on_wake(self) -> None:
        logger.info("Wake word detected.")
        self._play_sound(self.audio.notification)
        time.sleep(self.audio.wake_word_delay)
        self.ui.set_state("answering")
        generate_audio_from_text(random.choice(_JARVIS_RESPONSES), get_jarvis_voice())
        self.ui.set_state("thinking")

    def _handle_conversation(self) -> None:
        logger.info("Listening for command...")

        if is_muted():
            self.ui.set_state("idle")
            return

        user_input = record_text()

        if not user_input:
            logger.warning("No input detected after wake word.")
            self.ui.set_state("idle")
            return

        self.handle_user_input(user_input)
        self._follow_up_window()

    def _follow_up_window(self) -> None:
        wait_seconds = get_wait_interval_seconds()
        discussion_type = get_type_discussion()
        deadline = time.monotonic() + wait_seconds  # monotonic is correct for durations

        self.ui.set_state("listening")
        logger.info("Follow-up window open for %s seconds.", wait_seconds)

        while time.monotonic() < deadline:
            if is_muted():
                self.ui.set_state("idle")
                return

            follow_up = record_text(timeout=wait_seconds)

            if not follow_up or follow_up == "__MIC_MUTED__":
                self.ui.set_state("idle")
                return

            follow_up = follow_up.lower().strip()
            logger.info("Follow-up received: %s", follow_up)

            if self._is_stop_command(follow_up):
                generate_audio_from_text(
                    "Няма за какво, ако има нещо — питай!", get_jarvis_voice()
                )
                self._play_sound(self.audio.notification)
                self.ui.set_state("idle")
                return

            self.handle_user_input(follow_up)

            if discussion_type == "once":
                self.ui.set_state("idle")
                return

            # Continuous mode: reset the window after each valid input
            deadline = time.monotonic() + wait_seconds

        logger.info("Follow-up window expired, returning to idle.")
        self.ui.set_state("idle")

    def handle_user_input(self, user_input: str) -> None:
        try:
            response = self.chat_session.send_message(user_input)

            if not response.parts:
                logger.warning("LLM response was empty or blocked.")
                self.ui.set_state("idle")
                return

            data = json.loads(response.text)

        except errors.ClientError as e:
            logger.error("Gemini API error: %s", e)
            self.ui.set_state("idle")
            return

        except json.JSONDecodeError:
            logger.warning(
                "Could not parse LLM response as JSON, reading as plain text."
            )
            generate_audio_from_text(response.text, get_jarvis_voice())
            self.ui.set_state("idle")
            return

        self._dispatch(data)

    def _dispatch(self, data: dict) -> None:
        response_type = data.get("response_type")

        match response_type:
            case "answer":
                self._handle_answer(data)
            case "command":
                self._handle_command(data)
            case _:
                logger.warning("Unknown response_type received: %s", response_type)

    def _handle_answer(self, data: dict) -> None:
        answer = data.get("answer", "")
        logger.info("Assistant answer: %s", answer)
        self.ui.set_state("answering")
        generate_audio_from_text(answer, get_jarvis_voice())

    def _handle_command(self, data: dict) -> None:
        function_name = data.get("function")
        params = data.get("parameters", {})

        if not function_name:
            logger.warning("Command response missing 'function' key.")
            return

        func = COMMAND_REGISTRY.get(function_name)

        if not func:
            self._handle_unknown_command(function_name)
            return

        try:
            self._execute_command(function_name, func, params)
            logger.info("Command '%s' executed successfully.", function_name)
        except Exception as e:
            logger.error("Error executing command '%s': %s", function_name, e)
            self._play_sound(self.audio.error)

    def _execute_command(self, name: str, func: callable, params: dict) -> None:
        if name in _UI_STATE_COMMANDS:
            self.ui.set_state(_UI_STATE_COMMANDS[name])
            func(self.ui.set_state)
            self.ui.set_state("idle")
            return

        sig = inspect.signature(func)
        expected_params = set(sig.parameters.keys())
        unexpected = set(params.keys()) - expected_params

        if unexpected:
            logger.warning(
                "LLM returned unexpected params for '%s': %s — they will be ignored.",
                name,
                unexpected,
            )
            params = {k: v for k, v in params.items() if k in expected_params}

        # Always bind by name — safe regardless of param count,
        # immune to dict ordering issues.
        bound = sig.bind(**params)
        bound.apply_defaults()
        func(*bound.args, **bound.kwargs)

    def _handle_unknown_command(self, function_name: str) -> None:
        logger.warning("Unknown command requested: '%s'", function_name)
        self._play_sound(self.audio.error)
        generate_audio_from_text(
            "Съжалявам, все още не мога да направя това. "
            "Изпратих съобщение на разработчика да го добави в следващия ъпдейт!",
            get_jarvis_voice(),
        )
        request_new_feature(
            function_name,
            user_notes=f"User triggered missing command: {function_name}",
        )

    def _handle_startup_greeting(self) -> None:
        if check_launch_status():
            generate_audio_from_text(
                "Здравейте, аз съм Слави — вашият личен гласов асистент. "
                "Тук съм да ви помогна с всяка ваша нужда. "
                "Ако желаете да ме извикате, просто кажете името ми.",
                get_jarvis_voice(),
            )
        else:
            generate_audio_from_text(
                "На линия съм, извикайте ме когато имате нужда.",
                get_jarvis_voice(),
            )

    def _play_sound(self, path: str, volume: float | None = None) -> None:
        vol = volume if volume is not None else self.audio.default_volume
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(vol)
        pygame.mixer.music.play()

    @staticmethod
    def _is_stop_command(text: str) -> bool:
        return bool(_STOP_PATTERN.search(text))


def main() -> None:
    load_dotenv()  # Load and validate .env
    validate_environment()

    # Innitialize audio system and config
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    audio = AudioConfig()

    # Initialize UI
    ui = VisionUI("ui", "index.html")
    ui.show()

    # LLM client — created here
    system_prompt = load_system_prompt()
    gemini_client = genai.Client(api_key=os.getenv("GEMINI_KEY"))
    model_config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json",
        temperature=0.7,
    )
    chat_session = gemini_client.chats.create(
        model="gemini-2.5-flash", config=model_config
    )

    # Start the Assistant
    assistant = VisionAssistant(ui=ui, chat_session=chat_session, audio=audio)

    # Hotkeys
    setup_mic_hotkey(ui, audio)

    # Start the background threads
    threads = [
        threading.Thread(target=assistant.run, daemon=True, name="chatbot"),
        threading.Thread(target=lambda: setup_tray(ui), daemon=True, name="tray"),
    ]
    for t in threads:
        t.start()
        logger.info("Started thread: %s", t.name)

    # Block main thread on UI event loop
    ui.exec()


if __name__ == "__main__":
    main()
