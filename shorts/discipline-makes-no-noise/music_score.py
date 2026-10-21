"""Score for "Discipline makes no noise" — python3 <skill>/scripts/score.py music_score.py --out music.wav

Scene starts: 0, 4.5, 9.0, 13.0, 19.0, 24.0, 28.5, 32.5 (end 37.0).
"""
from score import AM, C, EM, F, G

DUR = 37.5
SEED = 41
MARKS = [0.1, 0.4, 1.35, 2.5, 5.5, 6.85, 10, 11.65, 13.5, 15, 17, 18.5, 20.5, 23.6, 25.1, 27, 30, 33, 34.5, 36.5]


def compose(s):
    # hook: the flash-forward pass (0.35), then the tape rewinds into the start (1.3)
    s.hook_hit(0.35, "snap")
    s.hook_hit(1.3, "rewind")

    # 1.3–9: jogging rhythm, they laugh, he falls
    for bar, ch in enumerate([AM, EM, AM, EM]):
        t0 = 1.3 + bar * 1.9
        s.pad(t0, ch, 2.1, 0.5, harmonics=4, attack=0.3)
        s.arp(t0, 1.9, ch, 0.475, 0.26, pattern=(0, 2, 1, 2))
        for b in range(4):
            s.hat(t0 + b * 0.475 + 0.24, 0.07)
    for t0 in (2.2, 2.6):                            # "HA!" — two mocking high notes each
        s.piano(t0, 81, 0.6, 0.22); s.piano(t0 + 0.12, 84, 0.6, 0.18)
    s.thud(6.8)                                     # he trips and falls

    # 9–13: the next morning; he runs, he falls again
    s.pad(9.0, (48, 55, 60, 64), 2.6, 0.6, harmonics=5, attack=0.8)
    s.notes(9.0, [(0.3, 72), (1.0, 76), (1.7, 79)], 2.0, 0.28)
    for t0 in (10.0, 10.5, 11.0):
        s.kick(t0, 0.45)
    s.thud(11.6, 0.8)
    s.pad(11.7, EM, 1.4, 0.5, harmonics=3)

    # 13–19: days pass — a running pulse that keeps building; a hit on every DAY change
    for k, (t0, ch) in enumerate(((13.0, AM), (14.5, F), (16.0, C), (17.5, G))):
        s.pad(t0, ch, 1.7, 0.55 + 0.1 * k, harmonics=4 + k)
        s.arp(t0, 1.5, ch, 0.25 if k >= 2 else 0.375, 0.26 + 0.03 * k, octave=12 + 12 * (k >= 2))
        s.kick(t0, 0.9)
        for b in range(6):
            s.kick(t0 + b * 0.25, 0.35 + 0.08 * k) if b % 2 else None
    tt = s._t(1.5)
    s._place(s.fx, 13.0, s.filt(s.noise(1.5), lo=2500, hi=8000) * 0.5 * (1 - (tt / 1.5) ** 4), 0.18)   # rain

    # 19–24: one day they come back; quiet, then a riser
    s.pad(19.0, AM, 3.5, 0.55, harmonics=3, attack=1.0)
    s.notes(19.0, [(0.5, 69), (1.6, 72), (2.6, 71)], 2.2, 0.28)
    for t0 in (21.0, 21.5, 22.0, 22.5, 23.0, 23.5):
        s.hat(t0, 0.05)
    s.riser(22.6, 1.6, 0.26)

    # 24–32.5: someone passes them — the drop
    s.whoosh(24.6, 0.4, 0.22)
    s.kick(25.0, 1.3, 0.6, 45, 160); s.shimmer(25.0)
    for bar, ch in enumerate([C, G, AM, F]):
        t0 = 25.0 + bar * 1.875
        s.pad(t0, ch + (ch[0] + 12,), 2.0, 1.0, harmonics=8, attack=0.05)
        s.bass(t0, ch[0] - 24, 1.875, 1.0)
        s.arp(t0, 1.875, ch, 0.234, 0.38, octave=24)
        for b in range(4):
            s.kick(t0 + b * 0.469, 0.9)
            s.clap(t0 + b * 0.469 + 0.234, 0.18) if b % 2 else s.hat(t0 + b * 0.469 + 0.234, 0.08)
    s.duck(25.0, 32.5, 0.469, 0.3)

    # 32.5–37: the message; quiet line, then a warm hit on RESULTS DO. (34.4)
    s.pad(32.5, (45, 52, 57, 60), 1.9, 0.6, harmonics=4, attack=0.4)
    s.notes(32.6, [(0, 64), (0.5, 67)], 2.0, 0.3)
    s.kick(34.4, 1.1, 0.8, 40, 110)
    s.pad(34.4, (48, 55, 60, 64, 67, 72), 3.1, 1.25, harmonics=7, attack=0.05)
    s.bass(34.4, 36, 3.0, 1.0)
    s.notes(34.4, [(0, 72), (0.16, 76), (0.32, 79), (0.48, 84)], 2.6, 0.42)
