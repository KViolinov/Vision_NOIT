import sys
import os
import json
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QObject, Signal, Slot, QUrl


# ==========================================
# BRIDGE: JS ↔ PYTHON COMMUNICATION
# ==========================================
class VisionBridge(QObject):
    """Bridge for JS <-> Python communication"""
    sendState = Signal(str)
    sendSpotify = Signal(str, str, bool)
    sendContacts = Signal(str)

    CONTACTS_FILE = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "jarvis_functions", "essential_functions", "contacts.json")
    )

    def __init__(self, ui_instance):
        super().__init__()
        self.ui_instance = ui_instance

    # --- BASIC COMMUNICATION ---
    @Slot()
    def ping(self):
        print("[PY] ✅ Bridge ping received from JS")

    @Slot(str)
    def onMessage(self, msg: str):
        print(f"[JS → PY]: {msg}")

    # ==========================================
    # CONTACTS HANDLING
    # ==========================================
    @Slot(result=str)
    def loadContacts(self):
        """Load contacts from contacts.json (used on page load)."""
        try:
            if not os.path.exists(self.CONTACTS_FILE):
                print(f"[PY] ⚠️ contacts.json not found at: {self.CONTACTS_FILE}")
                return "[]"

            with open(self.CONTACTS_FILE, "r", encoding="utf-8") as f:
                contacts = json.load(f)

            print(f"[PY] ✅ Loaded {len(contacts)} contacts from file.")
            return json.dumps(contacts, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[PY] ❌ Error loading contacts: {e}")
            return "[]"

    @Slot(str, str, str, str, result=bool)
    def addContact(self, name, phone, email, link):
        """Add a new contact to contacts.json"""
        new_contact = {
            "Име": name,
            "Телефон": phone,
            "Имейл": email,
            "Линк": link
        }

        try:
            contacts = json.loads(self.loadContacts())
            contacts.append(new_contact)

            with open(self.CONTACTS_FILE, "w", encoding="utf-8") as f:
                json.dump(contacts, f, ensure_ascii=False, indent=2)

            print(f"[PY] ✅ Added contact: {name}")
            self.sendContacts.emit(json.dumps(contacts, ensure_ascii=False))
            return True
        except Exception as e:
            print(f"[PY] ❌ Error adding contact: {e}")
            return False

    @Slot(str, result=bool)
    def deleteContact(self, name):
        """Delete a contact by name"""
        try:
            contacts = json.loads(self.loadContacts())
            filtered = [c for c in contacts if c.get("Име") != name]

            with open(self.CONTACTS_FILE, "w", encoding="utf-8") as f:
                json.dump(filtered, f, ensure_ascii=False, indent=2)

            print(f"[PY] 🗑 Deleted contact: {name}")
            self.sendContacts.emit(json.dumps(filtered, ensure_ascii=False))
            return True
        except Exception as e:
            print(f"[PY] ❌ Error deleting contact: {e}")
            return False


    # ==========================================
    # GENERAL SETTINGS HANDLING (config.json)
    # ==========================================
    CONFIG_FILE = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "jarvis_functions", "essential_functions", "config.json")
    )

    @Slot(result=str)
    def loadSettings(self):
        """Load general settings from config.json"""
        try:
            if not os.path.exists(self.CONFIG_FILE):
                print(f"[PY] ⚠️ config.json not found: {self.CONFIG_FILE}")
                return "{}"

            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            print(f"[PY] ✅ Loaded settings from config.json")
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[PY] ❌ Error loading config: {e}")
            return "{}"

    @Slot(str, str, str, int, result=bool)
    def saveSettings(self, name, voice, discussion_type, wait_time):
        """Save updated settings into config.json"""
        try:
            if not os.path.exists(self.CONFIG_FILE):
                print(f"[PY] ⚠️ config.json not found — creating new one")
                data = {}
            else:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)

            data["jarvis_name"] = name
            data["jarvis_voice"] = voice
            data["type_discussion"] = discussion_type
            data["wait_interval_seconds"] = wait_time

            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"[PY] 💾 Saved settings to config.json successfully.")
            return True
        except Exception as e:
            print(f"[PY] ❌ Error saving config: {e}")
            return False

    @Slot(result=str)
    def loadApiKeys(self):
        from dotenv import dotenv_values
        data = dotenv_values(".env")

        return json.dumps({
            "GEMINI_KEY": data.get("GEMINI_KEY", ""),
            "ELEVEN_LABS_API": data.get("ELEVEN_LABS_API", ""),
            "SPOTIFY_CLIENT_ID": data.get("SPOTIFY_CLIENT_ID", ""),
            "SPOTIFY_CLIENT_SECRET": data.get("SPOTIFY_CLIENT_SECRET", ""),
            "DEEPSEEK_API_KEY": data.get("DEEPSEEK_API_KEY", "")
        })

    @Slot(str)
    def saveApiKeys(self, json_payload):
        import json
        from dotenv import dotenv_values

        new_data = json.loads(json_payload)
        env = dotenv_values(".env")

        # Update existing keys
        for key, val in new_data.items():
            env[key] = val

        # Rewrite .env
        with open(".env", "w") as f:
            for key, value in env.items():
                if value is None:
                    value = ""
                f.write(f"{key}={value}\n")

        print("API keys updated:", new_data)


# ==========================================
# MAIN UI WINDOW (Single Page + Slide Settings)
# ==========================================
class VisionUI:
    def __init__(self, ui_folder="ui", start_page="index.html"):
        self.ui_folder = ui_folder
        self.start_page = start_page

        # Create Qt app
        self.app = QApplication.instance() or QApplication(sys.argv)

        # Main window
        self.window = QMainWindow()
        self.window.setWindowTitle("VISION Interface MK5")
        self.window.resize(1280, 820)

        # Web view (single page)
        self.view = QWebEngineView()
        self.window.setCentralWidget(self.view)

        # WebChannel bridge
        self.channel = QWebChannel()
        self.bridge = VisionBridge(self)
        self.channel.registerObject("bridge", self.bridge)
        self.view.page().setWebChannel(self.channel)

        # Load index.html
        file_path = os.path.abspath(os.path.join(self.ui_folder, self.start_page))
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"⚠️ index.html not found at {file_path}")
        self.view.load(QUrl.fromLocalFile(file_path))
        print(f"[VisionUI] Loaded {file_path}")

    # --- Basic control methods ---
    def show(self):
        self.window.show()
        print("[VisionUI] Main window shown.")

    def exec(self):
        print("[VisionUI] Starting Qt event loop...")
        self.app.exec()

    # ---- Exposed controls for external modules ----
    def set_state(self, new_state: str):
        """Change visual state of the orb (called from Python backend)."""
        print(f"[VisionUI] Switching to state: {new_state}")
        self.bridge.sendState.emit(new_state)

    def update_spotify(self, song, artist, playing):
        """Update Spotify info on UI."""
        print(f"[VisionUI] Spotify → {song} / {artist} / playing={playing}")
        self.bridge.sendSpotify.emit(song, artist, playing)
