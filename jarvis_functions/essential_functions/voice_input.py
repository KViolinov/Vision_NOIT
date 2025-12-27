import os, speech_recognition as sr

r = sr.Recognizer()
sr.FLAC_CONVERTER = os.path.join(os.path.dirname(__file__), "important_files", "flac.exe")

def record_text(timeout=None):
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.3)

            # Use the passed timeout value if provided
            listen_timeout = timeout if timeout is not None else 5
            phrase_limit = min(listen_timeout, 8) if timeout else 8

            audio = r.listen(source, timeout=listen_timeout, phrase_time_limit=phrase_limit)

        try:
            text = r.recognize_google(audio, language="bg-BG")
            print("🗣 You said:", text)
            return text.lower()
        except sr.UnknownValueError:
            print("❌ Could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"⚠️ API error: {e}")
            return None

    except sr.WaitTimeoutError:
        print("⚠️ Timeout: no speech detected.")
        return None
    except Exception as e:
        print(f"❌ Mic error: {e}")
        return None
