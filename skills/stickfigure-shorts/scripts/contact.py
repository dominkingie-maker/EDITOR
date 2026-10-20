"""Contact sheet of full frames at chosen times — the main way to check a story before rendering.

  python3 contact.py episode.py 0,0.6,2.8,5.4,12.5 --out sheet.png [--cols 4] [--crop 540,1560]

Pick times at the beats that matter: frame 0 (the hook), every impact, every reveal, every caption
change, the end card. The crop keeps the caption band + content area (y 540..1560) by default.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine  # noqa: E402
from PIL import Image  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("times", help="comma-separated seconds")
    ap.add_argument("--out", default="sheet.png")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--crop", default="540,1560", help="y0,y1 of the frame to keep")
    a = ap.parse_args()
    engine._init(a.episode)
    y0, y1 = (int(v) for v in a.crop.split(","))
    times = [float(v) for v in a.times.split(",")]
    tw, th = 432, int(432 * (y1 - y0) / engine.W)
    ims = [Image.fromarray(engine._rgb(int(t * engine.FPS))).crop((0, y0, engine.W, y1)).resize((tw, th))
           for t in times]
    rows = (len(ims) + a.cols - 1) // a.cols
    sheet = Image.new("RGB", (tw * a.cols, th * rows))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % a.cols) * tw, (i // a.cols) * th))
    sheet.save(a.out)
    print(f"sheet: {a.out}  {len(ims)} frames  total={engine._EP['total']:.1f}s")


if __name__ == "__main__":
    main()
