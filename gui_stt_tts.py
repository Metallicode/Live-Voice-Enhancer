import os
import threading
import time
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import sounddevice as sd
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()
# -------------------------
# CONFIG
# -------------------------
SAMPLE_RATE = 16000
CHANNELS = 1
RECORD_SECONDS = 5

STT_MODEL_ID = "scribe_v2"
STT_LANGUAGE_CODE = "heb"  # or "he"

# MP3 output (ElevenLabs supports these formats; mp3_44100_128 is default) :contentReference[oaicite:1]{index=1}
TTS_OUTPUT_FORMAT = "mp3_44100_128"

API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not API_KEY:
    raise SystemExit("Missing ELEVENLABS_API_KEY. Set it as an environment variable.")

DEFAULT_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")

PROJECT_DIR = Path(__file__).resolve().parent
RECORDINGS_DIR = PROJECT_DIR / "recordings"
TTS_DIR = PROJECT_DIR / "tts_out"
RECORDINGS_DIR.mkdir(exist_ok=True)
TTS_DIR.mkdir(exist_ok=True)

client = ElevenLabs(api_key=API_KEY)


# -------------------------
# Audio helpers
# -------------------------
def record_audio(seconds: float) -> np.ndarray:
    frames = int(seconds * SAMPLE_RATE)
    audio = sd.rec(frames, samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32")
    sd.wait()
    if audio.ndim > 1:
        audio = audio[:, 0]
    return audio.astype(np.float32)


def write_wav_pcm16(path: Path, audio_f32: np.ndarray):
    import wave
    audio_i16 = np.clip(audio_f32, -1.0, 1.0)
    audio_i16 = (audio_i16 * 32767.0).astype(np.int16)

    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_i16.tobytes())


def autoplay_audio(path: Path):
    """
    Auto-play MP3 using ffplay if available, otherwise fall back to xdg-open.
    """
    # Try ffplay (best for autoexit, no UI)
    try:
        subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    except FileNotFoundError:
        pass

    # Fallback: open with default system player
    subprocess.Popen(["xdg-open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# -------------------------
# ElevenLabs calls
# -------------------------
def stt_transcribe_wav(wav_path: Path) -> str:
    with open(wav_path, "rb") as f:
        transcription = client.speech_to_text.convert(
            file=f,
            model_id=STT_MODEL_ID,
            language_code=STT_LANGUAGE_CODE,
            diarize=False,
            tag_audio_events=False,
        )
    return transcription.text or ""


def tts_generate_mp3(text: str, voice_id: str) -> bytes:
    if not voice_id:
        raise ValueError("Missing Voice ID. Set ELEVENLABS_VOICE_ID or enter one in the UI.")

    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text[::-1],
        output_format="mp3_44100_128",
        model_id="eleven_v3",
    )

    # SDK may return bytes OR an iterator of chunks
    if isinstance(audio, (bytes, bytearray)):
        return bytes(audio)
    return b"".join(audio)


# -------------------------
# GUI
# -------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Assistive STT → TTS (ElevenLabs)")
        self.geometry("820x460")

        self.status_var = tk.StringVar(value="Ready.")

        controls = ttk.Frame(self, padding=12)
        controls.pack(fill="x")

        self.btn_record = ttk.Button(controls, text="Record 5s + Transcribe", command=self.on_record_transcribe)
        self.btn_record.pack(side="left")

        self.btn_speak = ttk.Button(controls, text="Generate + Play Voice", command=self.on_speak, state="disabled")
        self.btn_speak.pack(side="left", padx=(10, 0))

        ttk.Label(controls, text="Voice ID:").pack(side="left", padx=(16, 6))
        self.voice_entry = ttk.Entry(controls, width=46)
        self.voice_entry.pack(side="left", fill="x", expand=True)
        if DEFAULT_VOICE_ID:
            self.voice_entry.insert(0, DEFAULT_VOICE_ID)

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text="Transcribed text:").pack(anchor="w")

        self.text_box = tk.Text(body, wrap="word", height=14)
        self.text_box.pack(fill="both", expand=True, pady=(6, 8))

        # Right-align display using a tag (Text widget has no -justify option)
        self.text_box.tag_configure("rtl", justify="right")

        status = ttk.Frame(self, padding=(12, 6))
        status.pack(fill="x")
        ttk.Label(status, textvariable=self.status_var).pack(side="left")

    def set_busy(self, busy: bool, status: str):
        self.status_var.set(status)
        self.btn_record.config(state="disabled" if busy else "normal")

        if busy:
            self.btn_speak.config(state="disabled")
        else:
            txt = self.text_box.get("1.0", "end").strip()
            self.btn_speak.config(state="normal" if txt else "disabled")

    def set_text(self, text: str):
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", text[::-1])
        self.text_box.tag_add("rtl", "1.0", "end")

    def show_error(self, msg: str):
        self.set_busy(False, "Error.")
        messagebox.showerror("Error", msg)

    def on_record_transcribe(self):
        def worker():
            try:
                self.after(0, lambda: self.set_busy(True, "Recording..."))

                audio = record_audio(RECORD_SECONDS)
                ts = time.strftime("%Y%m%d-%H%M%S")
                wav_path = RECORDINGS_DIR / f"rec_{ts}.wav"
                write_wav_pcm16(wav_path, audio)

                self.after(0, lambda: self.set_busy(True, "Transcribing (ElevenLabs STT)..."))
                text = stt_transcribe_wav(wav_path)

                def update_ui():
                    if not text.strip():
                        self.set_text("")
                        self.set_busy(False, f"No text recognized. Saved: {wav_path.name}")
                        messagebox.showinfo("No speech detected", "No text was recognized. Try again closer to the mic.")
                        return
                    self.set_text(text)
                    self.set_busy(False, f"Done. Saved: {wav_path.name}")

                self.after(0, update_ui)

            except Exception as ex:
                self.after(0, lambda m=str(ex): self.show_error(m))

        threading.Thread(target=worker, daemon=True).start()

    def on_speak(self):
        text = self.text_box.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("No text", "Nothing to speak yet.")
            return

        voice_id = self.voice_entry.get().strip()
        if not voice_id:
            messagebox.showerror("Missing Voice ID", "Set ELEVENLABS_VOICE_ID or paste a Voice ID into the field.")
            return

        def worker():
            try:
                self.after(0, lambda: self.set_busy(True, "Generating voice (ElevenLabs TTS)..."))

                mp3_bytes = tts_generate_mp3(text, voice_id)
                ts = time.strftime("%Y%m%d-%H%M%S")
                mp3_path = TTS_DIR / f"tts_{ts}.mp3"
                mp3_path.write_bytes(mp3_bytes)

                self.after(0, lambda: self.set_busy(True, "Playing audio..."))
                autoplay_audio(mp3_path)

                self.after(0, lambda: self.set_busy(False, f"Done. Saved: {mp3_path.name}"))

            except Exception as ex:
                self.after(0, lambda m=str(ex): self.show_error(m))

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()

