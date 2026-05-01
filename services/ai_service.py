import json
import logging
from google import genai
from google.genai import types, errors

logger = logging.getLogger("vision")


class AIService:
    def __init__(self, api_key: str, system_prompt: str):
        self.client = genai.Client(api_key=api_key)
        self.config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            temperature=0.7,
        )
        self.chat_session = self.client.chats.create(
            model="gemini-2.5-flash", config=self.config
        )

    def send_message(self, text: str) -> dict | str | None:
        try:
            response = self.chat_session.send_message(text)
            if not response.parts:
                logger.warning("LLM response was empty or blocked.")
                return None
            return json.loads(response.text)
        except errors.ClientError as e:
            logger.error(f"Gemini API error: {e}")
            return None
        except json.JSONDecodeError:
            logger.warning(
                "Could not parse LLM response as JSON, reading as plain text."
            )
            return response.text
