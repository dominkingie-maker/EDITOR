"""Hook gate: measures the first 1.5 s of an episode and fails weak openings.

  python3 hookcheck.py episode.py            # prints metrics + PASS / FAIL (exit code 1 on FAIL)

What it measures (content band y 540..1560, grayscale, 270x255 thumbnails):
  lit0    % of pixels clearly lit on frame 0         -> something big is on screen immediately
  move0   mean change between frames 0.0 and 0.2 s   -> it is already moving
  hit     biggest single 0.1 s change before 1.2 s   -> a punch lands early (impact, snap, reveal)
  hit_t   when that happens
Thresholds were calibrated on finished episodes: strong hooks (box slam, knees on the road, face
covered by a box, FINISH LINE AHEAD stumble) pass; a calm walk-in or a template that eases in fails.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine  # noqa: E402
from PIL import Image  # noqa: E402

LIT0_MIN = 2.0      # %
MOVE0_MIN = 1.0
HIT_MIN = 6.0
HIT_BY = 1.2        # s


def thumb(t):
    im = Image.fromarray(engine._rgb(int(round(t * engine.FPS)))).crop((0, 540, engine.W, 1560))
    return np.asarray(im.convert("L").resize((270, 255)), np.float32)


def measure(path):
    engine._init(path)
    ts = [round(0.1 * k, 1) for k in range(16)]
    fr = {t: thumb(t) for t in ts}
    lit0 = float((fr[0.0] > 60).mean() * 100)
    move0 = float(np.abs(fr[0.2] - fr[0.0]).mean())
    diffs = [(float(np.abs(fr[b] - fr[a]).mean()), b) for a, b in zip(ts, ts[1:]) if b <= HIT_BY]
    hit, hit_t = max(diffs)
    return dict(lit0=lit0, move0=move0, hit=hit, hit_t=hit_t)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    m = measure(sys.argv[1])
    checks = [("lit0", m["lit0"] >= LIT0_MIN, f"{m['lit0']:.1f}% lit on frame 0 (need ≥ {LIT0_MIN})"),
              ("move0", m["move0"] >= MOVE0_MIN, f"motion 0→0.2 s = {m['move0']:.2f} (need ≥ {MOVE0_MIN})"),
              ("hit", m["hit"] >= HIT_MIN, f"biggest 0.1 s change = {m['hit']:.1f} at {m['hit_t']:.1f} s "
                                           f"(need ≥ {HIT_MIN} before {HIT_BY} s)")]
    for name, ok, msg in checks:
        print(f"  {'ok  ' if ok else 'FAIL'} {name:6s} {msg}")
    passed = all(ok for _, ok, _ in checks)
    print("HOOK PASS" if passed else "HOOK FAIL — strengthen the opening (see references/hooks.md)")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
