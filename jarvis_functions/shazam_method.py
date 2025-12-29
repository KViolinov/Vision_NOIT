import os
import time
import wave
import asyncio
import tempfile
import numpy as np
import sounddevice as sd
from shazamio import Shazam

from pydub import AudioSegment

AudioSegment.converter = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")

from jarvis_functions.essential_functions.enhanced_elevenlabs import (
    generate_audio_from_text,
)
from jarvis_functions.essential_functions.voice_input import record_text
from jarvis_functions.play_spotify import play_song

from jarvis_functions.essential_functions.change_config_settings import get_jarvis_voice
from account.check_account import require_login

jarvis_voice = get_jarvis_voice()


# Function to capture audio from the microphone
def record_audio(duration=5, samplerate=44100):
    print("Recording...")
    audio = sd.rec(
        int(duration * samplerate), samplerate=samplerate, channels=2, dtype="int16"
    )
    sd.wait()  # Wait for the recording to finish
    return audio


# Function to save the audio as a temporary WAV file
def save_audio_to_wav(audio_data, samplerate=44100):
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        with wave.open(tmpfile, "wb") as wf:
            wf.setnchannels(2)  # Stereo channels
            wf.setsampwidth(2)  # 2 bytes per sample (16-bit)
            wf.setframerate(samplerate)  # Sample rate (e.g., 44100 Hz)
            wf.writeframes(audio_data.tobytes())  # Write the audio data to the WAV file
        return tmpfile.name


# Synchronous function to recognize audio
@require_login
def recognize_song():
    generate_audio_from_text(
        text="Няма проблем, дайте ми само една секунда.", voice=jarvis_voice
    )

    time.sleep(1)  # Pause for a moment to ensure the message is delivered

    generate_audio_from_text(
        text="Готов съм, доближете телефона до микрофона.", voice=jarvis_voice
    )

    shazam = Shazam()

    # Record audio from the microphone (5 seconds)
    audio_data = record_audio(duration=5, samplerate=44100)

    # Save the audio data to a temporary WAV file
    wav_file = save_audio_to_wav(audio_data)

    # Run the async recognition inside a synchronous context using a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(shazam.recognize(wav_file))

    if "track" in result:
        title = result["track"].get("title", "Unknown Title")
        artist = result["track"].get("subtitle", "Unknown Artist")

        generate_audio_from_text(
            text=f"Песента е {title} от {artist}. Желаете ли да я пусна в spotify?",
            voice=jarvis_voice,
        )

        answer = record_text()

        if "да" in answer or "yes" in answer:
            play_song(title + " " + artist)

        elif "не" in answer or "no" in answer:
            generate_audio_from_text(text="Разбрах, няма проблем.", voice=jarvis_voice)

    else:
        return None, None  # Return None if no song is found
