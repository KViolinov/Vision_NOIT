import time
import pyautogui
import pywhatkit as kit
import webbrowser

from functions.essential_functions.enhanced_elevenlabs import (
    generate_audio_from_text,
)
from functions.essential_functions.voice_input import record_text

from functions.essential_functions.config import get_jarvis_voice
from functions.communication.contact_locator import find_contact

# from account.check_account import require_login

jarvis_voice = get_jarvis_voice()


# @require_login
def whatsapp_send_message(contact: str, message: str) -> None:
    phone_number = find_contact(contact, "телефон")
    # subprocess.run(["powershell", "Start-Process firefox.exe"])
    # Send the message (it types but does not send)

    kit.sendwhatmsg_instantly(phone_number, message)

    # Wait for WhatsApp Web to load and type the message
    time.sleep(2)  # Adjust this if needed

    # Press "Enter" to send the message
    pyautogui.press("enter")

    generate_audio_from_text(text="Съобщението е изпратено", voice=jarvis_voice)


def start_whatsapp_call(contact: str) -> None:
    phone_number = find_contact(contact, "телефон")

    # Strip leading + for the URL if present, WhatsApp Web expects it without
    clean_number = phone_number.lstrip("+")

    # Open WhatsApp Web chat for that number
    url = f"whatsapp://send?phone={clean_number}"
    webbrowser.open(url)

    # Wait for WhatsApp Web to fully load
    time.sleep(8)

    # if video:
    #     # Click the video call button (top-right area — adjust coords if needed)
    #     pyautogui.hotkey("alt", "shift", "v")  # WhatsApp Web shortcut for video call
    # else:
    #     # Voice call shortcut
    #     pyautogui.hotkey("alt", "shift", "p")  # WhatsApp Web shortcut for voice call

    generate_audio_from_text(text="Обаждането е started", voice=jarvis_voice)
