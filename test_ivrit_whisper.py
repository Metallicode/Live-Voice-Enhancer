from faster_whisper import WhisperModel

# You can use "cpu" or "cuda" depending on your machine.
# For CPU-only, int8 is much faster and uses less RAM.
DEVICE = "cpu"      # or "cuda"
COMPUTE_TYPE = "int8"  # "float16" if you have GPU, or "float32" if needed

def main():
    # This will download from Hugging Face the first time you run it
    model = WhisperModel(
        "ivrit-ai/whisper-large-v3-ct2",
        device=DEVICE,
        compute_type=COMPUTE_TYPE,
    )

    # Test audio file (Hebrew speech, mono, ~16kHz recommended but not required)
    audio_path = "test.wav"

    # Transcribe
    segments, info = model.transcribe(
        audio_path,
        language="he",        # force Hebrew
        beam_size=5,
        vad_filter=True,      # use built-in VAD
        vad_parameters=dict(min_silence_duration_ms=500),
    )

    print(f"Detected language: {info.language}, prob={info.language_probability:.2f}")
    print("Transcript:")

    full_text = []
    for seg in segments:
        print(f"[{seg.start:6.2f} - {seg.end:6.2f}] {seg.text}")
        full_text.append(seg.text)

    print("\nFull text:")
    print("".join(full_text))


if __name__ == "__main__":
    main()

