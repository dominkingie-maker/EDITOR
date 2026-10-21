"""Bed for "Section 7 - Right to Information" (original, numpy only), rendered with
    python3 skills/stickfigure-shorts/scripts/score.py music_score.py --out music.wav
and mixed about 18 dB under the voice by build.py. Sections follow the edit (seconds, edited time):
  0-6.3 intro   6.3-14.5 what it means   14.5-26.6 example + questions (pulse)
  26.6-32.8 limitations (tension)   32.8-39.4 why it matters (build)   39.4-45.5 closing (warm)
  45.5-48.5 thank-you card (resolve)
"""
from score import AM, C, DM, EM, F, G

DUR = 48.5
SEED = 7
MARKS = [1, 8, 16, 22, 29, 36, 42, 46.5]
BAR = 2.4                     # 100 bpm, four beats


def compose(s):
    s.pad(0.0, (45, 52, 57, 60), 6.3, 0.5, harmonics=4, attack=0.3)
    s.bass(0.0, 33, 3.0, 0.7)
    s.notes(1.2, [(0, 69), (1.2, 72), (2.4, 76)], 2.4, 0.22)

    t = 6.3
    for ch in (AM, F, C, G):                           # what it means: calm, steady
        s.pad(t, ch, BAR + 0.2, 0.55, harmonics=4, attack=0.4)
        s.bass(t, ch[0] - 24, BAR, 0.6)
        t += BAR
    s.notes(6.3, [(0, 76), (2.4, 77), (4.8, 79), (7.2, 74)], 2.2, 0.20)

    t = 14.5
    while t < 26.5:                                    # example + questions: gentle pulse
        ch = (AM, F, C, G)[int((t - 14.5) / BAR) % 4]
        s.pad(t, ch, BAR + 0.2, 0.6, harmonics=5, attack=0.2)
        s.bass(t, ch[0] - 24, BAR, 0.75)
        s.arp(t, BAR, ch, 0.3, 0.18, pattern=(0, 2, 1, 2))
        for b in range(4):
            s.kick(t + b * 0.6, 0.35, 0.3)
        t += BAR

    s.pad(26.6, DM, 3.1, 0.55, harmonics=3, attack=0.6)   # limitations: held tension
    s.pad(29.7, EM, 3.1, 0.55, harmonics=3, attack=0.6)
    for k in range(10):
        s.heartbeat(26.9 + k * 0.6, 0.3)

    t = 32.8
    for ch in (F, G, AM):                              # why it matters: build
        s.pad(t, ch, BAR + 0.2, 0.7, harmonics=6, attack=0.15)
        s.bass(t, ch[0] - 24, BAR, 0.8)
        s.arp(t, BAR, ch, 0.15, 0.2, octave=24)
        for b in range(4):
            s.kick(t + b * 0.6, 0.45, 0.3)
        t += BAR
    s.riser(38.2, 1.1, 0.12)

    t = 39.4
    for ch in (C, G, AM, F):                           # closing: warm major
        s.pad(t, ch + (ch[0] + 12,), 1.6, 0.8, harmonics=6, attack=0.1)
        s.bass(t, ch[0] - 24, 1.5, 0.8)
        s.arp(t, 1.5, ch, 0.25, 0.22, octave=12)
        t += 1.52

    s.pad(45.5, (48, 55, 60, 64, 67), 3.0, 1.0, harmonics=6, attack=0.05)   # thank you
    s.bass(45.5, 36, 3.0, 0.9)
    s.notes(45.5, [(0, 72), (0.2, 76), (0.4, 79), (0.6, 84)], 2.4, 0.32)
    s.shimmer(45.5, 2.4, 0.08)
