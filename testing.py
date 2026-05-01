from functions.communication.contact_locator import find_contact

# from jarvis_functions.send_message_instagram.input_to_message_ai import *
#
# text = "Искам да пратиш съобщение на Мерт, че е тъп турчин и ще му избием зъбите"
# #text = "Искам да пратиш съобщение към Вероника, и я питай какво прави"
#
# generate_message(text)


# import requests

# home_server_url = " https://localmodelvision.test/chat"


# while True:

#     user_input = input("You: ")
#     try:
#         r = requests.post(home_server_url, json={"prompt": user_input})
#         r.raise_for_status()  # raises HTTPError if status != 200
#         print(r.json())
#     except requests.RequestException as e:
#         print("Request failed:", e)
#         print({"error": str(e)})
#     except ValueError as e:  # JSON decoding error
#         print("Failed to parse response:", e, r.text)
#         print({"error": "Invalid JSON from server"})


# from functions.send_message_instagram.message_composer import generate_message

# generate_message(
#     "Искам да пратиш съобщение на Тати, и да го питаш кога ще сложим телевзора в градината"
# )


# from functions.whatsapp import start_whatsapp_call

# start_whatsapp_call("Тати")

# import asyncio
# from telethon import TelegramClient

# api_id = "30287443"
# api_hash = "6a51372d42a23682aeca9f21703f35ff"

# client = TelegramClient("jarvis_session", api_id, api_hash)


# # 1. Define the function as 'async'
# async def send_telegram_message(contact: str, message: str):
#     # 2. 'await' the async call
#     await client.send_message(contact, message)
#     print(f"Message sent to {contact}")


# # 3. Use the client context manager to run the async function
# if __name__ == "__main__":
#     with client:
#         client.loop.run_until_complete(
#             send_telegram_message("+359 878728225", "Здрасти, как си?")
#         )


from functions.communication.phone_call import initiate_call

initiate_call("Обади се на Тати")
