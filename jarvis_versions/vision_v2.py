import os
import re
import math
import json
import inspect
import pygame
import random
import spotipy
from enum import Enum

import google.generativeai as genai

from dotenv import load_dotenv

from jarvis_functions.essential_functions.enhanced_elevenlabs import generate_audio_from_text
from jarvis_functions.essential_functions.voice_input import record_text
from jarvis_functions.shazam_method import recognize_audio
from jarvis_functions.word_document import openWord
from jarvis_functions.whatsapp_messaging_method import whatsapp_send_message
from jarvis_functions.take_screenshot import take_screenshot
from jarvis_functions.play_spotify import play_song, play_music, pause_music
from jarvis_functions.mail_related import readMail, create_appointment, send_email
from jarvis_functions.gemini_vision_method import gemini_vision
from jarvis_functions.call_phone_method import call_phone
from jarvis_functions.send_message_instagram.input_to_message_ai import generate_message




load_dotenv()

# Initialize Pygame
pygame.init()
pygame.mixer.init()

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

system_instructions = (
    "Вие сте Джарвис, полезен и информативен AI асистент/агент. "
    "Винаги отговаряйте професионално и кратко, но също се дръж приятелски. "
    "Поддържайте отговорите кратки, но информативни. "
    "Осигурете, че всички отговори са фактологически точни и лесни за разбиране. "
    "Твоята работа е следната: При получаване на команда от потребителя, "
    "ти трябва да определиш дали е команда или просто въпрос."

    "Ако е въпрос, отговори на него кратко и информативно. "
    "Когато е подходящо, добавяйте стилови маркери за емоция или начин на изразяване, "
    "например [whispers], [laughs], [sarcastically], [cheerfully], [angrily], "
    "за да подскажете на TTS как да чете текста. "
    "Винаги оставяйте маркерите в скоби [] директно в текста."

    "Обаче ако е команда, трябва да напишеш 'command'."
    "След това на нов ред, трябва да напишеш името на функцията, която трябва да се извика (като събереш подходящата информация), "
    "като имаш предвид следните функции, които можеш да използваш: "

    "1. generate_message(user_input) - Изпраща съобщение в Instagram на посочения получател. Фунцията изисква параметър user_input от тип str, от тебе просто се иска да сложиш като параметър оригиналния текст на user-a. " # -
    "2. gemini_vision() - Използва Gemini Vision модел който разпознава какво има на уеб камерата. Функцията не изисква параметри." # -
    "3. take_screenshot() - Използва Gemini Vision модел който разпознава какво има на екрана. Функцията не изисква параметри. " # -
    "4. play_song(user_input) - Пуска песен в Spotify. Функцията изисква параметър user_input от тип str, който съдържа името на песента." # - 
    "5. pause_music() - Пауза на текущата песен в Spotify. Функцията не изисква параметри." # - 
    "6. change_jarvis_voice() - Променя гласа на Джарвис. Функцията не изисква параметри." # needs some work
    "7. change_jarvis_name() - Променя името на Джарвис. Функцията не изисква параметри." # needs some work
    "8. readMail() - Чете последните имейли от Outlook. Функцията не изисква параметри."
    "9. create_appointment() - Създава ново събитие в календара на Outlook. Функцията не изисква параметри."
    "10. send_email() - Изпраща имейл чрез Outlook. Функцията не изисква параметри." # -
    "11. openWord() - Отваря Microsoft Word и създава нов документ. Функцията не изисква параметри." # -
    "12. recognize_audio() - Разпознава песен чрез слушане на микрофона. Функцията не изисква параметри." # -

    "Винаги връщай отговора в JSON формат, като използваш следната структура: "
    "{'response_type': 'command', 'function': 'function_name', 'parameters': {'param1': 'value1', 'param2': 'value2'}}"
    "или ако е въпрос: ""{'response_type': 'answer', 'answer': 'your answer here'}"
)

chat = model.start_chat(history=[{"role": "user", "parts": [system_instructions], }])

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
    # "Слушам шефе, как да помогна?"
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

jarvis_voice = "Brian"

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
            pulse_factor = min(max_size, pulse_factor + pulse_speed) if pulse_factor < max_size else max(min_size,
                                                                                                         pulse_factor - pulse_speed)
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

def chatbot():
    global wake_word_detected, model_answering, is_generating, jarvis_voice, jarvis_name

    print("Welcome to Vision! Say any of the models name to activate. Say 'exit' to quit.")

    while True:
        if not wake_word_detected:
            print("Waiting for wake word...")
            user_input = record_text()

            if not user_input:
                print("Sorry, I didn't catch that. Please try again.")
                continue

            user_input_lower = user_input.lower()
            if any(word in user_input_lower for word in ["джарвис", "джарви", "джервис", "jarvis", "черви"]):
                wake_word_detected = True
                pygame.mixer.music.load("../sound_files/beep.flac")
                pygame.mixer.music.play()

                print("✅ Wake word detected!")
                model_answering = True
                is_generating = False

                response = random.choice(jarvis_responses)
                generate_audio_from_text(text=response, voice=jarvis_voice)

                model_answering = False
                is_generating = True
            else:
                continue

        print("Listening for commands...")
        user_input = record_text()

        if not user_input:
            print("Error: No input detected.")
            wake_word_detected = False
            continue

        # Process input
        response = chat.send_message(user_input)
        text = response.text.strip()

        # Parse JSON
        try:
            clean_text = re.sub(r"```(?:json)?|```", "", text).strip()
            clean_text = clean_text.replace("'", '"')
            data = json.loads(clean_text)
        except json.JSONDecodeError as e:
            print(f"⚠️ Could not parse JSON: {e}")
            wake_word_detected = False
            continue

        # Handle answer
        if data.get("response_type") == "answer":
            answer = data.get("answer", "")
            print("🤖 Jarvis:", answer)
            generate_audio_from_text(answer, jarvis_voice)

        # Handle command
        elif data.get("response_type") == "command":
            function_name = data.get("function")
            params = data.get("parameters", {})
            func = globals().get(function_name)
            if func:
                try:
                    sig = inspect.signature(func)
                    if len(sig.parameters) == 0:
                        func()
                    elif len(sig.parameters) == 1:
                        func(*params.values())
                    else:
                        func(**params)
                    print(f"✅ Function {function_name} executed successfully")
                except Exception as e:
                    print(f"❌ Error executing function: {e}")
            else:
                print(f"⚠️ Function {function_name} not found")

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