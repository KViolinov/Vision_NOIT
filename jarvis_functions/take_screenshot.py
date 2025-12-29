import os
import io
from PIL import ImageGrab
import google.generativeai as genai

from jarvis_functions.essential_functions.enhanced_elevenlabs import (
    generate_audio_from_text,
)

from account.check_account import require_login

from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_KEY")
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-2.5-flash")


@require_login
def take_screenshot():
    screenshot = ImageGrab.grab()

    # Save to memory buffer as PNG
    buffer = io.BytesIO()
    screenshot.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()

    response = model.generate_content(
        [
            "Опиши този скрийншот подробно с 5-10 изречения:",
            {"mime_type": "image/png", "data": image_bytes},
        ]
    )

    generate_audio_from_text(text=response.text, voice="Brian")
