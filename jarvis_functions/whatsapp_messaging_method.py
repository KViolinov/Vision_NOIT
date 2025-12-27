import time
import pyautogui
import pywhatkit as kit

from jarvis_functions.essential_functions.enhanced_elevenlabs import generate_audio_from_text
from jarvis_functions.essential_functions.voice_input import record_text

from jarvis_functions.essential_functions.change_config_settings import get_jarvis_voice
from jarvis_functions.essential_functions.contact_locator import find_contact

from account.check_account import require_login

jarvis_voice = get_jarvis_voice()

@require_login
def whatsapp_send_message():
    generate_audio_from_text(text="На кого искате да пратя съобшение?", voice=jarvis_voice)

    print("Listening for camera info...")
    contact_info = record_text()

    number_to_text = find_contact(contact_info, "Телефон")
    generate_audio_from_text(text=f"Добре, съобщението ще бъде към {contact_info}. А какво ще искате да бъде съобщението?",
                            voice=jarvis_voice)

    print("Listening for message info...")
    message_info = record_text()

    #subprocess.run(["powershell", "Start-Process firefox.exe"])
    # Send the message (it types but does not send)

    kit.sendwhatmsg_instantly(number_to_text, message_info)

    # Wait for WhatsApp Web to load and type the message
    time.sleep(2)  # Adjust this if needed

    # Press "Enter" to send the message
    pyautogui.press("enter")

    generate_audio_from_text(text="Съобщението е изпратено", voice=jarvis_voice)
