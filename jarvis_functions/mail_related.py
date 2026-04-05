import os
import json
import dotenv
import win32com.client as win32
import google.generativeai as genai

from jarvis_functions.essential_functions.voice_input import record_text
from jarvis_functions.essential_functions.enhanced_elevenlabs import (
    generate_audio_from_text,
)

from jarvis_functions.essential_functions.config import get_jarvis_voice
from jarvis_functions.essential_functions.contact_locator import find_contact

jarvis_voice = get_jarvis_voice()


# Helper functions
def send_email_function(subject, body, to_email):
    outlook = win32.Dispatch("outlook.application")
    mail = outlook.CreateItem(0)  # 0 = MailItem
    mail.Subject = subject
    mail.Body = body
    mail.To = to_email
    mail.Send()
    return True


def create_outlook_appointment(subject, start_time, duration_minutes: int):
    outlook = win32.Dispatch("Outlook.Application")
    appt = outlook.CreateItem(1)  # AppointmentItem

    appt.Subject = subject
    appt.Start = start_time
    appt.Duration = duration_minutes
    appt.ReminderMinutesBeforeStart = 15
    appt.BusyStatus = 2  # 2 = Busy
    appt.Save()

    print(f"✅ Appointment '{subject}' created at {start_time}")


def get_time(user_input):
    # Configure
    api_key = os.getenv("GEMINI_KEY")
    os.environ["GEMINI_API_KEY"] = api_key
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=(
            "Потребителят ще ти даде текст за създаване на събитие в Outlook календар.\n"
            "ЗАДЪЛЖИТЕЛНО върни само JSON със следната структура:\n"
            "{\n"
            '  "subject": "...",\n'
            '  "date": "YYYY-MM-DD",\n'
            '  "time": "HH:MM",\n'
            '  "duration_minutes": 60\n'
            "}\n"
            "Не добавяй нищо извън JSON. Не обяснявай. Само чист JSON."
        ),
    )

    # Send message
    response = model.generate_content(user_input)

    # Try parsing JSON
    try:
        data = json.loads(response.text)
        return data
    except json.JSONDecodeError:
        print("❌ Model did not return valid JSON:")
        print(response.text)
        return None


def send_email() -> str:
    generate_audio_from_text(
        text="Разбира се, към кого бихте желали да пратите имейла?",
        voice=get_jarvis_voice(),
    )

    print("Listening for email info...")
    user_input = record_text()

    to_email = find_contact(user_input, "имейл")

    generate_audio_from_text(
        text="Каква ще е темата на вашето писмо?", voice=get_jarvis_voice()
    )

    print("Listening for email info...")
    subject = record_text()

    generate_audio_from_text(
        text="Какво искате да изпратите?", voice=get_jarvis_voice()
    )

    print("Listening for email info...")
    body = record_text()

    generate_audio_from_text(
        text="Супер, преди да изпратя имейла, ще ви кажа какво съм си записал",
        voice=jarvis_voice,
    )

    generate_audio_from_text(text=f"Имейла е към {to_email}", voice=get_jarvis_voice())
    generate_audio_from_text(
        text="Темата на писмото е " + subject + "И съдържанието на писмото е " + body,
        voice=jarvis_voice,
    )

    generate_audio_from_text(
        text="Всичко наред ли е с информацията в писмото?", voice=jarvis_voice
    )

    print("Listening for approval...")
    user_input = record_text()

    if "да" in user_input:
        generate_audio_from_text(text="✅ Супер, пращам имейла", voice=jarvis_voice)

        send_email_function(subject=subject, body=body, to_email=to_email)

    elif "не" in user_input:
        generate_audio_from_text(text="Сорка", voice=jarvis_voice)

        return "Имаше проблем с информацията в имейла"

    return "Имейлът е изпратен успешно."


# def create_appointment():
#     # 1) Ask for subject
#     generate_audio_from_text(
#         text="Разбира се, как искате да се казва събитието?",
#         voice=jarvis_voice
#     )
#     print("Listening for appointment info...")
#     appointment_name = record_text()
#
#     # 2) Ask for time
#     generate_audio_from_text(
#         text="За кога да бъде това събитие?",
#         voice=jarvis_voice
#     )
#     print("Listening for appointment info...")
#     appointment_time = record_text()
#
#     # 3) Ask for duration
#     generate_audio_from_text(
#         text="Колко време ще продължи това събитие?",
#         voice=jarvis_voice
#     )
#     print("Listening for appointment info...")
#     appointment_duration = record_text()
#
#     # -----------------------------------------
#     # FIX: parse natural language time
#     # -----------------------------------------
#     try:
#         event_time = parse_natural_time(appointment_time)
#     except Exception as e:
#         generate_audio_from_text(
#             text="Съжалявам, но не можах да разбера часа.",
#             voice=jarvis_voice
#         )
#         return "Грешка при разпознаване на часа"
#
#     print(f"Parsed event time: {event_time}")
#
#     # -----------------------------------------
#     # FIX: parse the duration (convert text → minutes)
#     # -----------------------------------------
#     duration_minutes = parse_duration_to_minutes(appointment_duration)
#
#     if duration_minutes is None:
#         duration_minutes = 60  # default fallback
#
#     # -----------------------------------------
#     # Confirm with user
#     # -----------------------------------------
#     generate_audio_from_text(
#         text=f"Супер, запазвам събитие {appointment_name}, "
#              f"в {event_time.strftime('%H:%M %d-%m-%Y')}, "
#              f"и ще трае {duration_minutes} минути.",
#         voice=jarvis_voice
#     )
#
#     # Create in Outlook
#     create_outlook_appointment(
#         subject=appointment_name,
#         start_time=event_time,
#         duration_minutes=duration_minutes
#     )
#
#     return "Събитието е създадено успешно."


def readMail():
    # Initialize Outlook
    outlook = win32.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)  # 6 = Inbox

    # Get all messages sorted by received time (newest first)
    messages = inbox.Items
    messages.Sort("[ReceivedTime]", True)  # Sort descending (newest first)

    # Retrieve the last 5 emails
    num_emails = 3  # Change this number if you need more
    latest_messages = [messages.GetNext() for _ in range(num_emails)]

    generate_audio_from_text(
        text="Ето последните 3 имейла в пощата ви: ", voice=jarvis_voice
    )
    # Print email details
    for i, email in enumerate(latest_messages, start=1):
        print(f"\n📧 Email {i}:")
        print(f"Subject: {email.Subject}")
        print(f"From: {email.SenderName}")
        print(f"Received: {email.ReceivedTime}")
        print("\n--- Email Body ---\n")
        print(email.Body)  # Full email body
        print("\n--- End of Email ---\n")
        generate_audio_from_text(
            text=f"Имейл номер {i}, изпратено е от {email.SenderName}, "
            f"темата е {email.Subject}, а съдържанието на писмото е {email.Body}",
            voice=jarvis_voice,
        )

    return "Четенето на имейли е завършено."
