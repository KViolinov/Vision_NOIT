from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import os, sys

def ensure_ffmpeg_in_path():
    """Ensure ffmpeg, ffplay, ffprobe are available in PATH (works in both dev & compiled)."""
    if getattr(sys, 'frozen', False):
        # When compiled with Nuitka or PyInstaller
        base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
        ffmpeg_dir = os.path.join(base_path, "jarvis_functions", "essential_functions", "important_files")
    else:
        # When running directly from source — ffmpeg files are in the same folder
        ffmpeg_dir = os.path.dirname(os.path.abspath(__file__))

    if os.path.exists(ffmpeg_dir):
        os.environ["PATH"] += os.pathsep + ffmpeg_dir
        print(f"[FFmpeg] Added to PATH: {ffmpeg_dir}")
    else:
        print("[FFmpeg] Folder not found:", ffmpeg_dir)

# Make sure ffmpeg is available before ElevenLabs tries to play audio
ensure_ffmpeg_in_path()
# ---------------------------------

load_dotenv()

elevenlabs = ElevenLabs(
  api_key=os.getenv("ELEVEN_LABS_API"),
)

def generate_audio_from_text(text: str, voice: str):
    voice_id = ""

    match voice:
        case "Brian":
            voice_id = "nPczCjzI2devNBz1zQrb"
        case "Samantha":
            voice_id = "gu1puNDpHxzdmn6ZDDcv"
        case "Roger":
            voice_id = "CwhRBWXzGAHq8TQ4Fs17"
        case "Jessica":
            voice_id = "cgSgspJ2msm6clMCkdW9"
        case "Slavi":
            voice_id = "D7b0HzOjHS3KpzAVn1oC"

    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_flash_v2_5",  # better quality model
        output_format="mp3_44100_128",
    )

    play(audio)
