"""score — a tiny numpy synth for original, story-timed background music (no samples, no licences).

A score file defines DUR (seconds), optional MARKS (times to report loudness at) and compose(s):

    DUR = 30.5
    MARKS = [0.6, 5, 12, 18.5, 28]
    def compose(s):
        s.whoosh(0.0, 0.55); s.thud(0.55)                 # the hook hit
        for i, ch in enumerate([AM, F, C, G]):
            s.pad(2 + 2 * i, ch, 2.2); s.arp(2 + 2 * i, 2.0, ch, 0.5, 0.32)
        ...

    python3 score.py my_score.py --out music.wav

The report prints RMS dB at each MARK so you can check the arc without listening:
intro ≈ -22…-26, build ≈ -15…-18, payoff ≈ -12…-14, a "silence" beat ≈ -25 or lower.
"""
import argparse
import importlib.util
import sys
import wave

import numpy as np

SR = 44100

# common chords (MIDI, middle register); add 12 for an octave up
AM, C, D, DM, EM, F, G, GM, BB = ((57, 60, 64), (48, 52, 55), (50, 54, 57), (50, 53, 57), (52, 55, 59),
                                  (53, 57, 60), (55, 59, 62), (55, 58, 62), (46, 50, 53))
C_MAJ_WIDE = (48, 55, 60, 64, 67)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


class Score:
    def __init__(self, dur, seed=0):
        self.dur, self.n = dur, int(SR * dur)
        self.rng = np.random.default_rng(seed)
        self.keys = np.zeros(self.n)
        self.pads = np.zeros((2, self.n))
        self.bass_ = np.zeros(self.n)
        self.drums = np.zeros(self.n)
        self.fx = np.zeros(self.n)

    # ---- low level
    def _place(self, buf, start, sig, gain=1.0):
        i = int(start * SR)
        n = buf.shape[-1]
        if i >= n or start < 0:
            return
        sig = sig[..., : n - i]
        buf[..., i:i + sig.shape[-1]] += gain * sig   # works for mono and (2, N) stereo buffers

    def _t(self, dur):
        return np.arange(int(SR * dur)) / SR

    def noise(self, dur):
        return self.rng.standard_normal(int(SR * dur))

    @staticmethod
    def filt(x, lo=None, hi=None):
        X = np.fft.rfft(x)
        f = np.fft.rfftfreq(len(x), 1 / SR)
        m = np.ones_like(f)
        if lo:
            m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
        if hi:
            m *= 1 / (1 + (f / hi) ** 4)
        return np.fft.irfft(X * m, len(x))

    def _piano_sig(self, f, dur, vel):
        t = self._t(dur)
        out = np.zeros_like(t)
        for k, amp in enumerate((1.0, 0.45, 0.22, 0.1, 0.05), start=1):
            out += amp * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * t) * np.exp(-t * (2.0 + 1.5 * k))
        return vel * out * np.minimum(t / 0.004, 1)

    def _kick_sig(self, strength, length, f0, f1):
        t = self._t(length)
        f = f0 + (f1 - f0) * np.exp(-t * 30)
        return strength * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)

    # ---- instruments
    def piano(self, t, midi, dur=1.6, vel=0.32):
        self._place(self.keys, t, self._piano_sig(hz(midi), dur, vel))

    def notes(self, t0, seq, dur=2.2, vel=0.30):
        """seq = [(dt, midi), ...] — sparse single notes (sad / reflective moments)."""
        for dt, m in seq:
            self.piano(t0 + dt, m, dur, vel)

    def arp(self, t0, length, chord, step=0.5, vel=0.32, octave=12, pattern=(0, 1, 2, 1)):
        for i in range(int(round(length / step))):
            self.piano(t0 + i * step, chord[pattern[i % len(pattern)] % len(chord)] + octave, 1.4, vel)

    def pad(self, t0, chord, dur, gain=0.6, harmonics=5, attack=0.5):
        """Warm detuned pad (stereo). More harmonics = brighter; long attack = swell."""
        t = self._t(dur)
        out = np.zeros((2, len(t)))
        for m in chord:
            for ch, det in enumerate((0.9985, 1.0015)):
                for k in range(1, harmonics + 1):
                    out[ch] += np.sin(2 * np.pi * hz(m) * det * k * t + k) / k
        env = np.minimum(t / attack, 1) * np.minimum((dur - t) / 0.6, 1)
        self._place(self.pads, t0, out * env / (len(chord) * 2.5), gain)

    def bass(self, t0, midi, dur=2.0, vel=1.0):
        self._place(self.bass_, t0, self._piano_sig(hz(midi), dur, vel))

    def kick(self, t, strength=0.8, length=0.45, f0=50, f1=140):
        self._place(self.drums, t, self._kick_sig(strength, length, f0, f1))

    def heartbeat(self, t, strength=0.55):
        self._place(self.drums, t, self._kick_sig(strength, 0.35, 42, 78))
        self._place(self.drums, t + 0.24, self._kick_sig(0.65 * strength, 0.3, 40, 72))

    def hat(self, t, gain=0.10):
        self._place(self.drums, t, self.filt(self.noise(0.05), lo=7000) * np.exp(-self._t(0.05) * 70), gain)

    def clap(self, t, gain=0.30):
        self._place(self.drums, t, self.filt(self.noise(0.18), lo=1200, hi=6000) * np.exp(-self._t(0.18) * 22), gain)

    # ---- sound design for story beats
    def thud(self, t, strength=1.0):
        """Heavy impact: falls, a box slamming down, knees hitting the road."""
        self._place(self.fx, t, self._kick_sig(1.3 * strength, 1.1, 38, 92))
        self._place(self.fx, t, self.filt(self.noise(0.28), hi=1000) * np.exp(-self._t(0.28) * 12), 0.5 * strength)

    def whoosh(self, t, dur=0.55, gain=0.2):
        """Rising noise INTO a hit at t + dur (frame-0 hooks)."""
        self._place(self.fx, t, self.filt(self.noise(dur) * (self._t(dur) / dur) ** 2, lo=400, hi=6000), gain)

    def riser(self, t, dur=1.5, gain=0.25):
        """Tension build ending at t + dur — leave a beat of near-silence after it for a reveal."""
        self._place(self.fx, t, self.filt(self.noise(dur) * (self._t(dur) / dur) ** 3, lo=1500, hi=9000), gain)

    def shimmer(self, t, dur=1.6, gain=0.10):
        """Cymbal-like wash for a payoff (crossing a line, a lift locking out)."""
        self._place(self.fx, t, self.filt(self.noise(dur), lo=3000) * np.exp(-self._t(dur) * 2.5), gain)

    def hook_hit(self, t, kind="slam"):
        """The sound of the hook, landing exactly on the visual hit at t (put it in EVERY score).
        slam: whoosh into a heavy thud + low note · snap: short whoosh, punchy kick, shimmer ·
        rewind: tape-stop sweep down ending at t (cold-open flash-forward)."""
        if kind == "slam":
            self.whoosh(max(0.0, t - 0.55), min(0.55, t), 0.2)
            self.thud(t)
            self.piano(t, 40, 2.6, 0.6)
        elif kind == "snap":
            self.whoosh(max(0.0, t - 0.3), min(0.3, t), 0.16)
            self.kick(t, 1.2, 0.6, 45, 160)
            self.shimmer(t, 1.0, 0.08)
        elif kind == "rewind":
            d = 0.45
            tt = self._t(d)
            f = 700 * np.exp(-tt / d * 2.4) + 40
            sweep = np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - tt / d)
            self._place(self.fx, t - d, sweep, 0.35)
            self._place(self.fx, t - d, self.filt(self.noise(d), lo=800, hi=5000) * (1 - tt / d), 0.12)

    def duck(self, t0, t1, every=0.5, depth=0.35):
        """Sidechain the pads to a beat grid between t0 and t1 (pumping energy for a payoff section)."""
        t = np.arange(self.n) / SR
        g = np.ones(self.n)
        for k in np.arange(t0, t1, every):
            m = t >= k
            g[m] *= 1 - depth * np.exp(-(t[m] - k) / 0.12)
        self.pads *= g

    # ---- output
    def _reverb(self, x, length=2.4, decay=0.75, mix=0.34):
        ir = self.noise(length) * np.exp(-self._t(length) / decay)
        ir = self.filt(ir, hi=4500)
        ir /= np.sqrt(np.sum(ir ** 2))
        n = 1 << int(np.ceil(np.log2(len(x) + len(ir))))
        return x + mix * np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[: len(x)]

    def render(self):
        keys = self._reverb(self.keys)
        bass = self.filt(self.bass_, hi=220)
        delayed = np.concatenate([np.zeros(240), keys[:-240]])
        mixd = np.stack([0.9 * keys + self.pads[0] + 0.7 * bass + 0.8 * self.drums + self.fx,
                         0.9 * delayed + self.pads[1] + 0.7 * bass + 0.8 * self.drums + self.fx])
        mixd = np.tanh(1.2 * mixd / np.max(np.abs(mixd)))
        return mixd * 0.89 / np.max(np.abs(mixd))

    def write(self, path, marks=()):
        mixd = self.render()
        with wave.open(path, "wb") as wf:
            wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
            wf.writeframes((mixd.T * 32767).astype(np.int16).tobytes())
        print(f"music: {path}  {self.dur}s")
        for m in marks:
            seg = mixd[0, int(m * SR):int((m + 0.4) * SR)]
            print(f"  {m:6.2f}s  {20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9):6.1f} dB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("score_file")
    ap.add_argument("--out", default="music.wav")
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("score_file", a.score_file)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["score_file"] = mod
    spec.loader.exec_module(mod)
    s = Score(mod.DUR, getattr(mod, "SEED", 0))
    mod.compose(s)
    s.write(a.out, getattr(mod, "MARKS", ()))


if __name__ == "__main__":
    sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
    import score
    score.main()
