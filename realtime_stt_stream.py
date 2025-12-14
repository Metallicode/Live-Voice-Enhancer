import os
import asyncio
import base64
import numpy as np
import sounddevice as sd

from dotenv import load_dotenv

load_dotenv()

from elevenlabs import (
    ElevenLabs,
    RealtimeAudioOptions,
    AudioFormat,
    CommitStrategy,
    RealtimeEvents,
)

SAMPLE_RATE = 16000
CHUNK_MS = 200              # docs suggest streaming chunks; 100–1000ms is typical :contentReference[oaicite:2]{index=2}
CHANNELS = 1

MODEL_ID = "scribe_v2_realtime"
LANGUAGE_CODE = "he"        # or "heb"
AUDIO_FORMAT = AudioFormat.PCM_16000
COMMIT_STRATEGY = CommitStrategy.VAD  # automatic commit using VAD :contentReference[oaicite:3]{index=3}


def pcm16_b64_from_float32(audio_f32: np.ndarray) -> str:
    """Convert float32 [-1,1] mono to PCM16LE base64."""
    audio_f32 = np.clip(audio_f32, -1.0, 1.0)
    pcm16 = (audio_f32 * 32767.0).astype(np.int16)
    return base64.b64encode(pcm16.tobytes()).decode("ascii")


async def main():
    if not os.environ.get("ELEVENLABS_API_KEY"):
        raise RuntimeError("Set ELEVENLABS_API_KEY env var.")

    elevenlabs = ElevenLabs()  # reads ELEVENLABS_API_KEY from env (SDK behavior)

    config = RealtimeAudioOptions(
        model_id="scribe_v2_realtime",
        language_code="he",
        audio_format=AudioFormat.PCM_16000,
        sample_rate=16000,              # ✅ ADD THIS
        commit_strategy=CommitStrategy.VAD,
        vad_silence_threshold_secs=1.5,
        vad_threshold=0.4,
        min_speech_duration_ms=100,
        min_silence_duration_ms=100,
        include_timestamps=False,
    )

    connection = await elevenlabs.speech_to_text.realtime.connect(config)

    # --- Event handlers (print everything useful) ---
    def on_error(err):
        print(f"\n[ERROR] {err}")

    def on_close():
        print("\n[CLOSE] Connection closed")

    def on_partial(data):
        # some SDK versions pass dict-like payloads
        text = getattr(data, "text", None) or (data.get("text") if isinstance(data, dict) else "")
        print(f"\r[partial] {text[:200]}   ", end="", flush=True)

    def on_committed(data):
        text = getattr(data, "text", None) or (data.get("text") if isinstance(data, dict) else "")
        print(f"\n[committed] {text}")

    connection.on(RealtimeEvents.ERROR, on_error)
    connection.on(RealtimeEvents.CLOSE, on_close)

    # Depending on SDK version, these event names may exist:
    # If your SDK raises AttributeError here, tell me what RealtimeEvents contains.
    if hasattr(RealtimeEvents, "PARTIAL_TRANSCRIPT"):
        connection.on(RealtimeEvents.PARTIAL_TRANSCRIPT, on_partial)
    if hasattr(RealtimeEvents, "COMMITTED_TRANSCRIPT"):
        connection.on(RealtimeEvents.COMMITTED_TRANSCRIPT, on_committed)

    # --- Mic streaming loop ---
    frames_per_chunk = int(SAMPLE_RATE * (CHUNK_MS / 1000.0))

    print("Recording… speak for a few seconds. Press Ctrl+C to stop.\n")

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
            blocksize=frames_per_chunk,
        ) as stream:
            while True:
                audio_chunk, _ = stream.read(frames_per_chunk)
                mono = audio_chunk[:, 0] if audio_chunk.ndim > 1 else audio_chunk
                b64 = pcm16_b64_from_float32(mono)

                await connection.send({
                    "audio_base_64": b64,
                    "sample_rate": SAMPLE_RATE,
                })

                # With VAD commit, you usually do NOT need manual commit. :contentReference[oaicite:4]{index=4}
                # If you want to force a commit occasionally, uncomment:
                # await connection.commit()

    except KeyboardInterrupt:
        print("\nStopping… committing final segment.")
        try:
            await connection.commit()
        except Exception:
            pass

    # Give server a moment to flush final events
    await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())

