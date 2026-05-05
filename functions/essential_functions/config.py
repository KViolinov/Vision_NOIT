import json
import os

from functions.essential_functions.voice_input import record_text
from functions.essential_functions.enhanced_elevenlabs import (
    generate_audio_from_text,
)

from account.check_account import require_login

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        default = {"jarvis_name": "Слави", "jarvis_voice": "Slavi"}
        save_config(default)
        return default
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# @require_login
def change_jarvis_voice():
    voices = ["Brian", "Jessica", "Roger", "Slavi", "Samantha", "Harvey", "Yordan"]
    config = load_config()

    current_voice = config.get("jarvis_voice", "Brian")

    # Ask user to choose a new voice
    generate_audio_from_text(
        text="Разбира се! С кой глас бихте желали да говоря? "
        "Имам следните гласове на разположение: Брайън,",
        voice=current_voice,
    )
    generate_audio_from_text("Джесика", voice="Jessica")
    generate_audio_from_text("Роджър", voice="Roger")
    generate_audio_from_text("Харви", voice="Harvey")
    generate_audio_from_text("Слави", voice="Slavi")
    generate_audio_from_text("Йордан", voice="Yordan")
    generate_audio_from_text("и Саманта. Кой глас бихте предпочели?", voice="Samantha")

    print("🎙️ Listening for voice choice...")
    user_input = record_text().lower()

    if any(x in user_input for x in ["брайън", "brian"]):
        new_voice = voices[0]
    elif any(x in user_input for x in ["джесика", "jessica"]):
        new_voice = voices[1]
    elif any(x in user_input for x in ["роджър", "roger"]):
        new_voice = voices[2]
    elif any(x in user_input for x in ["слави", "slavi"]):
        new_voice = voices[3]
    elif any(x in user_input for x in ["саманта", "samantha"]):
        new_voice = voices[4]
    elif any(x in user_input for x in ["харви", "harvey"]):
        new_voice = voices[5]
    else:
        generate_audio_from_text(
            "Не разбрах гласа. Ще оставя стария.", voice=current_voice
        )
        return

    config["jarvis_voice"] = new_voice
    save_config(config)

    generate_audio_from_text(
        text=f"Супер! Смених гласа на {new_voice}.", voice=new_voice
    )


# @require_login
def change_jarvis_name():
    config = load_config()
    current_voice = config.get("jarvis_voice", "Brian")

    generate_audio_from_text(
        "Разбира се, как бихте желали да се казвам?", voice=current_voice
    )

    print("🎙️ Listening for new name...")
    user_input = record_text()

    if not user_input:
        generate_audio_from_text(
            "Не можах да разбера. Може ли да повторите?", voice=current_voice
        )
        user_input = record_text()

    if user_input:
        config["jarvis_name"] = user_input.strip().capitalize()
        save_config(config)
        generate_audio_from_text(
            text=f"Супер! От сега нататък можете да ме наричате {user_input}.",
            voice=current_voice,
        )
    else:
        generate_audio_from_text(
            "Все още не разбрах. Ще запазя старото име.", voice=current_voice
        )


def get_jarvis_name() -> str:
    return load_config().get("jarvis_name", "Слави")


def get_jarvis_voice() -> str:
    return load_config().get("jarvis_voice", "Slavi")


def get_wait_interval_seconds() -> int:
    return load_config().get("wait_interval_seconds", 5)


def get_type_discussion() -> str:
    return load_config().get("type_discussion", "once")
