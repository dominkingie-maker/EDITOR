"""Original background track for "You can care without carrying everything" (numpy only).

120 BPM (one bar = 2 s), 30.5 s, timed to the story:
  0.00–0.55  whoosh into an impact hit (the box slams onto the stack — the hook)
  0.55–8     sparse minor piano + soft pad (Am F C G)
  8–18       kick, bass and a fuller pad build the weight; noise riser into 18 s
  18–27      the turn: brighter major progression, eighth-note piano, light drums
  27–30.5    resolves on C major and rings out

  python3 music.py music.wav
"""
import sys
import wave

import numpy as np

SR = 44100
DUR = 30.5
N = int(SR * DUR)
rng = np.random.default_rng(7)


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
        out += amp * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * t) * np.exp(-t * (2.2 + 1.6 * k))
    return vel * out * np.minimum(t / 0.004, 1)


def pad(notes, dur, harmonics=5, attack=0.5):
    t = np.arange(int(SR * dur)) / SR
    out = np.zeros((2, len(t)))
    for m in notes:
        for ch, det in enumerate((0.9985, 1.0015)):
            f = hz(m) * det
            for k in range(1, harmonics + 1):
                out[ch] += np.sin(2 * np.pi * f * k * t + k) / k
    env = np.minimum(t / attack, 1) * np.minimum((dur - t) / 0.5, 1)
    return out * env / (len(notes) * 2.5)


def kick(strength=1.0, length=0.45, f0=55, f1=150):
    t = np.arange(int(SR * length)) / SR
    f = f0 + (f1 - f0) * np.exp(-t * 32)
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


def reverb(x, length=1.8, decay=0.55, mix=0.28):
    ir = noise(length) * np.exp(-np.arange(int(SR * length)) / SR / decay)
    ir = fft_filter(ir, hi=5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    n = 1 << int(np.ceil(np.log2(len(x) + len(ir))))
    wet = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[: len(x)]
    return x + mix * wet


A_PROG = [(57, 60, 64), (53, 57, 60), (55, 60, 64), (55, 59, 62)]          # Am F C/G G
B_PROG = [(53, 57, 60), (55, 59, 62), (57, 60, 64), (53, 57, 60), (55, 59, 62)]  # F G Am F G
C_MAJ = (48, 55, 60, 64, 67)

keys = np.zeros(N)
pads = np.zeros((2, N))
bass = np.zeros(N)
drums = np.zeros(N)
fx = np.zeros(N)

# --- hook: whoosh into an impact ---
w = noise(0.6) * np.linspace(0, 1, int(SR * 0.6)) ** 2
place(fx, 0.0, fft_filter(w, lo=400, hi=6000), 0.22)
place(fx, 0.55, kick(1.6, 1.6, f0=38, f1=110), 0.7)
place(fx, 0.55, fft_filter(noise(0.5), hi=1800) * np.exp(-np.arange(int(SR * 0.5)) / SR * 9), 0.5)
place(keys, 0.55, piano(hz(45), 3.0, 0.9) + piano(hz(57), 3.0, 0.5))

# --- part A: 0.55–18 ---
for bar in range(9):
    t0 = bar * 2.0
    chord = A_PROG[bar % 4]
    if t0 >= 2.0:
        notes = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[1] + 12]
        step = 0.5 if bar < 4 else 0.25
        for i in range(int(2.0 / step)):
            m = notes[i % 4] + (12 if (bar >= 4 and i % 8 == 6) else 0)
            place(keys, t0 + i * step, piano(hz(m), 1.4, 0.32 + 0.03 * (i % 2 == 0)))
    if bar == 0:
        place(pads, 0.6, pad(chord, 1.6, harmonics=4, attack=0.3), 0.45)
    else:
        place(pads, t0, pad(chord, 2.2, harmonics=4 if bar < 4 else 6), 0.5 if bar < 4 else 0.6)
    if bar >= 4:
        place(bass, t0, piano(hz(chord[0] - 24), 2.0, 1.0))
        for beat in (0.0, 1.0) if bar < 7 else (0.0, 0.5, 1.0, 1.5):
            place(drums, t0 + beat, kick(0.55))

# riser 15.5 -> 18, then a breath of silence before the turn
r_len = 2.35
r = noise(r_len) * np.linspace(0, 1, int(SR * r_len)) ** 3
place(fx, 15.5, fft_filter(r, lo=1500, hi=9000), 0.30)
for k in range(8):
    place(drums, 16.0 + k * 0.25, fft_filter(noise(0.12), lo=900, hi=5000) * np.exp(-np.arange(int(SR * 0.12)) / SR * 30), 0.06 + 0.03 * k)

# --- part B: 18–27 (the turn) ---
for bar, chord in enumerate(B_PROG):
    t0 = 18.0 + bar * 2.0
    length = 2.0 if bar < 4 else 1.0
    place(pads, t0, pad(chord, length + 0.3, harmonics=8, attack=0.08), 1.0)
    place(bass, t0, piano(hz(chord[0] - 24), length, 1.1))
    notes = [chord[0] + 24, chord[2] + 12, chord[1] + 24, chord[2] + 12]
    for i in range(int(length / 0.25)):
        place(keys, t0 + i * 0.25, piano(hz(notes[i % 4]), 1.2, 0.5))
    for beat in np.arange(0, length, 0.5):
        place(drums, t0 + beat, kick(1.1))
        place(drums, t0 + beat + 0.25, fft_filter(noise(0.05), lo=7000) * np.exp(-np.arange(int(SR * 0.05)) / SR * 70), 0.10)
    for beat in (0.5, 1.5):
        if beat < length:
            place(drums, t0 + beat, fft_filter(noise(0.18), lo=1200, hi=6000) * np.exp(-np.arange(int(SR * 0.18)) / SR * 22), 0.32)

# --- ending: C major rings out ---
place(pads, 27.0, pad(C_MAJ, 3.5, harmonics=6, attack=0.05), 1.3)
place(bass, 27.0, piano(hz(36), 3.5, 1.1))
for i, m in enumerate((72, 76, 79, 84)):
    place(keys, 27.0 + i * 0.18, piano(hz(m), 3.0, 0.8))
place(drums, 27.0, kick(1.0))

# sidechain duck on the pad during part B
t = np.arange(N) / SR
duck = np.ones(N)
for k in np.arange(18.0, 27.0, 0.5):
    m = t >= k
    duck[m] *= 1 - 0.35 * np.exp(-(t[m] - k) / 0.12)
pads *= duck

keys = reverb(keys, mix=0.35)
bass = fft_filter(bass, hi=220)
left = 0.9 * keys + pads[0] + 0.7 * bass + 0.8 * drums + fx
right = 0.9 * np.concatenate([np.zeros(220), keys[:-220]]) + pads[1] + 0.7 * bass + 0.8 * drums + fx
mixdown = np.stack([left, right])
mixdown = np.tanh(1.2 * mixdown / np.max(np.abs(mixdown)))
mixdown *= 0.89 / np.max(np.abs(mixdown))

out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
with wave.open(out, "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((mixdown.T * 32767).astype(np.int16).tobytes())
print(f"music: {out}  {DUR}s")
