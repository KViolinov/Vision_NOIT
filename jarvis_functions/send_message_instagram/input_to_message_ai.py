import google.generativeai as genai
from jarvis_functions.send_message_instagram.send_message import *

import os
from dotenv import load_dotenv
load_dotenv()

def generate_message(text: str):
    genai.configure(api_key=os.getenv("GEMINI_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = (
        "Ще ти дам текст, който трябва да бъде изпратен на потребител в Instagram. "
        "Искам да извлечеш само името на човека, на когото е адресирано, като отделна дума. "
        "На нов ред преформулирай това, което искам да изпратя като съобщение. "
        "Дай само един вариант на съобщението, без допълнителни обяснения, и нека съобщението да е човешко и кратко. "
        "Без здравей, без излишни думи, просто съобщението. "
        f"Текстът е: {text}"
    )

    response = model.generate_content(prompt)

    full_text = response.candidates[0].content.parts[0].text.strip()
    print(full_text)

    lines = [line.strip() for line in full_text.split("\n") if line.strip()]

    if len(lines) >= 2:
        name = lines[0]
        message = lines[1]
    else:
        name = ""
        message = full_text

    print(f"Extracted name: {name}")
    print(f"Generated message: {message}")

    send_message_to_instagram_user(name, message)