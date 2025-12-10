# Real-Time Voice Enhancer & Vocoder (Assistive Speech DSP)

This project is a **real-time Python audio processing pipeline** designed to help improve the intelligibility of weak or impaired speech (e.g. vocal cord paralysis) in noisy or non-ideal environments.

It processes live microphone input and outputs a clearer, louder, and optionally vocoded voice through speakers or headphones with **low latency**.

This is **assistive DSP**, not a medical device.

---

## Features

- 🎙 **Live microphone input → speaker output**
- 🔊 **Upward compressor** for very quiet voices
- 🚪 **Smoothed noise gate** (no harsh chopping)
- 🧠 **Adaptive spectral noise reduction**
  - Learns the noise profile in real time
- 🎚 **Speech-focused EQ**
  - High-pass filter
  - Presence boost (2–4 kHz)
  - Mild high-frequency shelf
- 🤖 **Classic multi-band channel vocoder**
  - Noise carrier
  - Log-spaced frequency bands
  - Adjustable mix with natural voice
- 🧱 **Limiter** to prevent clipping

Designed to be:
- Hackable
- Educational
- Extendable (ASR → TTS, pitch shifting, formant work, etc.)

---

## Requirements

- Python **3.9+**
- PortAudio (system dependency)

### Python packages

```bash
pip install sounddevice numpy
```





# STT → TTS Assistive Voice Proxy

This project is a **simple speech-to-text → text-to-speech (STT → TTS)** loop in Python, designed as a prototype “voice proxy” for people with weak or impaired speech (e.g. vocal cord paralysis).

The idea:

1. The user speaks into a microphone.
2. A speech recognition model (Whisper) converts the audio to text.
3. A TTS engine speaks the text back with a **clear, loud synthetic voice**.

It’s not real-time syllable-by-syllable, but works well for **short phrases** and is much more intelligible than a very weak, breathy voice.

> ⚠️ This is an experimental assistive tool, not a medical device.

---

## Features

- 🎙 **Press-to-talk recording** from the microphone
- 🧠 **Whisper-based speech recognition** (local model)
- 🗣 **On-device text-to-speech** via `pyttsx3`
- 🔁 Simple loop:
  - Press Enter → record
  - Whisper transcribes
  - TTS speaks the recognized text
- 🧩 Easy to customize:
  - Recording length
  - Whisper model size (`tiny`, `base`, `small`…)
  - TTS voice and speaking rate

---

## Requirements

### System

- Python **3.9+**
- A working microphone
- Speakers or headphones
- `ffmpeg` installed and on your PATH (required by Whisper)

Examples:

- **Debian/Ubuntu:**
  ```bash
  sudo apt install ffmpeg

```
pip install sounddevice numpy openai-whisper pyttsx3
```





# Hebrew Speech-to-Text (STT) with faster-whisper

This project provides a **simple speech-to-text pipeline** using  
[`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) and a **Hebrew-optimized Whisper model**:

> **ivrit-ai/whisper-large-v3-ct2**
>
> https://huggingface.co/ivrit-ai/models

It is intended as a foundation for **assistive speech applications**, where spoken Hebrew is converted into clear, machine-readable text (and later TTS).

---

## Requirements

### System
- Ubuntu 20.04+
- A working microphone
- Python **3.11** (recommended)
- Internet connection (model downloads once)

### Python packages
- `faster-whisper`
- `soundfile`
- `numpy`
- `sounddevice` (for mic input, optional)

---

## Installation

### 1. Create and activate a Python 3.11 virtual environment

```bash
python3.11 -m venv venv311
source venv311/bin/activate

