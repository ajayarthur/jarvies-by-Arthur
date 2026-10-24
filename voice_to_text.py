import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import tempfile
import whisper


model = whisper.load_model("small")  # You can use "tiny" for faster


def record_audio(seconds=5, fs=16000):
    print("🎙 Listening...")
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype="float32")
    sd.wait()
    print("🎤 Done recording.")

    # Save to temporary WAV
    temp_path = tempfile.mktemp(suffix=".wav")
    wav.write(temp_path, fs, recording)
    return temp_path


def speech_to_text(duration=5):
    """Record audio and convert to text using Whisper."""
    wav_path = record_audio(duration)
    print("🔍 Recognizing speech...")
    result = model.transcribe(wav_path)
    return result["text"].strip()
