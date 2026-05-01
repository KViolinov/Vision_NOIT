import os
import sys
import threading
import keyboard
import logging
from pathlib import Path

import pystray
from pystray import MenuItem as item
from PIL import Image
from dotenv import load_dotenv

from ui.vision_ui import VisionUI
from functions.essential_functions.mic_state import toggle_mic

from services.audio_service import AudioConfig, AudioService
from services.ai_service import AIService
from services.command_dispatcher import CommandDispatcher
from core.vision_assistant import VisionAssistant

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("vision.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("vision")

REQUIRED_ENV_VARS = ["GEMINI_KEY", "SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET"]


def load_system_prompt(path: str = "prompts/system_prompt.txt") -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        raise RuntimeError(
            f"System prompt not found at '{path}'. Create the file or check your working directory."
        )


def validate_environment() -> None:
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\nPlease check your .env file."
        )


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
        logger.error(f"Tray setup failed: {e}")


def setup_mic_hotkey(ui: VisionUI, audio: AudioService) -> None:
    def on_toggle():
        muted = toggle_mic()
        ui.update_mic_status(muted)
        state = "🔇 Muted" if muted else "🎙️ Unmuted"
        logger.info(f"Mic toggled: {state}")
        audio.play_sound(audio.config.mic_toggle)

    keyboard.add_hotkey("m", on_toggle)


def main() -> None:
    load_dotenv()
    validate_environment()

    # 1. Boot up configurations and hardware services
    audio_config = AudioConfig()
    audio_service = AudioService(audio_config)
    ui = VisionUI("ui", "index.html")

    # 2. Boot up Logic/Software services
    ai_service = AIService(
        api_key=os.getenv("GEMINI_KEY"), system_prompt=load_system_prompt()
    )
    dispatcher = CommandDispatcher(ui=ui, audio=audio_service)

    # 3. Create Orchestrator
    assistant = VisionAssistant(
        ui=ui, audio=audio_service, ai=ai_service, dispatcher=dispatcher
    )

    # 4. Setup Hotkeys and UI
    ui.show()
    setup_mic_hotkey(ui, audio_service)

    # 5. Start background threads
    threads = [
        threading.Thread(target=assistant.run, daemon=True, name="chatbot"),
        threading.Thread(target=lambda: setup_tray(ui), daemon=True, name="tray"),
    ]
    for t in threads:
        t.start()
        logger.info(f"Started thread: {t.name}")

    # 6. Block main thread on UI
    ui.exec()


if __name__ == "__main__":
    main()
