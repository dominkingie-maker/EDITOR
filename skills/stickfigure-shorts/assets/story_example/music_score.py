"""Score for "Keep going" — rendered with:  python3 <skill>/scripts/score.py music_score.py --out music.wav

Sections follow the scene timeline in episode.py (scene starts: 0, 4, 9, 12.5, 18, 22.5, 28.5, 34.5, 37).
"""
from score import AM, C, EM, F, G, D

DUR = 41.8
SEED = 31
MARKS = [0.1, 0.75, 3, 5.35, 8.25, 10.5, 13, 16, 19.5, 24, 27, 28.8, 30, 32, 35, 37.5, 39.1, 41]
STEP_STARTS = [0.4, 1.3, 2.2, 3.0, 3.7, 4.3, 4.9]   # same list as episode.py (scene 6 starts at 22.5)


def compose(s):
    # hook: racing heartbeat, a jolt as he nearly goes down by the sign
    s.heartbeat(0.0, 1.0); s.heartbeat(0.34, 1.1)
    s.thud(0.7, 0.7); s.piano(0.7, 40, 2.6, 0.6)

    # 0.7–9: the endless road, two falls
    for bar, ch in enumerate([EM, C, G, D]):
        t0 = 1.2 + bar * 2.0
        s.pad(t0, ch, 2.3, 0.55, harmonics=4, attack=0.6)
        s.notes(t0, [(0, ch[0] + 12), (1.0, ch[2] + 12)], 1.8, 0.28)
    for t0 in range(14, 89, 10):
        s.heartbeat(t0 / 10, 0.55)
    s.thud(5.3); s.thud(8.2, 1.1)

    # 9–12.5: ready to give up
    s.pad(9.0, (40, 47, 52, 55), 3.8, 0.6, harmonics=3, attack=0.8)
    s.notes(9.0, [(0.4, 71), (1.4, 67), (2.4, 64)], 2.4, 0.30)

    # 12.5–18: the crane shot reveals the finish line
    s.riser(11.8, 0.8, 0.18)
    for t0, ch in ((12.5, (48, 55, 60, 62, 64)), (15.25, (53, 57, 60, 64, 67))):
        s.pad(t0, ch, 3.15, 1.45, harmonics=7, attack=0.8)
        s.bass(t0, ch[0] - 12, 2.75, 0.6)
        s.arp(t0 + 0.3, 2.45, ch, 0.1875, 0.28, octave=24, pattern=(0, 2, 4, 3, 1, 4))

    # 18–22.5: trembling hands, he pushes himself up
    s.pad(18.0, EM, 3.2, 0.5, harmonics=3, attack=0.8)
    s.pad(21.0, (48, 55, 60, 64), 1.8, 0.7, attack=0.8)
    s.notes(18.0, [(0.5, 71), (1.6, 67), (2.6, 72), (3.3, 74), (4.0, 76)], 2.2, 0.32)
    for t0 in (18.3, 19.5, 20.7, 21.9):
        s.heartbeat(t0, 0.4)

    # 22.5–28.5: he walks — a soft kick on every footfall
    for k, st in enumerate(STEP_STARTS):
        s.kick(22.5 + st + 0.6, 0.55 + 0.06 * k)
    for t0, ch in ((22.5, AM), (24.5, F), (26.5, G)):
        s.pad(t0, ch, 2.3, 0.65, harmonics=6)
        s.arp(t0, 2.0, ch, 0.5, 0.30, pattern=(0, 2, 1, 2))
        s.bass(t0, ch[0] - 24, 2.0, 0.8)
    s.riser(27.2, 1.3, 0.22)

    # 28.5–29.5: silence at the crest, one high note
    s.piano(28.6, 84, 2.0, 0.28)

    # 29.5–34.5: he smiles, and walks across
    s.pad(29.5, (48, 55, 60, 64), 1.6, 0.9, harmonics=6)
    for bar, ch in enumerate([C, G, AM, F]):
        t0 = 31.0 + bar * 0.9
        s.pad(t0, ch + (ch[0] + 12,), 1.2, 1.1, harmonics=8, attack=0.05)
        s.bass(t0, ch[0] - 24, 0.9, 1.1)
        s.arp(t0, 0.9, ch, 0.15, 0.40, octave=24)
        s.kick(t0, 0.85); s.kick(t0 + 0.45, 0.85)
    s.shimmer(32.7)

    # 34.5–37: pulling away
    s.pad(34.6, (48, 55, 60, 64, 67), 2.8, 1.0, harmonics=6, attack=0.1)
    s.bass(34.6, 36, 2.6, 0.9)
    s.notes(34.7, [(0, 84), (0.4, 79), (0.8, 76), (1.2, 72)], 2.0, 0.30)

    # 37–41.8: the message; a warm hit as KEEP GOING appears (38.9)
    s.pad(37.0, (45, 52, 57, 60), 1.9, 0.6, harmonics=4, attack=0.6)
    s.notes(37.2, [(0, 64), (0.5, 67), (1.0, 69)], 2.0, 0.30)
    s.kick(38.9, 1.0, 0.8, 40, 110)
    s.pad(38.9, (48, 55, 60, 64, 67, 72), 2.9, 1.3, harmonics=7, attack=0.05)
    s.bass(38.9, 36, 2.9, 1.0)
    s.notes(38.9, [(0, 72), (0.16, 76), (0.32, 79), (0.48, 84)], 2.6, 0.42)
