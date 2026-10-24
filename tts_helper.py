import os
import time
import asyncio
import edge_tts
import threading
import subprocess

# ---------------------------------------------------------
# NON-BLOCKING ffplay (TTS playback in background thread)
# ---------------------------------------------------------
def play_audio_background(filepath: str):
    played = False
    try:
        res = subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", filepath],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if res.returncode == 0:
            played = True
    except Exception:
        pass

    if not played:
        try:
            import winsound
            winsound.PlaySound(filepath, winsound.SND_FILENAME)
        except Exception as e:
            print("TTS Playback Error:", e)

    # Cleanup after playback
    try:
        os.remove(filepath)
    except:
        pass


# ---------------------------------------------------------
# MAIN FUNCTION — SAFE, NON-BLOCKING TTS
# ---------------------------------------------------------
async def speak_text(text: str, voice: str = "en-IN-PrabhatNeural"):
    # Create cache folder
    tmp_dir = os.path.join(os.getcwd(), "tts_cache")
    os.makedirs(tmp_dir, exist_ok=True)

    # Temporary WAV file
    filepath = os.path.join(tmp_dir, f"tts_{int(time.time() * 1000)}.wav")

    # Generate TTS to WAV (Async = smooth generation)
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filepath)

    # Play audio in background thread (non-blocking)
    threading.Thread(
        target=play_audio_background,
        args=(filepath,),
        daemon=True
    ).start()


async def generate_tts_file(text: str, voice: str = "en-IN-PrabhatNeural") -> str:
    tmp_dir = os.path.join(os.getcwd(), "tts_cache")
    os.makedirs(tmp_dir, exist_ok=True)
    filename = f"web_tts_{int(time.time() * 1000)}.wav"
    filepath = os.path.join(tmp_dir, filename)
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filepath)
    return filename

