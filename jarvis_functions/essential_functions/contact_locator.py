import os
import json

# Path to the contacts.json file
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
CONTACTS_FILE = os.path.join(
    ROOT_DIR, "jarvis_functions", "essential_functions", "contacts.json"
)


def find_contact(query: str, field: str = None) -> str | dict | None:
    """
    Searches contacts.json for a contact and returns either the whole dict or a specific field.
    """

    if not os.path.exists(CONTACTS_FILE):
        print(f"⚠️ File not found: {CONTACTS_FILE}")
        return None

    # Load JSON list
    with open(CONTACTS_FILE, "r", encoding="utf-8") as file:
        contacts = json.load(file)

    # Search
    for contact in contacts:
        name = contact.get("Име", "")

        if query.lower() in name.lower():
            # full contact requested
            if field is None:
                return contact

            # specific field requested
            field = field.capitalize()  # normalize ("име" -> "Име")
            if field in contact:
                return contact[field]

            print(f"⚠️ Полето '{field}' не е намерено за {name}.")
            return None

    print(f"⚠️ Контакт с '{query}' не е намерен.")
    return None
