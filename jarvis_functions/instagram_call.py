from jarvis_functions.essential_functions.contact_locator import find_contact
import webbrowser


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
