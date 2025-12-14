
# ElevenLabs Realtime Speech-to-Text (Experimental)

This project is a **Python experiment using ElevenLabs’ Realtime Speech-to-Text API**.

It streams microphone audio to ElevenLabs in real time and receives:
- **Partial transcripts** (live feedback)
- **Committed transcripts** (final segments)

The goal is to evaluate realtime STT as a building block for **assistive communication tools**, especially where batch transcription introduces too much delay.

---

## Current Status

✅ Connection and audio streaming work  
✅ Realtime session is established  
⚠️ Realtime transcription is **experimental** and still unstable  
⚠️ Connection may close unexpectedly depending on audio activity  

This matches the current maturity of the ElevenLabs realtime STT feature.

---

## Important Python Version Requirement

⚠️ **Python 3.11 is required**

The ElevenLabs realtime SDK depends on newer versions of the `websockets` library that **do not work on Python 3.8**.

If you try to run this on Python 3.8, you will encounter errors like:

```

TypeError: create_connection() got an unexpected keyword argument 'additional_headers'

````

This is a hard dependency issue, not a bug in your code.

✅ **Use Python 3.11 or newer**

---

## Requirements

### System
- Linux (tested on Ubuntu 20.04)
- Microphone
- Internet connection

### Python
- Python **3.11**
- Packages:
  - `elevenlabs`
  - `websockets`
  - `sounddevice`
  - `numpy`

---

## Installation

### 1. Create a Python 3.11 virtual environment

```bash
python3.11 -m venv venv_rt
source venv_rt/bin/activate
````

Verify:

```bash
python --version
# Python 3.11.x
```

---

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install elevenlabs websockets sounddevice numpy
```

---

### 3. Set your API key

```bash
export ELEVENLABS_API_KEY="your_api_key_here"
```

(Add this to `~/.bashrc` if you want it permanent.)

---

## Running the Realtime STT Test

```bash
python eleven_realtime_stt_mic.py
```

What to expect:

* The script connects to ElevenLabs Realtime STT
* Microphone audio is streamed continuously
* Partial transcripts may appear live
* Committed transcripts appear after voice activity is detected
* Stop with `Ctrl+C`

---

## Configuration (in code)

Key parameters:

```python
MODEL_ID = "scribe_v2_realtime"
LANGUAGE_CODE = "he"          # or "en", "heb", or auto-detect
AUDIO_FORMAT = AudioFormat.PCM_16000
SAMPLE_RATE = 16000
COMMIT_STRATEGY = CommitStrategy.VAD
```

* **VAD commit strategy** automatically finalizes segments when silence is detected
* Manual commit is also supported but not required for basic tests

---

## Known Limitations

* Realtime STT may disconnect if:

  * Not enough audio activity is detected
  * Audio chunks are malformed
  * The session times out
* Transcription may not begin until ~2 seconds of audio have been received
* Feature behavior may change as ElevenLabs updates the API
* This is **not a stable or production-ready feature yet**

---

## Intended Use

This experiment is intended for:

* Research
* Prototyping assistive speech tools
* Evaluating latency vs batch transcription
* Comparing realtime STT with Whisper-style pipelines

It is **not** a medical or accessibility-certified solution.

---

## Next Steps / Ideas

* Add automatic reconnection with backoff
* Log partial vs committed latency
* Pipe realtime text into a TTS engine
* Compare realtime vs batch accuracy for impaired speech
* Integrate into a separate UI or service layer

---

## Disclaimer

This project is experimental.

No guarantees are made regarding accuracy, availability, or suitability for clinical or assistive use.

```









# Assistive Speech: Record → Transcribe → Speak (ElevenLabs)

This project is a **small desktop assistive communication tool**.

It allows a user to:
1. Press a button to **record 5 seconds of speech**
2. Send the recording to **ElevenLabs Speech-to-Text (STT)**
3. Display the **transcribed text on screen** (Hebrew supported)
4. Optionally generate a **clear synthetic voice** from that text using **ElevenLabs Text-to-Speech (TTS)**
5. Automatically **play the generated voice**

The tool is designed for **people with weak or impaired speech**, where speech recognition works better than direct voice intelligibility.

---

## Features

- 🎙 Button-based recording (no keyboard needed)
- 🧠 ElevenLabs **Scribe** STT (`scribe_v1`)
- 🗣 ElevenLabs TTS (`eleven_v3` or `eleven_multilingual_v2`)
- 🇮🇱 Hebrew language support (right-aligned display)
- ▶ Automatic playback of generated speech
- 💾 Audio files saved locally for review

---

## Important Python Version Notice (READ THIS)

⚠️ **This GUI uses Tkinter, which on Ubuntu 20.04 only works with Python 3.8.**

- Ubuntu 20.04 ships Tkinter bindings **only for Python 3.8**
- Newer Python versions (3.10 / 3.11) **cannot use Tkinter** on this OS
- This is a system limitation, not a bug in the script

✅ **Use Python 3.8 for this GUI application**

You may still use Python 3.11 for non-GUI scripts (e.g. Whisper experiments).

---

## Requirements

### System
- Ubuntu 20.04+
- Microphone
- Speakers or headphones
- `ffmpeg` (for MP3 playback)

Install ffmpeg:

```bash
sudo apt install ffmpeg


##Installation:

1. Create a Python 3.8 virtual environment

python3 -m venv venv
source venv/bin/activate



2. Install dependencies

pip install --upgrade pip
pip install sounddevice numpy elevenlabs


3. Set environment variables (using .env)
ELEVENLABS_API_KEY="your_api_key_here"
ELEVENLABS_VOICE_ID="your_voice_id_here"


4. running:
python gui_stt_tts.py
```


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

