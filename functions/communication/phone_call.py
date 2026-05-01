import pyautogui
import time
import subprocess
import webbrowser

import google.generativeai as genai
from functions.communication.contact_locator import find_contact

import os
from dotenv import load_dotenv

load_dotenv()

_CALL_BUTTON_IMG = (
    "functions\\communication\\assets\\windows_phone_link_call_button.jpg"
)


def extract_contact_from_text(user_input: str):
    genai.configure(api_key=os.getenv("GEMINI_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = (
        "Ще ти дам текст"
        "Искам да извлечеш само името на човека, на когото е адресирано, като отделна дума. "
        "Без здравей, без излишни думи, просто името на човека. "
        f"Текстът е: {user_input}"
    )

    response = model.generate_content(prompt)
    return response.candidates[0].content.parts[0].text.strip()


def initiate_call(user_input: str):
    name = extract_contact_from_text(user_input)
    phone_number = find_contact(name, "телефон")

    # subprocess.run(["cmd", "/c", "start", f"tel:{phone_number}"])
    webbrowser.open(f"tel:{phone_number}")
    time.sleep(3)  # Wait for the app to pop up

    try:
        button_pos = pyautogui.locateOnScreen(_CALL_BUTTON_IMG, confidence=0.8)
        if button_pos:
            target = pyautogui.center(button_pos)
            pyautogui.moveTo(target)
            pyautogui.mouseDown()
            time.sleep(0.1)  # Hold for 100ms
            pyautogui.mouseUp()
            print("Manual click sequence performed.")
    except:
        print("Could not find call button image, relying on Enter key.")
