import time
from jarvis_functions.essential_functions.mic_state import is_muted

import os, speech_recognition as sr

r = sr.Recognizer()
sr.FLAC_CONVERTER = os.path.join(
    os.path.dirname(__file__), "important_files", "flac.exe"
)

MUTED_SIGNAL = "__MIC_MUTED__"


def record_text(timeout=None):
    if is_muted():
        time.sleep(0.15)  # prevent busy loop
        return MUTED_SIGNAL

    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.3)

            listen_timeout = timeout if timeout is not None else 5
            phrase_limit = min(listen_timeout, 8) if timeout else 8

            audio = r.listen(
                source, timeout=listen_timeout, phrase_time_limit=phrase_limit
            )

        try:
            text = r.recognize_google(audio, language="bg-BG")
            print("🗣 You said:", text)
            return text.lower()

        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"⚠️ API error: {e}")
            return None

    except sr.WaitTimeoutError:
        return None
    except Exception as e:
        print(f"❌ Mic error: {e}")
        return None
