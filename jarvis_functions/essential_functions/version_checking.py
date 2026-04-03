import requests
from packaging import version
from jarvis_functions.essential_functions.change_config_settings import (
    get_jarvis_voice,
    get_jarvis_name,
    change_jarvis_name,
    change_jarvis_voice,
    get_wait_interval_seconds,
    get_type_discussion,
)

from jarvis_functions.essential_functions.enhanced_elevenlabs import (
    generate_audio_from_text,
)


def check_for_update(PROJECT_VERSION: str):
    url = "https://kvb-bg.com/Vision/version.json"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # throws if 4xx/5xx

        data = response.json()

        latest_version = data.get("latest_version")
        minimum_version = data.get("min_required_version")
        required = data.get("force_update", False)
        message = data.get("message", "")
        update_type = data.get("update_type", "optional")
        release_date = data.get("release_date", "")

        if version.parse(latest_version) > version.parse(PROJECT_VERSION):
            print("Update available")
            generate_audio_from_text(
                "Наличен е нова версия на Vision. Можете да я изтеглите от Microsoft Store-a",
                get_jarvis_voice(),
            )

            if required:
                print("FORCE UPDATE")
                generate_audio_from_text(
                    "Наличен е нова версия на Vision. Можете да я изтеглите от Microsoft Store-a",
                    get_jarvis_voice(),
                )
        else:
            print("No update available")

    except requests.exceptions.RequestException as e:
        print(f"❌ Update check failed: {e}")
        return None
