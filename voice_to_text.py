import os
import tempfile
import subprocess
from typing import Optional

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = None

try:
    import sounddevice as sd
    import scipy.io.wavfile as wav
    import numpy as np
except ImportError:
    sd = None
    wav = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import whisper
    model = whisper.load_model("small")
except Exception:
    whisper = None
    model = None


def convert_to_pcm_wav(input_path: str) -> str:
    """
    Converts any input audio file (m4a, aac, mp3, ogg, etc.) to 16kHz 16-bit mono PCM WAV.
    If the file is already a valid WAV and can be read by the wave module, returns original path.
    """
    if not os.path.exists(input_path):
        return input_path

    # Check if already a valid PCM WAV
    try:
        import wave
        with wave.open(input_path, "rb") as wf:
            if wf.getnchannels() in (1, 2) and wf.getsampwidth() == 2:
                return input_path
    except Exception:
        pass

    ffmpeg_bin = FFMPEG_EXE or "ffmpeg"
    out_wav = tempfile.mktemp(suffix="_pcm.wav")
    try:
        cmd = [
            ffmpeg_bin, "-y", "-i", input_path,
            "-ac", "1", "-ar", "16000",
            "-sample_fmt", "s16", out_wav
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        if res.returncode == 0 and os.path.exists(out_wav) and os.path.getsize(out_wav) > 0:
            return out_wav
    except Exception as e:
        print(f"[Audio Conversion Warning] {e}")

    return input_path


def transcribe_audio_file(filepath: str, language: str = "en-IN") -> str:
    """
    Transcribes an audio file (.wav, .m4a, .mp3, etc.) using SpeechRecognition (Google) or Whisper.
    Supports English & Hinglish transcription.
    """
    if not os.path.exists(filepath):
        return ""

    pcm_wav = convert_to_pcm_wav(filepath)
    cleanup_temp = (pcm_wav != filepath)

    try:
        # Primary: Fast, high-accuracy cloud speech recognition
        if sr is not None:
            try:
                recognizer = sr.Recognizer()
                with sr.AudioFile(pcm_wav) as source:
                    audio = recognizer.record(source)
                    text = recognizer.recognize_google(audio, language=language)
                    return text.strip()
            except sr.UnknownValueError:
                return ""
            except Exception as e:
                print(f"[SpeechRecognition Error] {e}")

        # Fallback: Local Whisper model
        if model is not None:
            try:
                result = model.transcribe(pcm_wav)
                return result.get("text", "").strip()
            except Exception as e:
                print(f"[Whisper Error] {e}")

        return ""
    finally:
        if cleanup_temp:
            try:
                os.remove(pcm_wav)
            except Exception:
                pass


def record_audio(seconds=5, fs=16000):
    """Record audio from local PC microphone."""
    if sd is None or wav is None:
        return ""

    print("🎙 Listening...")
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype="float32")
    sd.wait()
    print("🎤 Done recording.")

    temp_path = tempfile.mktemp(suffix=".wav")
    wav.write(temp_path, fs, recording)
    return temp_path


def speech_to_text(duration=5):
    """Record audio and convert to text."""
    wav_path = record_audio(duration)
    if not wav_path:
        return ""
    text = transcribe_audio_file(wav_path)
    try:
        os.remove(wav_path)
    except:
        pass
    return text
