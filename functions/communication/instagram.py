from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip
import time
from functions.communication.contact_locator import find_contact


def send_message_to_instagram_user(target_username: str, message: str) -> bool:
    url = find_contact(target_username, "линк")
    if not url:
        print("No URL found for user.")
        return False

    options = Options()
    # Connect to already-running Chrome instead of spawning a new one
    options.add_experimental_option("debuggerAddress", "localhost:9222")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        print(f"Navigated to: {driver.current_url}")
        time.sleep(3)

        input_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[aria-label='Message']")
            )
        )

        input_box.click()
        time.sleep(0.5)

        message_to_send = message + " - изпратено от Слави"
        pyperclip.copy(message_to_send)
        input_box.send_keys(Keys.CONTROL, "v")
        time.sleep(0.5)
        input_box.send_keys(Keys.RETURN)
        time.sleep(1.5)

        print("Message sent successfully.")
        return True

    except Exception as e:
        print(f"Failed at URL: {driver.current_url}")
        print(f"Error: {e}")
        return False

    finally:
        # Don't quit — just close the Instagram tab, leave Chrome running
        driver.close()


# Currently not working (for some reason) - needs further testing and debugging
def start_call(target_caller: str):
    link = find_contact(target_caller, field="Линк")

    if link and link != "none":
        try:
            thread_id = link.rstrip("/").split("/")[-1]

            call_url = f"https://www.instagram.com/call/?has_video=false&ig_thread_id={thread_id}"

            print(f"🚀 Opening call link for thread ID: {thread_id}")
            webbrowser.open(call_url)
        except Exception as e:
            print(f"❌ Error processing the link: {e}")
    elif link == "none":
        print(f"⚠️ {target_caller} has no Instagram link associated.")
