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
