import queue
import sys
import threading
import time

import numpy as np
import sounddevice as sd
import whisper
import pyttsx3

# ============= CONFIG =============
SAMPLE_RATE = 16000
CHANNELS = 1
RECORD_SECONDS = 4.0      # length of each utterance
MODEL_NAME = "base"       # "tiny", "base", "small", etc.
LANGUAGE = "en"           # or None for auto-detect
# ==================================


def record_audio(duration=RECORD_SECONDS, samplerate=SAMPLE_RATE, channels=CHANNELS):
    """Record a single utterance and return it as a float32 numpy array."""
    print(f"\nRecording for {duration:.1f} seconds... Speak now.")
    audio = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=channels,
        dtype="float32",
    )
    sd.wait()
    print("Recording finished.")
    # If stereo, take first channel
    if audio.ndim > 1:
        audio = audio[:, 0]
    return audio


def main():
    print("Loading Whisper model (this may take a bit the first time)...")
    model = whisper.load_model(MODEL_NAME)
    print(f"Loaded model: {MODEL_NAME}")

    # Init TTS
    tts_engine = pyttsx3.init()
    # You can tweak voice/rate here:
    # voices = tts_engine.getProperty("voices")
    # tts_engine.setProperty("voice", voices[0].id)
    # tts_engine.setProperty("rate", 170)

    print("\nSimple STT → TTS loop")
    print("Press Enter to record an utterance, or type 'q' + Enter to quit.\n")

    while True:
        user_in = input("Press Enter to record, or 'q' + Enter to quit: ").strip().lower()
        if user_in == "q":
            print("Exiting.")
            break

        # 1) Record
        audio = record_audio()

        # 2) Run Whisper STT
        print("Transcribing...")
        # Whisper expects 16 kHz float32 numpy array
        # If you want, you can use options like 'language=LANGUAGE' or 'task="translate"'
        result = model.transcribe(
            audio,
            fp16=False,  # set True if you have GPU with half-precision support
            language=LANGUAGE,
        )

        text = result.get("text", "").strip()
        if not text:
            print("Didn't catch anything.")
            continue

        print(f"Recognized: \"{text}\"")

        # 3) TTS speak it back
        print("Speaking...")
        tts_engine.say(text)
        tts_engine.runAndWait()
        print("Done.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.")

