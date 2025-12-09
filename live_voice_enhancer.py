import numpy as np
import sounddevice as sd

# =======================
# CONFIG
# =======================
SAMPLE_RATE = 16000       # Hz
BLOCK_SIZE  = 512         # frames per block
CHANNELS    = 1           # mono processing

# ----- Compressor -----
TARGET_RMS_DB   = -20.0   # desired loudness
MAX_GAIN_DB     = 20.0    # max upward gain
COMP_SMOOTHING  = 0.1     # gain smoothing (0..1)

# ----- Smoothed Gate -----
GATE_THRESHOLD_DB = -45.0  # level where gate starts acting
GATE_RANGE_DB     = 10.0   # dB range over which gate fades in
GATE_ATTENUATION  = 0.3    # minimum level when fully gated
GATE_SMOOTHING    = 0.5    # smoothing of gate gain

# ----- Noise Reduction -----
NOISE_UPDATE_THRESH_DB = -35.0  # frames below this treated as noise-only
NOISE_UPDATE_ALPHA     = 0.1    # how quickly noise profile adapts (0..1)
NOISE_OVEREST          = 1.0    # >1 = stronger suppression
NR_GAIN_FLOOR          = 0.15   # avoid complete nulling (musical noise)

# ----- Spectral EQ -----
HPF_CUTOFF_HZ      = 80.0                  # high-pass
PRESENCE_BAND      = (2000.0, 4000.0)      # intelligibility boost
PRESENCE_GAIN_DB   = 6.0
HF_SHELF_HZ        = 6000.0
HF_SHELF_GAIN_DB   = 3.0

# ----- Channel Vocoder -----
VOCODER_MIX        = 0.4    # 0 = off, 1 = full vocoder
NUM_BANDS          = 16     # number of vocoder bands
BAND_MIN_FREQ      = 200.0  # lower edge of first band
BAND_MAX_FREQ      = 6000.0 # upper edge of last band
ENV_ATTACK         = 0.3    # envelope attack smoothing
ENV_RELEASE        = 0.05   # envelope release smoothing

# ----- Limiter -----
LIMITER_THRESHOLD  = 0.98

# =======================
# UTILS
# =======================
def db_to_lin(db):
    return 10.0 ** (db / 20.0)

# =======================
# FREQUENCY GRID & EQ CURVE
# =======================
freqs = np.fft.rfftfreq(BLOCK_SIZE, d=1.0 / SAMPLE_RATE)

# Build EQ curve in dB
eq_curve_db = np.zeros_like(freqs)

# 1) High-pass
eq_curve_db[freqs < HPF_CUTOFF_HZ] -= 20.0

# 2) Presence boost
f1, f2 = PRESENCE_BAND
for i, f in enumerate(freqs):
    if f1 <= f <= f2:
        center = 0.5 * (f1 + f2)
        width  = (f2 - f1) * 0.5
        dist   = abs(f - center)
        if dist < width:
            eq_curve_db[i] += PRESENCE_GAIN_DB * (1.0 - dist / width)

# 3) HF shelf
nyquist = SAMPLE_RATE / 2.0
for i, f in enumerate(freqs):
    if f > HF_SHELF_HZ:
        t = (f - HF_SHELF_HZ) / (nyquist - HF_SHELF_HZ + 1e-12)
        t = np.clip(t, 0.0, 1.0)
        eq_curve_db[i] += HF_SHELF_GAIN_DB * t

EQ_CURVE_LIN = db_to_lin(eq_curve_db)

# =======================
# CHANNEL VOCODER BANDS
# =======================
# Log-spaced band edges
band_edges = np.geomspace(BAND_MIN_FREQ, BAND_MAX_FREQ, NUM_BANDS + 1)
band_indices = []
for b in range(NUM_BANDS):
    low = band_edges[b]
    high = band_edges[b + 1]
    mask = (freqs >= low) & (freqs < high)
    band_indices.append(np.where(mask)[0])

# =======================
# STATE
# =======================
previous_gain_lin = 1.0             # compressor
previous_gate_gain = 1.0            # smoothed gate
noise_est_mag = np.ones_like(freqs) * 1e-4  # initial noise profile
band_env = np.ones(NUM_BANDS) * 1e-3        # vocoder envelopes

# =======================
# CALLBACK
# =======================
def audio_callback(indata, outdata, frames, time, status):
    global previous_gain_lin, previous_gate_gain, noise_est_mag, band_env

    if status:
        print(status)

    # Safety: ensure expected block size
    if frames != BLOCK_SIZE:
        x = indata[:BLOCK_SIZE, 0]
    else:
        x = indata[:, 0]

    x = x.astype(np.float32)

    # ===== 1) COMPRESSOR + SMOOTHED GATE (time domain) =====
    rms = np.sqrt(np.mean(x * x) + 1e-12)
    rms_db = 20.0 * np.log10(rms + 1e-12)

    # --- smoothed gate: fade between 1.0 and GATE_ATTENUATION over GATE_RANGE_DB ---
    if rms_db >= GATE_THRESHOLD_DB:
        gate_target = 1.0
    elif rms_db <= GATE_THRESHOLD_DB - GATE_RANGE_DB:
        gate_target = GATE_ATTENUATION
    else:
        # linear interpolation
        t = (GATE_THRESHOLD_DB - rms_db) / GATE_RANGE_DB  # 0..1
        gate_target = 1.0 - t * (1.0 - GATE_ATTENUATION)

    gate_gain = (1.0 - GATE_SMOOTHING) * previous_gate_gain + GATE_SMOOTHING * gate_target
    previous_gate_gain = gate_gain

    # --- upward compression ---
    gain_db = TARGET_RMS_DB - rms_db
    if gain_db > MAX_GAIN_DB:
        gain_db = MAX_GAIN_DB
    if gain_db < 0.0:
        gain_db = 0.0  # upward only

    gain_lin = db_to_lin(gain_db) * gate_gain
    gain_lin = (1.0 - COMP_SMOOTHING) * previous_gain_lin + COMP_SMOOTHING * gain_lin
    previous_gain_lin = gain_lin

    x_comp = x * gain_lin

    # ===== 2) NOISE REDUCTION + EQ (spectral) =====
    X = np.fft.rfft(x_comp)
    mag = np.abs(X)
    phase = np.angle(X)

    # --- update noise profile when frame is mostly noise ---
    if rms_db < NOISE_UPDATE_THRESH_DB:
        noise_est_mag = (1.0 - NOISE_UPDATE_ALPHA) * noise_est_mag + NOISE_UPDATE_ALPHA * mag

    noise_power = noise_est_mag ** 2
    signal_power = mag ** 2

    # simple spectral subtraction / Wiener-style gain
    snr_est = np.maximum(signal_power - NOISE_OVEREST * noise_power, 0.0)
    gain_nr = np.sqrt(snr_est / (signal_power + 1e-12))
    gain_nr = np.clip(gain_nr, NR_GAIN_FLOOR, 1.0)

    X_denoised = X * gain_nr

    # apply EQ
    X_eq = X_denoised * EQ_CURVE_LIN
    x_eq = np.fft.irfft(X_eq, n=BLOCK_SIZE).astype(np.float32)

    # ===== 3) CLASSIC MULTI-BAND CHANNEL VOCODER (NOISE CARRIER) =====
    if VOCODER_MIX > 0.0:
        mag_eq = np.abs(X_eq)

        # --- update band envelopes from speech magnitude ---
        for b in range(NUM_BANDS):
            idx = band_indices[b]
            if idx.size == 0:
                continue
            band_mag = np.mean(mag_eq[idx]) + 1e-12
            if band_mag > band_env[b]:
                # attack
                band_env[b] = (1.0 - ENV_ATTACK) * band_env[b] + ENV_ATTACK * band_mag
            else:
                # release
                band_env[b] = (1.0 - ENV_RELEASE) * band_env[b] + ENV_RELEASE * band_mag

        # noise carrier
        noise = np.random.randn(BLOCK_SIZE).astype(np.float32)
        N = np.fft.rfft(noise)

        # build vocoder spectrum: band envelopes + noise phase
        V = np.zeros_like(N, dtype=np.complex64)
        for b in range(NUM_BANDS):
            idx = band_indices[b]
            if idx.size == 0:
                continue
            band_phase = np.angle(N[idx])
            V[idx] = band_env[b] * np.exp(1j * band_phase)

        v_time = np.fft.irfft(V, n=BLOCK_SIZE).astype(np.float32)

        # normalize vocoder level to roughly match x_eq
        v_rms = np.sqrt(np.mean(v_time * v_time) + 1e-12)
        x_rms = np.sqrt(np.mean(x_eq * x_eq) + 1e-12)
        if v_rms > 0.0:
            v_time *= (x_rms / v_rms)

        mix = np.clip(VOCODER_MIX, 0.0, 1.0)
        y = (1.0 - mix) * x_eq + mix * v_time
    else:
        y = x_eq

    # ===== 4) LIMITER =====
    peak = np.max(np.abs(y))
    if peak > LIMITER_THRESHOLD:
        y = y * (LIMITER_THRESHOLD / peak)

    outdata[:, 0] = y

# =======================
# MAIN
# =======================
if __name__ == "__main__":
    print("Starting real-time enhanced + vocoded voice.")
    print("Press Ctrl+C to stop.")

    with sd.Stream(channels=CHANNELS,
                   samplerate=SAMPLE_RATE,
                   blocksize=BLOCK_SIZE,
                   dtype="float32",
                   callback=audio_callback):
        try:
            while True:
                sd.sleep(1000)
        except KeyboardInterrupt:
            print("\nStopping.")

