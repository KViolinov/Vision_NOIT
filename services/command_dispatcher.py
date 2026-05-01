import inspect
import logging

from ui.vision_ui import VisionUI
from services.audio_service import AudioService

from functions.communication.whatsapp import whatsapp_send_message
from functions.communication.message_composer import generate_message
from functions.communication.phone_call import initiate_call
from functions.take_screenshot import take_screenshot
from functions.vision_camera import gemini_vision
from functions.record_video import record_video
from functions.song_recognition import recognize_song
from functions.play_spotify import play_song, play_music, pause_music
from functions.essential_functions.config import (
    change_jarvis_voice,
    change_jarvis_name,
)
from functions.document_writer import open_word
from functions.essential_functions.request_new_feature import request_new_feature

logger = logging.getLogger("vision")

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
    "initiate_call": initiate_call,
    "recognize_song": recognize_song,
    "request_new_feature": request_new_feature,
}

_UI_STATE_COMMANDS: dict[str, str] = {
    "gemini_vision": "camera",
    "record_video": "recording",
}


class CommandDispatcher:
    def __init__(self, ui: VisionUI, audio: AudioService):
        self.ui = ui
        self.audio = audio
        self.registry = COMMAND_REGISTRY
        self.ui_state_overrides = _UI_STATE_COMMANDS

    def dispatch(self, data: dict) -> None:
        response_type = data.get("response_type")
        match response_type:
            case "answer":
                self._handle_answer(data)
            case "command":
                self._handle_command(data)
            case _:
                logger.warning(f"Unknown response_type received: {response_type}")

    def _handle_answer(self, data: dict) -> None:
        answer = data.get("answer", "")
        logger.info(f"Assistant answer: {answer}")
        self.ui.set_state("answering")
        self.audio.speak(answer)

    def _handle_command(self, data: dict) -> None:
        function_name = data.get("function")
        params = data.get("parameters", {})

        if not function_name:
            logger.warning("Command response missing 'function' key.")
            return

        func = self.registry.get(function_name)
        if not func:
            self._handle_unknown_command(function_name)
            return

        try:
            self._execute_command(function_name, func, params)
            logger.info(f"Command '{function_name}' executed successfully.")
        except Exception as e:
            logger.error(f"Error executing command '{function_name}': {e}")
            self.audio.play_sound(self.audio.config.error)

    def _execute_command(self, name: str, func: callable, params: dict) -> None:
        if name in self.ui_state_overrides:
            self.ui.set_state(self.ui_state_overrides[name])
            func(self.ui.set_state)
            self.ui.set_state("idle")
            return

        sig = inspect.signature(func)
        expected_params = set(sig.parameters.keys())
        unexpected = set(params.keys()) - expected_params

        if unexpected:
            logger.warning(
                f"LLM returned unexpected params for '{name}': {unexpected} — ignored."
            )
            params = {k: v for k, v in params.items() if k in expected_params}

        bound = sig.bind(**params)
        bound.apply_defaults()
        func(*bound.args, **bound.kwargs)

    def _handle_unknown_command(self, function_name: str) -> None:
        logger.warning(f"Unknown command requested: '{function_name}'")
        self.audio.play_sound(self.audio.config.error)
        self.audio.speak(
            "Съжалявам, все още не мога да направя това. "
            "Изпратих съобщение на разработчика да го добави в следващия ъпдейт!"
        )
        request_new_feature(
            function_name,
            user_notes=f"User triggered missing command: {function_name}",
        )
