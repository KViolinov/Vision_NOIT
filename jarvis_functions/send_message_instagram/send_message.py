import pyautogui
import time
import webbrowser
import pyperclip

from jarvis_functions.essential_functions.contact_locator import find_contact

def send_message_to_instagram_user(target_username: str, message: str):
    #url_to_open = get_url_for_username(target_username)
    url_to_open = find_contact(target_username, "линк")

    if url_to_open:
        print(f"Opening {url_to_open} in your default web browser...")
        webbrowser.open(url_to_open, new=2)

        print("Waiting for page to load...")
        time.sleep(25)

        message_to_send = message + " - изпратено от Слави"
        pyperclip.copy(message_to_send)

        print("Waiting for user to focus the chat input box...")
        time.sleep(5)  # Или pyautogui.click(...)

        # Paste and send
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1)
        pyautogui.press("enter")

        print("Message sent.")
        time.sleep(2)

        # Close tab
        pyautogui.hotkey("ctrl", "w")

        print("Done.")

    else:
        print("No URL found.")
