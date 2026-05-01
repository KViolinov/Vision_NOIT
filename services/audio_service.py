import pygame
from dataclasses import dataclass

from functions.essential_functions.enhanced_elevenlabs import (
    generate_audio_from_text,
)
from functions.essential_functions.voice_input import record_text
from functions.essential_functions.mic_state import is_muted
from functions.essential_functions.config import get_jarvis_voice


@dataclass(frozen=True)
class AudioConfig:
    startup: str = "sound_files/startup_sound_v2.mp3"
    notification: str = "sound_files/notification_sound.mp3"
    mic_toggle: str = "sound_files/mic_mute_unmute_sound.mp3"
    error: str = "sound_files/error_message_sound.mp3"
    default_volume: float = 0.5
    wake_word_delay: float = 0.5


class AudioService:
    def __init__(self, config: AudioConfig):
        self.config = config
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    def play_sound(self, path: str, volume: float | None = None) -> None:
        vol = volume if volume is not None else self.config.default_volume
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(vol)
        pygame.mixer.music.play()

    def speak(self, text: str, voice: str | None = None) -> None:
        target_voice = voice or get_jarvis_voice()
        generate_audio_from_text(text, target_voice)

    def listen(self, timeout: float | None = None) -> str:
        return record_text(timeout=timeout)

    @property
    def is_muted(self) -> bool:
        return is_muted()
