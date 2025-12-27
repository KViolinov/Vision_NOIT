import os
import cv2
import time
import pygame
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

from jarvis_functions.essential_functions.enhanced_elevenlabs import generate_audio_from_text
from jarvis_functions.essential_functions.change_config_settings import get_jarvis_voice

os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_KEY")

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel(model_name="gemini-2.5-flash")

system_instruction = (
    "Вие сте Джарвис, полезен и информативен AI асистент."
    "Винаги отговаряйте професионално и кратко, но също се дръж приятелски."
    "Поддържайте отговорите кратки, но информативни."
    "Осигурете, че всички отговори са фактологически точни и лесни за разбиране."
)

chat = model.start_chat(history=[{"role": "user","parts": [system_instruction],}])


def gemini_vision(set_state_callback=None):
    if set_state_callback:
        set_state_callback("camera")

    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    # # Create a named window
    # cv2.namedWindow("Capture Window", cv2.WINDOW_NORMAL)
    #
    # # Create a named window and resize it
    # cv2.namedWindow("Capture Window", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("Capture Window", 800, 600)  # Set window size to 800x600
    #
    # for i in range(3, 0, -1):
    #     start_time = time.time()  # Start time for each second
    #
    #     while time.time() - start_time < 1:  # Loop for one second
    #         ret, frame = cap.read()
    #         if not ret:
    #             print("Error: Failed to capture image.")
    #             break
    #
    #         height, width, _ = frame.shape
    #
    #         # Calculate the position of the scan line (y-coordinate)
    #         # Cycle between top and bottom within the second
    #         progress = (time.time() - start_time)  # Progress within the second (0 to 1)
    #
    #         if i % 2 == 1:  # Odd numbers scan top to bottom
    #             line_position = int(progress * height)
    #         else:  # Even numbers scan bottom to top
    #             line_position = int(height - (progress * height))
    #
    #         # Draw the moving line on the frame
    #         cv2.line(frame, (0, line_position), (width, line_position), (0, 255, 0), 5)
    #
    #         # Add countdown text (centered)
    #         cv2.putText(frame, str(i), (350, 300), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 5)
    #
    #         # Show the frame
    #         cv2.imshow("Capture Window", frame)
    #
    #         if cv2.waitKey(1) & 0xFF == ord('q'):  # Added a way to quit
    #             break
    #
    #     else:  # Continue if no breaks in the while loop
    #         continue  # Only then decrement i
    #     break  # Break if the inner loop was broken

    # Capture the final image when countdown hits 1
    pygame.mixer.music.load("sound_files/camera_shutter.wav")
    pygame.mixer.music.play()

    ret, frame_bgr = cap.read()
    if not ret:
        print("Error: Failed to capture final image.")
        cap.release()
        cv2.destroyAllWindows()
        exit()

    # Convert BGR to RGB for Gemini
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

    # Convert to PIL Image
    captured_image = Image.fromarray(frame_rgb)

    # Close the OpenCV window
    cap.release()
    cv2.destroyAllWindows()

    # Provide a prompt
    prompt = "Опиши какво виждаш на снимката, с няколко изречения."

    # Send the image to the Gemini Vision model
    response = model.generate_content([prompt, captured_image])

    # Print the AI's response
    print("\nAI Response:")
    print(response.text)
    generate_audio_from_text(text=response.text, voice=get_jarvis_voice())

    if set_state_callback:
        set_state_callback("idle")