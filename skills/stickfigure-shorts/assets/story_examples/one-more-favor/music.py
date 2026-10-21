"""Original background track for "One more favor" (numpy only).

120 BPM, 30.5 s, timed to the story:
  0.00–0.55  rising tension into a soft thud (the box lands over his face — the hook)
  0.55–8     D minor piano + pad; slow "heavy footsteps" kick from 3 s
  8–13       bass and eighth-note piano push harder
  13–18      everything drops away: one held chord and sparse high notes (he notices)
  18–24      gentle re-entry, steadier, warmer
  24–30.5    F major, no drums, rising arpeggio, rings out (the bench, the glow)

  python3 music.py music.wav
"""
import sys
import wave

import numpy as np

SR = 44100
DUR = 30.5
N = int(SR * DUR)
rng = np.random.default_rng(11)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(buf, start, sig, gain=1.0):
    i = int(start * SR)
    n = buf.shape[-1]
    if i >= n:
        return
    sig = sig[..., : n - i]
    buf[..., i:i + sig.shape[-1]] += gain * sig


def piano(f, dur=1.6, vel=1.0):
    t = np.arange(int(SR * dur)) / SR
    out = np.zeros_like(t)
    for k, amp in enumerate((1.0, 0.45, 0.22, 0.1, 0.05), start=1):
        out += amp * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * t) * np.exp(-t * (2.0 + 1.5 * k))
    return vel * out * np.minimum(t / 0.004, 1)


def pad(notes, dur, harmonics=5, attack=0.5):
    t = np.arange(int(SR * dur)) / SR
    out = np.zeros((2, len(t)))
    for m in notes:
        for ch, det in enumerate((0.9985, 1.0015)):
            f = hz(m) * det
            for k in range(1, harmonics + 1):
                out[ch] += np.sin(2 * np.pi * f * k * t + k) / k
    env = np.minimum(t / attack, 1) * np.minimum((dur - t) / 0.6, 1)
    return out * env / (len(notes) * 2.5)


def kick(strength=1.0, length=0.45, f0=50, f1=140):
    t = np.arange(int(SR * length)) / SR
    f = f0 + (f1 - f0) * np.exp(-t * 30)
    return strength * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)


def noise(length):
    return rng.standard_normal(int(SR * length))


def fft_filter(x, lo=None, hi=None):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if lo:
        m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi:
        m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))


def reverb(x, length=2.2, decay=0.7, mix=0.32):
    ir = noise(length) * np.exp(-np.arange(int(SR * length)) / SR / decay)
    ir = fft_filter(ir, hi=4500)
    ir /= np.sqrt(np.sum(ir ** 2))
    n = 1 << int(np.ceil(np.log2(len(x) + len(ir))))
    wet = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[: len(x)]
    return x + mix * wet


DM, BB, F, C, GM = (50, 53, 57), (46, 50, 53), (53, 57, 60), (48, 52, 55), (55, 58, 62)
MINOR = [DM, BB, F, C]

keys = np.zeros(N)
pads = np.zeros((2, N))
bass = np.zeros(N)
drums = np.zeros(N)
fx = np.zeros(N)


def arp(t0, length, chord, step, vel, octave=12, pattern=(0, 1, 2, 1)):
    for i in range(int(round(length / step))):
        place(keys, t0 + i * step, piano(hz(chord[pattern[i % len(pattern)]] + octave), 1.4, vel))


# --- hook: rising tone into a soft, heavy thud ---
tt = np.arange(int(SR * 0.55)) / SR
rise = np.sin(2 * np.pi * np.cumsum(220 + 300 * (tt / 0.55) ** 2) / SR) * (tt / 0.55) ** 2
place(fx, 0.0, rise, 0.10)
place(fx, 0.0, fft_filter(noise(0.55) * (tt / 0.55) ** 3, lo=600, hi=5000), 0.12)
place(fx, 0.55, kick(1.3, 1.2, f0=42, f1=95))
place(fx, 0.55, fft_filter(noise(0.25), hi=900) * np.exp(-np.arange(int(SR * 0.25)) / SR * 14), 0.6)
place(keys, 0.55, piano(hz(38), 3.0, 0.8) + piano(hz(50), 3.0, 0.45))

# --- 0.55–13: the weight ---
for bar in range(7):
    t0 = 1.0 + bar * 2.0
    if t0 >= 13:
        break
    length = min(2.0, 13.0 - t0)
    chord = MINOR[bar % 4]
    place(pads, t0, pad(chord, length + 0.3, harmonics=4 if bar < 3 else 6), 0.5 if bar < 3 else 0.65)
    arp(t0, length, chord, 0.5 if bar < 3 else 0.25, 0.32)
    if t0 >= 3.0:
        for beat in np.arange(0, length, 1.0):
            place(drums, t0 + beat, kick(0.6 if bar < 3 else 0.8))
    if t0 >= 8.0:
        place(bass, t0, piano(hz(chord[0] - 24), length, 1.0))
# a short swell into the drop-out
r = noise(1.0) * np.linspace(0, 1, SR) ** 3
place(fx, 12.0, fft_filter(r, lo=1200, hi=7000), 0.18)

# --- 13–18: almost nothing. He notices. ---
place(pads, 13.0, pad(BB, 5.2, harmonics=3, attack=1.2), 0.55)
for i, (dt, m) in enumerate(((0.4, 74), (1.6, 77), (2.8, 72), (3.9, 74))):
    place(keys, 13.0 + dt, piano(hz(m), 2.4, 0.30))

# --- 18–24: steadier, warmer ---
for bar, chord in enumerate([GM, BB, F]):
    t0 = 18.0 + bar * 2.0
    place(pads, t0, pad(chord, 2.3, harmonics=5, attack=0.3), 0.7)
    arp(t0, 2.0, chord, 0.5, 0.36, pattern=(0, 2, 1, 2))
    place(bass, t0, piano(hz(chord[0] - 24), 2.0, 0.9))
    place(drums, t0, kick(0.5))

# --- 24–30.5: rest. F major, rising arpeggio, rings out ---
for t0, chord, length in ((24.0, (53, 57, 60, 65), 2.0), (26.0, (46, 53, 58, 62), 1.0), (27.0, (53, 57, 60, 65, 69), 3.5)):
    place(pads, t0, pad(chord, length + 0.4, harmonics=6, attack=0.25), 0.9)
    place(bass, t0, piano(hz(chord[0] - 24), length + 0.5, 1.0))
for i, m in enumerate((65, 69, 72, 77, 81, 77, 72, 69)):
    place(keys, 24.0 + i * 0.375, piano(hz(m), 1.8, 0.34))
for i, m in enumerate((72, 77, 81, 84)):
    place(keys, 27.0 + i * 0.22, piano(hz(m), 3.2, 0.42))

keys = reverb(keys)
bass = fft_filter(bass, hi=220)
left = 0.9 * keys + pads[0] + 0.7 * bass + 0.8 * drums + fx
right = 0.9 * np.concatenate([np.zeros(260), keys[:-260]]) + pads[1] + 0.7 * bass + 0.8 * drums + fx
mixdown = np.stack([left, right])
mixdown = np.tanh(1.2 * mixdown / np.max(np.abs(mixdown)))
mixdown *= 0.89 / np.max(np.abs(mixdown))

out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
with wave.open(out, "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((mixdown.T * 32767).astype(np.int16).tobytes())
print(f"music: {out}  {DUR}s")
