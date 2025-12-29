import os
import cv2
import time
import pygame
import threading

from jarvis_functions.essential_functions.voice_input import record_text
from account.check_account import require_login


pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)


@require_login
def record_video(set_state_callback=None):
    if set_state_callback:
        set_state_callback("recording")

    pygame.mixer.music.load("sound_files/start_recording.mp3")
    pygame.mixer.music.play()

    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    os.makedirs(downloads_dir, exist_ok=True)

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    video_path = os.path.join(downloads_dir, f"vision_record_{timestamp}.mp4")

    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    fourcc = cv2.VideoWriter_fourcc(*"XVID")

    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    video_path = os.path.join(downloads_dir, f"vision_record_{timestamp}.avi")

    out = cv2.VideoWriter(video_path, fourcc, 30, (1920, 1080))

    print("🎥 Recording started... Say 'Джарвис, спри видеото' to stop.")

    stop_flag = {"value": False}

    def listen_for_stop():
        stop_phrases = [
            "спри видеото",
            "спри видео",
            "джарвис спри видеото",
            "джарвис спри видео",
        ]

        while not stop_flag["value"]:
            text = record_text()
            if not text:
                continue
            normalized = text.lower().strip()

            # Match any of the stop phrases
            if any(phrase in normalized for phrase in stop_phrases):
                print("🛑 Stop command detected.")
                stop_flag["value"] = True
                break

    # Run listener in background thread
    listener_thread = threading.Thread(target=listen_for_stop, daemon=True)
    listener_thread.start()

    # Record until stop_flag is True
    while not stop_flag["value"]:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Frame capture failed.")
            break

        out.write(frame)
        cv2.imshow("Recording...", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            stop_flag["value"] = True
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    pygame.mixer.music.load("sound_files/end_recording.mp3")
    pygame.mixer.music.play()

    if set_state_callback:
        set_state_callback("idle")

    print(f"✅ Video saved to: {video_path}")
    return video_path
