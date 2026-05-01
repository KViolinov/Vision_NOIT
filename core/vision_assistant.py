import time
import logging
import threading
import random
import re

from ui.vision_ui import VisionUI
from services.audio_service import AudioService
from services.ai_service import AIService
from services.command_dispatcher import CommandDispatcher

from functions.essential_functions.config import (
    get_jarvis_name,
    get_wait_interval_seconds,
    get_type_discussion,
)
from functions.essential_functions.launch_state import check_launch_status
from functions.essential_functions.version_checking import check_for_update

logger = logging.getLogger("vision")

PROJECT_VERSION = "2.1.0"

_JARVIS_RESPONSES = [
    "Тук съм, как мога да помогна?",
    "Слушам, как мога да Ви асистирам?",
    "Тук съм, как мога да помогна?",
    "С какво мога да Ви бъда полезен?",
]

_STOP_KEYWORDS = frozenset(
    ["спри", "благодаря", "благодаря ти", "край", "чао", "довиждане", "нищо"]
)
_STOP_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(kw) for kw in _STOP_KEYWORDS) + r")\b", re.IGNORECASE
)


class VisionAssistant:
    def __init__(
        self,
        ui: VisionUI,
        audio: AudioService,
        ai: AIService,
        dispatcher: CommandDispatcher,
    ):
        self.ui = ui
        self.audio = audio
        self.ai = ai
        self.dispatcher = dispatcher
        self._shutdown = threading.Event()

    def run(self) -> None:
        self.audio.play_sound(self.audio.config.startup)
        time.sleep(5)  # allow UI and pygame to fully initialize

        self._handle_startup_greeting()
        check_for_update(PROJECT_VERSION)

        self._main_loop()

    def shutdown(self) -> None:
        self._shutdown.set()

    def _main_loop(self) -> None:
        logger.info("Assistant main loop started.")
        while not self._shutdown.is_set():
            if self._await_wake_word():
                self._handle_conversation()

    def _await_wake_word(self) -> bool:
        logger.info("Waiting for wake word...")
        while not self._shutdown.is_set():
            if self.audio.is_muted:
                time.sleep(0.3)
                continue

            user_input = self.audio.listen()
            if not user_input:
                continue

            if get_jarvis_name().lower() in user_input.lower():
                self._on_wake()
                return True
        return False

    def _on_wake(self) -> None:
        logger.info("Wake word detected.")
        self.audio.play_sound(self.audio.config.notification)
        time.sleep(self.audio.config.wake_word_delay)

        self.ui.set_state("answering")
        self.audio.speak(random.choice(_JARVIS_RESPONSES))
        self.ui.set_state("thinking")

    def _handle_conversation(self) -> None:
        logger.info("Listening for command...")
        if self.audio.is_muted:
            self.ui.set_state("idle")
            return

        user_input = self.audio.listen()
        if not user_input:
            logger.warning("No input detected after wake word.")
            self.ui.set_state("idle")
            return

        self._process_and_dispatch(user_input)
        self._follow_up_window()

    def _process_and_dispatch(self, user_input: str) -> None:
        response = self.ai.send_message(user_input)
        if response is None:
            self.ui.set_state("idle")
            return

        if isinstance(response, str):
            self.audio.speak(response)
            self.ui.set_state("idle")
            return

        self.dispatcher.dispatch(response)

    def _follow_up_window(self) -> None:
        wait_seconds = get_wait_interval_seconds()
        discussion_type = get_type_discussion()
        deadline = time.monotonic() + wait_seconds

        self.ui.set_state("listening")
        logger.info(f"Follow-up window open for {wait_seconds} seconds.")

        while time.monotonic() < deadline:
            if self.audio.is_muted:
                self.ui.set_state("idle")
                return

            follow_up = self.audio.listen(timeout=wait_seconds)
            if not follow_up or follow_up == "__MIC_MUTED__":
                self.ui.set_state("idle")
                return

            follow_up = follow_up.lower().strip()
            logger.info(f"Follow-up received: {follow_up}")

            if self._is_stop_command(follow_up):
                self.audio.speak("Няма за какво, ако има нещо — питай!")
                self.audio.play_sound(self.audio.config.notification)
                self.ui.set_state("idle")
                return

            self._process_and_dispatch(follow_up)

            if discussion_type == "once":
                self.ui.set_state("idle")
                return

            deadline = time.monotonic() + wait_seconds

        logger.info("Follow-up window expired, returning to idle.")
        self.ui.set_state("idle")

    def _handle_startup_greeting(self) -> None:
        if check_launch_status():
            self.audio.speak(
                "Здравейте, аз съм Слави — вашият личен гласов асистент. "
                "Тук съм да ви помогна с всяка ваша нужда. "
                "Ако желаете да ме извикате, просто кажете името ми."
            )
        else:
            self.audio.speak("На линия съм, извикайте ме когато имате нужда.")

    @staticmethod
    def _is_stop_command(text: str) -> bool:
        return bool(_STOP_PATTERN.search(text))
