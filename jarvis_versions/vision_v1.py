# vision ver 1.2 for live demo Djon Atanasov - 2025

import os
import math
import pygame
import random
import spotipy
from enum import Enum

import ollama
from openai import OpenAI
import google.generativeai as genai

import speech_recognition as sr
from elevenlabs import play
from elevenlabs.client import ElevenLabs

from dotenv import load_dotenv

from jarvis_functions.shazam_method import recognize_audio
from jarvis_functions.play_spotify import play_song, pause_music
from jarvis_functions.whatsapp_messaging_method import whatsapp_send_message
from jarvis_functions.send_message_instagram.send_message import *
from jarvis_functions.send_message_instagram.input_to_message_ai import *
from jarvis_functions.gemini_vision_method import gemini_vision
from jarvis_functions.take_screenshot import take_screenshot
from jarvis_functions.word_document import openWord
from jarvis_functions.mail_related import send_email, create_appointment, readMail

#from api_keys.api_keys import ELEVEN_LABS_API, GEMINI_KEY, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

load_dotenv()


# Initialize Pygame
pygame.init()
pygame.mixer.init()
client = ElevenLabs(api_key=os.getenv("ELEVEN_LABS_API"))
r = sr.Recognizer()

# Seting up spotify
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri='http://localhost:8888/callback',
    scope='user-library-read user-read-playback-state user-modify-playback-state'))  # Scope for currently playing song


os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_KEY")
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel(model_name="gemini-2.5-flash")

# system_instruction = (
#     "Вие сте Джарвис, полезен и информативен AI асистент. "
#     "Винаги отговаряйте професионално и кратко, но също се дръж приятелски. "
#     "Поддържайте отговорите кратки, но информативни. "
#     "Осигурете, че всички отговори са фактологически точни и лесни за разбиране. "
#     "При представяне на информацията, да се има на предвид и да се адаптира за дете или тинейджър със сериозни зрителни проблеми. "
#     # "Можете да използвате емоционални или звукови тагове като: "
#     # "[laughs], [laughs harder], [starts laughing], [wheezing], "
#     # "[whispers], [sighs], [exhales], [sarcastic], [curious], "
#     # "[excited], [crying], [snorts], [mischievously] за да предадете тон или емоция, но не ги преизползвайте."
# )

system_instruction = (
    "Вие сте Джарвис, полезен и информативен AI асистент. "
    "Винаги отговаряйте професионално и кратко, но също се дръж приятелски. "
    "Поддържайте отговорите кратки, но информативни. "
    "Осигурете, че всички отговори са фактологически точни и лесни за разбиране. "
    "Когато е подходящо, добавяйте стилови маркери за емоция или начин на изразяване, "
    "например [whispers], [laughs], [sarcastically], [cheerfully], [angrily], "
    "за да подскажете на TTS как да чете текста. "
    "Винаги оставяйте маркерите в скоби [] директно в текста."
)



chat = model.start_chat(history=[{"role": "user","parts": [system_instruction],}])

# Screen Dimensions
# info = pygame.display.Info()
# WIDTH, HEIGHT = info.current_w, info.current_h
# screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Jarvis Interface")


class Color(Enum):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 128, 255)
    CYAN = (0, 255, 255)
    ORANGE1 = (255, 165, 0)
    ORANGE2 = (255, 115, 0)
    GREEN1 = (0, 219, 0)
    GREEN2 = (4, 201, 4)
    PINK1 = (255, 182, 193)  # Light Pink
    PINK2 = (255, 105, 180)  # Hot Pink
    PURPLE1 = (166, 0, 255)
    PURPLE2 = (176, 28, 255)

# Visual Config
font_large = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 32)

font_large = pygame.font.Font(pygame.font.get_default_font(), 36)
font_small = pygame.font.Font(pygame.font.get_default_font(), 20)

clock = pygame.time.Clock()

# Rotating Circle Parameters
center = (WIDTH // 2, HEIGHT // 2)
max_radius = min(WIDTH, HEIGHT) // 3
angle = 0
speed = 1

# Particle Parameters
particles = []
num_particles = 100

# Pulse effect variables
pulse_factor = 1
pulse_speed = 0.05
min_size = 3
max_size = 3

# Color Transition
current_color_1 = list(Color.BLUE.value)
current_color_2 = list(Color.CYAN.value)
target_color_1 = list(Color.BLUE.value)
target_color_2 = list(Color.CYAN.value)
color_transition_speed = 10

# Ball initial random positions
random_particles = [{"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT),
                     "dx": random.uniform(-2, 2), "dy": random.uniform(-2, 2)} for _ in range(num_particles)]

jarvis_responses = [
    "Тук съм, как мога да помогна?",
    "Слушам, как мога да Ви асистирам?",
    "Тук съм, как мога да помогна?",
    "С какво мога да Ви бъда полезен?"
    #"Слушам шефе, как да помогна?"
]

selected_songs = [
    "Another one bites the dust - Queen",
    "Back in black",
    "Shoot to Thrill",
    "Thunderstruck",
    "You Give Love a Bad Name",
    "Highway to Hell - AC/DC",
    "September - Earth, Wind & Fire",
    "Should I Stay or Should I Go - Remastered",
    "If You Want Blood(You've Got It) - AC/DC",
    "Welcome Tо The Jungle - Guns N' Roses"
]

status_list = []

jarvis_name = "Джарвис"

voices = ["Brian", "Jessica", "Roger", "Samantha"]
jarvis_voice = voices[0] #deffault voice

model_answering = False
is_collided = False
is_generating = False
wake_word_detected = False

running = True
current_song = ""
current_artist = ""
album_cover = None
current_progress = 0
song_duration = 0

models = ["Gemini", "Llama3", "Deepseek"]
selected_model = models[0]
dropdown_open = False
dropdown_rect = pygame.Rect(20, 120, 150, 30)

def blend_color(current, target, speed):
    """Gradually transitions the current color toward the target color."""
    for i in range(3):
        diff = target[i] - current[i]
        if abs(diff) > speed:
            current[i] += speed if diff > 0 else -speed
        else:
            current[i] = target[i]

def draw_particles(surface, particles, target_mode=False):
    """Draws particles on the surface. If target_mode is True, arrange them in a circle and pulse."""
    global angle, pulse_factor

    for i, particle in enumerate(particles):
        if target_mode:
            # Calculate target circular positions
            target_x = center[0] + math.cos(math.radians(angle + i * 360 / len(particles))) * max_radius
            target_y = center[1] + math.sin(math.radians(angle + i * 360 / len(particles))) * max_radius
            # Smoothly move particles towards their circular positions
            particle["x"] += (target_x - particle["x"]) * 0.05
            particle["y"] += (target_y - particle["y"]) * 0.05

            # Pulse effect
            pulse_factor = min(max_size, pulse_factor + pulse_speed) if pulse_factor < max_size else max(min_size, pulse_factor - pulse_speed)
        else:
            # Move particles randomly when in default mode
            particle["x"] += particle["dx"]
            particle["y"] += particle["dy"]

            # Keep particles within the screen bounds
            if particle["x"] <= 0 or particle["x"] >= WIDTH:
                particle["dx"] *= -1
            if particle["y"] <= 0 or particle["y"] >= HEIGHT:
                particle["dy"] *= -1

        # Draw the particle
        pygame.draw.circle(surface, tuple(current_color_2), (int(particle["x"]), int(particle["y"])), int(pulse_factor))

def draw_response(model):
    """Update settings when the model is answering."""
    global target_color_1, target_color_2, is_collided, angle, speed

    if model == "Gemini":
        target_color_1 = list(Color.GREEN1.value)
        target_color_2 = list(Color.GREEN2.value)
    elif model == "Llama3":
        target_color_1 = list(Color.PINK1.value)
        target_color_2 = list(Color.PINK2.value)
    elif model == "Deepseek":
        target_color_1 = list(Color.PURPLE1.value)
        target_color_2 = list(Color.PURPLE2.value)

    speed = 1
    is_collided = True
    angle += speed

def draw_thinking():
    """Update settings when the model is listening."""
    global target_color_1, target_color_2, is_collided, angle, speed
    target_color_1 = list(Color.ORANGE1.value)
    target_color_2 = list(Color.ORANGE1.value)
    speed = 0.5
    is_collided = True
    angle += speed

def draw_default():
    """Update settings when the model is not answering."""
    global target_color_1, target_color_2, is_collided, speed
    target_color_1 = list(Color.BLUE.value)
    target_color_2 = list(Color.CYAN.value)
    speed = 1
    is_collided = False

def draw_text(surface, text, position, font, color):
    """Draws text onto the surface."""
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

def fetch_current_track():
    """Fetch the current playing track and its album cover."""
    try:
        current_track = sp.currently_playing()
        if current_track and current_track['is_playing']:
            song = current_track['item']['name']
            artist = ", ".join([a['name'] for a in current_track['item']['artists']])
            album_cover_url = current_track['item']['album']['images'][0]['url']
            progress_ms = current_track['progress_ms']  # Progress in milliseconds
            duration_ms = current_track['item']['duration_ms']  # Duration in milliseconds
            return song, artist, album_cover_url, progress_ms, duration_ms
        return None, None, None, 0, 0
    except Exception as e:
        print(f"Error fetching track: {e}")
        return None, None, None, 0, 0

def draw_progress_bar(surface, x, y, width, height, progress, max_progress):
    """Draw a progress bar to represent the song timeline."""
    # Check if max_progress is non-zero to avoid division by zero
    if max_progress > 0:
        # Calculate the progress ratio
        progress_ratio = progress / max_progress
        progress_width = int(width * progress_ratio)
    else:
        progress_width = 0  # If duration is zero, show no progress

    # Draw the empty progress bar (background)
    pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height))

    # Draw the filled progress bar (foreground)
    pygame.draw.rect(surface, Color.GREEN1.value, (x, y, progress_width, height))

def update_status(new_status):
    # Add new status to the list
    status_list.append(new_status)

    # Ensure the list only has 5 elements
    if len(status_list) > 5:
        status_list.pop(0)  # Remove the oldest status (first element)

def draw_dropdown(surface, x, y, w, h, font, options, selected, is_open):
    # Draw main box
    pygame.draw.rect(surface, Color.WHITE.value, (x, y, w, h), border_radius=5)
    text_surface = font.render(selected, True, Color.BLACK.value)
    surface.blit(text_surface, (x + 5, y + (h - text_surface.get_height()) // 2))

    # Draw arrow
    pygame.draw.polygon(surface, Color.BLACK.value, [
        (x + w - 20, y + h // 3),
        (x + w - 10, y + h // 3),
        (x + w - 15, y + 2 * h // 3)
    ])

    # Draw expanded options if open
    if is_open:
        for i, option in enumerate(options):
            rect = pygame.Rect(x, y + (i + 1) * h, w, h)
            pygame.draw.rect(surface, Color.WHITE.value, rect, border_radius=5)
            option_surface = font.render(option, True, Color.BLACK.value)
            surface.blit(option_surface, (x + 5, y + (h - option_surface.get_height()) // 2 + (i + 1) * h))

def record_text():
    """Listen for speech and return the recognized text."""
    try:
        with sr.Microphone() as source:
            #print("Listening...")
            r.adjust_for_ambient_noise(source, duration=0.2)
            audio = r.listen(source)

            # Recognize speech using Google API
            MyText = r.recognize_google(audio, language="bg-BG")
            print(f"You said: {MyText}")
            return MyText.lower()

    except sr.RequestError as e:
        print(f"API Request Error: {e}")
        return None
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that. Please try again.")
        return None

def chatbot():
    global wake_word_detected, model_answering, is_generating, jarvis_voice, jarvis_name, selected_model

    print("Welcome to Vision! Say any of the models name to activate. Say 'exit' to quit.")

    while True:
        if not wake_word_detected:
            # Listen for the wake word
            print("Waiting for wake word...")
            user_input = record_text()

            if user_input:
                should_wake = False
                user_input_lower = user_input.lower()

                if jarvis_name == "Джарвис":
                    if any(word in user_input_lower for word in ["джарвис", "джарви", "джервис", "jarvis", "черви"]):
                        should_wake = True
                else:
                    if jarvis_name.lower() in user_input_lower:
                        should_wake = True

                if should_wake:
                    wake_word_detected = True
                    pygame.mixer.music.load("../sound_files/beep.flac")
                    pygame.mixer.music.play()

                    print("✅ Wake word detected!")
                    model_answering = True
                    is_generating = False

                    response = random.choice(jarvis_responses)
                    audio = client.generate(text=response, voice=jarvis_voice)
                    play(audio)

                    model_answering = False
                    is_generating = True
                    continue


            elif user_input == "излез":
                print("Goodbye!")
                audio = client.generate(text="Goodbye!", voice=jarvis_voice)
                play(audio)
                break

        else:
            # Actively listen for commands
            print("Listening for commands...")
            user_input = record_text()

            #show_live_caption_text(user_input)

            if user_input is None:
                print("Error: No input detected.")
                continue

            if "представи се" in user_input or "представиш" in user_input or "представи" in user_input:
                audio = client.generate(text="Здравейте, аз съм Джарвис, акроним от (Just A Rather Very Intelligent System), аз съм езиков модел на Gemini обучен от Google."
                                             "Вдъхновен съм от легендарния изкуствен интелект на Тони Старк – Джарвис от Железния човек."
                                             "Моята мисия е да помогна на децата със зрителни и други проблеми да им помогне с работата им с компютри и за по-доброто им усвояване на учебния материал."
                                             "Ако искате да ме попитате нещо, просто ме повикайте по име.", voice="Brian")
                play(audio)
                model_answering = False
                is_generating = False
                wake_word_detected = False
                continue

            if "можеш" in user_input and "правиш" in user_input:
                audio = client.generate(text="Мога да търся информация в интернет, да я обобщавам и да ви я представям. "
                                             "Също така, мога да изпращам и чета имейли, да пускам музика, да отварям нови документи в Word "
                                             "И дори да ви опиша това, което виждам като изпозлвам Gemini Vision и OCR модел за разпознаване на текст.",
                                        voice="Brian")
                play(audio)
                model_answering = False
                is_generating = False
                continue


            if "смениш" in user_input and "глас" in user_input:
                model_answering = True
                is_generating = False

                audios = [
                    client.generate(text="Разбира се, с кой глас бихте желали да говоря? "
                                         "Имам следните гласове на разположение: Брайън", voice=jarvis_voice),
                    client.generate(text="Джесика", voice=voices[1]),
                    client.generate(text="Роджър", voice=voices[2]),
                    client.generate(text="и Саманта. Кой глас бихте предпочели?", voice=voices[3])
                ]

                for audio in audios:
                    play(audio)

                print("Listening for voice choice...")
                user_input = record_text()

                if "брайън" in user_input or "brian" in user_input:
                    jarvis_voice = voices[0]
                elif "джесика" in user_input or "jessica" in user_input:
                    jarvis_voice = voices[1]
                elif "роджър" in user_input or "roger" in user_input:
                    jarvis_voice = voices[2]
                elif "саманта" in user_input or "samantha" in user_input:
                    jarvis_voice = voices[3]

                audio = client.generate(text=f"Супер, смених гласа на {jarvis_voice}", voice=jarvis_voice)
                play(audio)

                model_answering = False
                is_generating = False
                wake_word_detected = False
                continue

            if "смениш" in user_input and "име" in user_input:
                model_answering = True
                is_generating = False

                audio = client.generate(text="Разбира се, как бихте желали да се казвам?", voice=jarvis_voice)
                play(audio)

                print("Listening for name choice...")
                user_input = record_text()

                if user_input is None:
                    audio = client.generate(text="Нe можах да разбера. Може ли да повторите?", voice=jarvis_voice)
                    play(audio)
                    user_input = record_text()

                audio = client.generate(text=f"Супер, от сега нататък можете да ме наричате {user_input}", voice=jarvis_voice)
                play(audio)

                jarvis_name = user_input

                model_answering = False
                is_generating = False
                wake_word_detected = False
                continue

            if "смениш" in user_input and "модел" in user_input:
                model_answering = True
                is_generating = False

                audio = client.generate(text="Разбира се, кой модел желаете да използвате?"
                                             "Разполагам с Gemini(който в момента го използвате), Llama 3 и DeepSeek", voice=jarvis_voice)
                play(audio)

                print("Listening for model choice...")
                user_input = record_text()

                if user_input is None:
                    audio = client.generate(text="Нe можах да разбера. Може ли да повторите?", voice=jarvis_voice)
                    play(audio)
                    user_input = record_text()

                audio = client.generate(text=f"Супер, избрахте {user_input} за модел",
                                        voice=jarvis_voice)
                play(audio)

                selected_model = user_input

                model_answering = False
                is_generating = False
                wake_word_detected = False
                continue


            if ("пусни" in user_input or "пуснеш" in user_input) and ("песен" in user_input or "музика" in user_input):
                model_answering = True
                is_generating = False

                audio = client.generate(text="Разбира се, имате ли някакви предпочитания за песен?", voice=jarvis_voice)
                play(audio)

                model_answering = False
                is_generating = True

                print("Listening for song info...")
                user_input = record_text()

                if user_input is None:
                    audio = client.generate(text="Нo можах да разбера. Може ли да повторите?", voice=jarvis_voice)
                    play(audio)
                    user_input = record_text()

                if "да" in user_input:
                    model_answering = True
                    is_generating = False

                    audio = client.generate(text="Добре, коя песен бихте желали да ви пусна?",
                                            voice=jarvis_voice)
                    play(audio)

                    print("Listening for specific song...")
                    user_song = record_text()

                    song_from_ai = chat.send_message({
                        "parts": (
                                "Твоята цел е да предложиш песен според това, което user-a е казал. "
                                "Ако user-a споменава конкретен изпълнител, предложи песен **само от този изпълнител**. "
                                "Отговори само с името на песента и изпълнителя, без нищо друго. "
                                "- " + user_song
                        )
                    })

                    audio = client.generate(text=f"Пускам, {song_from_ai.text}",
                                            voice=jarvis_voice)
                    play(audio)

                    play_song(song_from_ai.text)

                    print(f"Playing track: {song_from_ai.text}")
                    update_status(f"Played {song_from_ai.text}")

                    print("Playback started on LAPTOP_KOSI.")

                elif "не" in user_input or "изненадай ме" in user_input or "изненадай" in user_input:
                    model_answering = True
                    is_generating = False

                    audio = client.generate(text="Пускам тогава от избрания от вас списък с песни?",
                                            voice=jarvis_voice)
                    play(audio)

                    track_name = random.choice(selected_songs)
                    play_song(track_name)

                    print(f"Playing track: {track_name}")
                    update_status(f"Played {track_name}")

                    print("Playback started on LAPTOP_KOSI.")

                model_answering = False
                is_generating = False
                wake_word_detected = False
                continue

            if "спри" in user_input and ("песента" in user_input or "музиката" in user_input):
                pause_music()
                model_answering = False
                is_generating = False
                wake_word_detected = False
                continue


            if "пратиш" in user_input and ("имейл" in user_input or "писмо" in user_input):
                model_answering = True
                is_generating = False

                message = send_email()

                update_status(f"Sent an email to {message}")

                model_answering = False
                is_generating = False
                wake_word_detected = False
                continue

            if "прочетеш" in user_input and ("писма" in user_input or "имейли" in user_input or "пис" in user_input):

                readMail(jarvis_voice)

                update_status(f"Прочете последните 3 имейла")
                model_answering = False
                is_generating = False
                wake_word_detected = False
                continue

            if (("събитие" in user_input or "събити" in user_input or "събития" in user_input)
                    and ("създадеш" in user_input or "Създадеш" in user_input or "създай" in user_input or "Създай" in user_input)):

                create_appointment(jarvis_voice)

                update_status(f"Made an event in the calendar")
                model_answering = False
                is_generating = False
                wake_word_detected = False
                continue

                # Направи ми събитие за 3 следобяд днес, което да продължи 1 час, и да се казва "нахрани котката"pip install pywin32


            if ("съобщение" in user_input or "съобщения" in user_input) and "пратиш" in user_input: # currently not working, needs testing
                # whatsapp_send_message()
                generate_message(user_input)

                update_status("Изпрати съобщение")
                model_answering = False
                is_generating = False
                wake_word_detected = False
                continue

            if ("виждаш" in user_input or "вижда" in user_input) and "какво" in user_input:
                gemini_vision()

                update_status(f"Използва Gemini Vision за камерата")
                model_answering = False
                is_generating = False
                wake_word_detected = False
                continue

            if ("има" in user_input or "виж" in user_input) and ("екрана" in user_input or "екрa" in user_input):
                take_screenshot()

                # text_from_screenshot = take_screenshot()

                # audio = client.generate(text=text_from_screenshot, voice=jarvis_voice)
                # play(audio)

                update_status("Използва Gemini Vision за скрийншот")
                model_answering = False
                is_generating = False
                wake_word_detected = False
                continue

            if ("разпознаеш" in user_input or "коя" in user_input) and "песен" in user_input:
                audio = client.generate(text="Разбира се, започвам да слушам. Ако разпозная песента ще ви кажа името и автора на песента",
                                        voice=jarvis_voice)
                play(audio)

                title, artist = recognize_audio()  # Get the title and artist
                if title and artist:
                    audio = client.generate(
                        text=f"Намерих песента, песента е {title}, а автора е {artist}. Желаете ли да пусна песента в spotify?",
                        voice=jarvis_voice)
                    play(audio)
                    print(f"Song Title: {title}")
                    print(f"Artist: {artist}")

                    print("Listening for song info...")
                    answer_info = record_text()

                    if "да" in answer_info:
                        audio = client.generate(text=f"Пускам, {title} на {artist}",
                                                voice=jarvis_voice)
                        play(audio)
                        play_song(title)

                    elif "не" in answer_info:
                        model_answering = False
                        is_generating = False
                        wake_word_detected = False
                        continue
                else:
                    print("No song found")

                update_status(f"Използва Shazam и отрки {title}")
                model_answering = False
                is_generating = False
                wake_word_detected = False
                continue

            if (("отвори" in user_input or "отвориш" in user_input or "отвориш" in user_input ) # currently not working
                    and ("word" in user_input or "wor" in user_input or "документ" in user_input)):

                openWord(jarvis_voice)

                update_status(f"Made a Word document")
                model_answering = False
                is_generating = False
                wake_word_detected = False
                continue


            if user_input:

                is_generating = True

                if (selected_model == "Gemini"):
                    result = chat.send_message({"parts": [user_input]})

                elif(selected_model == "Llama3"):
                    result = ollama.chat(
                        model="tinyllama",
                        messages=[{"role": "user", "content": user_input}]
                    )

                elif(selected_model == "Deepseek"): # currently not working
                    deepseek_client = OpenAI(
                        api_key="sk-b137c86b799b4260854985c40021ce7e",
                        base_url="https://api.deepseek.com"
                    )

                    result = deepseek_client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_input}
                        ],
                        temperature=0.7,
                        max_tokens=1000
                    )

                is_generating = False
                model_answering = True

                if (selected_model == "Gemini"):
                    print(f"Jarvis ({selected_model}): {result.text}")

                    audio = client.generate(text=result.text, voice=jarvis_voice)
                    play(audio)


                elif (selected_model == "Llama3"):
                    print(f"Jarvis ({selected_model}): {result['message']['content']}")
                    audio = client.generate(text=result['message']['content'], voice=jarvis_voice)
                    play(audio)

                elif(selected_model == "Deepseek"):
                    print(f"Jarvis ({selected_model}): {result.choices[0].message.content}")
                    audio = client.generate(text=result.choices[0].message.content, voice=jarvis_voice)
                    play(audio)

                model_answering = False
                is_generating = False

            wake_word_detected = False

# Main Loop
running = True
chatbot_thread = None

# Run chatbot in a separate thread
import threading
chatbot_thread = threading.Thread(target=chatbot)
chatbot_thread.start()

while running:
    screen.fill(Color.BLACK.value)

    # Event Handling
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if dropdown_rect.collidepoint(mouse_pos):
                dropdown_open = not dropdown_open
            elif dropdown_open:
                for i, option in enumerate(models):
                    option_rect = pygame.Rect(
                        dropdown_rect.x,
                        dropdown_rect.y + (i + 1) * dropdown_rect.height,
                        dropdown_rect.width,
                        dropdown_rect.height
                    )
                    if option_rect.collidepoint(mouse_pos):
                        selected_model = option
                        print(f"✅ Selected model: {selected_model}")
                        dropdown_open = False

    # Toggle behavior based on whether the model is generating or answering
    if is_generating:
        draw_thinking()  # Show thinking state
    elif model_answering:
        draw_response(selected_model)  # Show answering state
    else:
        draw_default()  # Default state when nothing is happening.

    # Smooth Color Transition
    blend_color(current_color_1, target_color_1, color_transition_speed)
    blend_color(current_color_2, target_color_2, color_transition_speed)

    # Draw Particles
    draw_particles(screen, random_particles, target_mode=is_collided)

    # Draw Text
    draw_text(screen, "Vision Interface MK4", (10, 10), font_large, Color.WHITE.value)
    draw_text(screen, "System Status: All Systems Online", (10, 60), font_small, tuple(current_color_2))

    # Draw the list of statuses under "System Status"
    start_y = 90  # Starting position for the list of items
    line_height = 30  # Space between each list item
    for index, status in enumerate(status_list):
        draw_text(screen, status, (10, start_y + index * line_height), font_small, Color.WHITE.value)

    # Draw dropdown
    draw_dropdown(screen, dropdown_rect.x, dropdown_rect.y, dropdown_rect.width, dropdown_rect.height,
                  font_small, models, selected_model, dropdown_open)

    # Fetch current track periodically (e.g., every 3 seconds)
    if pygame.time.get_ticks() % 3000 < 50:  # Update every 3 seconds
        song, artist, album_cover_url, progress_ms, duration_ms = fetch_current_track()
        if song and artist:  # Only update if song and artist are available
            current_song = song
            current_artist = artist
            current_progress = progress_ms
            song_duration = duration_ms

    # Draw the progress bar for the song timeline
    progress_bar_x = (WIDTH - 700) // 2
    progress_bar_y = HEIGHT - 30
    draw_progress_bar(screen, progress_bar_x, progress_bar_y, 700, 10, current_progress, song_duration)

    # Draw song information above the progress bar
    if current_song:
        song_surface = font_small.render(current_song, True, Color.WHITE.value)
        song_text_x = (WIDTH - song_surface.get_width()) // 2
        song_text_y = progress_bar_y - 30
        screen.blit(song_surface, (song_text_x, song_text_y))

    # Update Display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# TODO: To make Live Caption