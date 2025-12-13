import os
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not API_KEY:
    raise SystemExit("Missing ELEVENLABS_API_KEY (set env var or .env file).")

# Path to your WAV
AUDIO_PATH = "test.wav"

# Hebrew language code:
# ElevenLabs accepts ISO-639-1 or ISO-639-3 language codes. Hebrew is "he" or "heb".
# If you're unsure, set language_code=None to auto-detect.
LANGUAGE_CODE = "he"   # try "heb" if needed

def main():
    client = ElevenLabs(api_key=API_KEY)

    with open(AUDIO_PATH, "rb") as f:
        transcription = client.speech_to_text.convert(
            file=f,
            model_id="scribe_v1",
            language_code=LANGUAGE_CODE,   # or None for auto-detect
            diarize=False,                 # set True if multiple speakers
            tag_audio_events=False,        # True to tag laughter/applause etc.
        )

    # transcription is typically a dict-like object / JSON payload
    print(transcription.text)



if __name__ == "__main__":
    main()

