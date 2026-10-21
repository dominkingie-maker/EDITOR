"""Original background track for "You can't always see how close you are" (numpy only).

35.5 s, timed to the story:
  0.00–0.75   racing heartbeat into a heavy thud (he falls to his knees — the hook)
  0.75–12     slow heartbeat, low E minor pads, sparse piano (no finish line in sight)
  12–17.5     the crane shot: bright, airy C major swell, high arpeggios (it's just over the hill)
  17.5–22.5   back to him: quiet heartbeat, single notes, lifting as he stands
  22.5–25.7   one step, then another: a kick on every step, rising pad
  25.7–26.6   silence (he freezes at the top)
  26.6–31.5   full warm major as he walks to the line and crosses it
  31.5–35.5   final message: soft resolution, rings out

  python3 music.py music.wav
"""
import sys
import wave

import numpy as np

SR = 44100
DUR = 35.5
N = int(SR * DUR)
rng = np.random.default_rng(23)


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


def heartbeat(t0, strength=1.0):
    place(drums, t0, kick(strength, 0.35, f0=42, f1=78))
    place(drums, t0 + 0.24, kick(0.65 * strength, 0.3, f0=40, f1=72))


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


def reverb(x, length=2.6, decay=0.8, mix=0.36):
    ir = noise(length) * np.exp(-np.arange(int(SR * length)) / SR / decay)
    ir = fft_filter(ir, hi=4500)
    ir /= np.sqrt(np.sum(ir ** 2))
    n = 1 << int(np.ceil(np.log2(len(x) + len(ir))))
    wet = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[: len(x)]
    return x + mix * wet


keys = np.zeros(N)
pads = np.zeros((2, N))
bass = np.zeros(N)
drums = np.zeros(N)
fx = np.zeros(N)


def arp(t0, length, chord, step, vel, octave=12, pattern=(0, 1, 2, 1)):
    for i in range(int(round(length / step))):
        place(keys, t0 + i * step, piano(hz(chord[pattern[i % len(pattern)]] + octave), 1.4, vel))


EM, C, G, D, AM, F = (52, 55, 59), (48, 52, 55), (55, 59, 62), (50, 54, 57), (57, 60, 64), (53, 57, 60)

# --- hook: racing heartbeat, breath of noise, thud ---
for k, t0 in enumerate((0.0, 0.34)):
    heartbeat(t0, 0.9 + 0.2 * k)
tt = np.arange(int(SR * 0.75)) / SR
place(fx, 0.0, fft_filter(noise(0.75) * (tt / 0.75) ** 2, lo=500, hi=4000), 0.12)
place(fx, 0.75, kick(1.5, 1.3, f0=36, f1=90))
place(fx, 0.75, fft_filter(noise(0.3), hi=1000) * np.exp(-np.arange(int(SR * 0.3)) / SR * 12), 0.6)
place(keys, 0.75, piano(hz(40), 3.0, 0.8) + piano(hz(52), 3.0, 0.4))

# --- 0.75–12: the endless road ---
for bar, chord in enumerate([EM, C, G, D, EM]):
    t0 = 2.0 + bar * 2.0
    place(pads, t0, pad(chord, 2.3, harmonics=4, attack=0.6), 0.55)
    for i, m in enumerate((chord[0] + 12, chord[2] + 12)):
        place(keys, t0 + i * 1.0, piano(hz(m), 1.8, 0.30))
for t0 in np.arange(1.6, 11.6, 1.05):
    heartbeat(t0, 0.55)

# --- 12–17.5: the crane shot reveals the finish ---
place(fx, 11.3, fft_filter(noise(0.8) * np.linspace(0, 1, int(SR * 0.8)) ** 3, lo=2000, hi=9000), 0.18)
for t0, chord, length in ((12.0, (48, 55, 60, 62, 64), 2.75), (14.75, (53, 57, 60, 64, 67), 2.75)):
    place(pads, t0, pad(chord, length + 0.4, harmonics=7, attack=0.8), 1.45)
    place(bass, t0, piano(hz(chord[0] - 12), length, 0.6))
    arp(t0 + 0.3, length - 0.3, chord, 0.1875, 0.28, octave=24, pattern=(0, 2, 4, 3, 1, 4))

# --- 17.5–22.5: back to him; he stands ---
place(pads, 17.5, pad(EM, 3.2, harmonics=3, attack=0.8), 0.5)
place(pads, 20.5, pad((48, 55, 60, 64), 2.3, harmonics=5, attack=0.8), 0.7)
for dt, m in ((0.5, 71), (1.7, 67), (2.9, 72), (3.6, 74), (4.3, 76)):
    place(keys, 17.5 + dt, piano(hz(m), 2.2, 0.32))
for t0 in np.arange(17.8, 22.0, 1.2):
    heartbeat(t0, 0.4)

# --- 22.5–25.7: one step, then another ---
steps = [22.7, 23.4, 24.0, 24.55, 25.05, 25.5]
for k, t0 in enumerate(steps):
    place(drums, t0, kick(0.6 + 0.07 * k))
place(pads, 22.5, pad(AM, 1.6, harmonics=6), 0.6)
place(pads, 24.1, pad(F, 1.6, harmonics=7), 0.75)
place(fx, 24.4, fft_filter(noise(1.3) * np.linspace(0, 1, int(SR * 1.3)) ** 3, lo=1500, hi=9000), 0.22)
# 25.7–26.6: silence, one high note
place(keys, 25.75, piano(hz(84), 2.0, 0.28))

# --- 26.6–31.5: across the line ---
for bar, chord in enumerate([C, G, AM]):
    t0 = 26.6 + bar * 1.6
    place(pads, t0, pad(chord + (chord[0] + 12,), 1.9, harmonics=8, attack=0.05), 1.1)
    place(bass, t0, piano(hz(chord[0] - 24), 1.6, 1.1))
    arp(t0, 1.6, chord, 0.2, 0.42, octave=24, pattern=(0, 1, 2, 1))
    for beat in np.arange(0, 1.6, 0.4):
        place(drums, t0 + beat, kick(0.9))
place(fx, 27.9, fft_filter(noise(1.6), lo=3000) * np.exp(-np.arange(int(SR * 1.6)) / SR * 2.5), 0.10)

# --- 31.5–35.5: the message ---
place(pads, 31.4, pad((48, 55, 60, 64, 67), 4.1, harmonics=6, attack=0.3), 1.2)
place(bass, 31.4, piano(hz(36), 4.0, 1.0))
for i, m in enumerate((67, 72, 76, 79, 84)):
    place(keys, 31.5 + i * 0.25, piano(hz(m), 3.0, 0.36))

keys = reverb(keys)
bass = fft_filter(bass, hi=220)
left = 0.9 * keys + pads[0] + 0.7 * bass + 0.8 * drums + fx
right = 0.9 * np.concatenate([np.zeros(240), keys[:-240]]) + pads[1] + 0.7 * bass + 0.8 * drums + fx
mixdown = np.stack([left, right])
mixdown = np.tanh(1.2 * mixdown / np.max(np.abs(mixdown)))
mixdown *= 0.89 / np.max(np.abs(mixdown))

out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
with wave.open(out, "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((mixdown.T * 32767).astype(np.int16).tobytes())
print(f"music: {out}  {DUR}s")
