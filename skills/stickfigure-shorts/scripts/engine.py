"""Rendering engine for minimal glowing stick-figure Shorts.

An *episode* is a Python file that defines `EPISODE = dict(scenes=[...], ...)`.
Each scene is a `Scene(draw_fn, duration)` where `draw_fn(ctx, t)` draws onto a
transparent 1080x1920 cairo context at local time `t` (seconds, starting at 0).
The engine handles fade-to-black transitions, bloom, watermark, encoding and music.

CLI:
  python3 engine.py EPISODE.py --preview sheet.png        # contact sheet (fast check)
  python3 engine.py EPISODE.py --frames 3.0,9.5 --outdir d  # full-res stills
  python3 engine.py EPISODE.py --out video.mp4 [--music track.mp3 --music-start 12]
"""
import argparse, importlib.util, math, os, subprocess, sys
from dataclasses import dataclass
from multiprocessing import Pool

import cairo
import numpy as np
from PIL import Image, ImageFilter

W, H, FPS = 1080, 1920, 30
TEXT_Y1, TEXT_Y2 = 600, 662          # caption baselines (upper third)
CONTENT_TOP, CONTENT_BOTTOM = 720, 1560  # where the visual metaphor lives
CX = W / 2
GOLD = (1.0, 0.76, 0.22)
TEAL = (0.16, 0.86, 0.74)
RED = (0.95, 0.30, 0.28)
FONT = "Inter"

# Per-episode style, overridden by EPISODE settings.
STYLE = dict(accent=GOLD, watermark="", bloom=0.85, fade_out=0.4, black=2 / FPS, fade_in=0.45,
             end_fade=0.6)


@dataclass
class Scene:
    draw: callable
    duration: float
    name: str = "custom"      # template name, recorded in the episode history
    caption: str = ""         # recorded in the episode history


# ---------- easing ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def ease(x):
    """Smoothstep 0..1 — use for fades."""
    x = clamp(x)
    return x * x * (3 - 2 * x)

def eio(x):
    """Cubic ease-in-out 0..1 — use for movement."""
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2

def lerp(a, b, k):
    return a + (b - a) * k

def accent():
    return STYLE["accent"]


# ---------- text ----------
def _font(ctx, size, bold=False):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)

def words(ctx, text, y, t0, t, size=40, col=(1, 1, 1), accent_words=(), step=0.16, max_w=W - 140):
    """Centered caption line; words fade and rise in one after another from t0.
    Words listed in accent_words (exact tokens, e.g. "starts.") use the accent colour."""
    _font(ctx, size)
    ws = text.split(" ")
    space = ctx.text_extents(" ").x_advance
    widths = [ctx.text_extents(w).x_advance for w in ws]
    total = sum(widths) + space * (len(ws) - 1)
    if total > max_w:  # auto-shrink long lines instead of overflowing
        return words(ctx, text, y, t0, t, size * max_w / total, col, accent_words, step, max_w)
    x = (W - total) / 2
    for i, w in enumerate(ws):
        a = ease((t - t0 - i * step) / 0.3)
        if a > 0:
            ctx.set_source_rgba(*(accent() if w in accent_words else col), a)
            ctx.move_to(x, y + (1 - a) * 10)
            ctx.show_text(w)
        x += widths[i] + space
    ctx.new_path()  # show_text leaves a current point; don't let the next shape connect to it

def caption(ctx, t, line1, line2="", t2=2.4, accent_words=()):
    """Standard two-line caption: setup at t=0, payoff at t2."""
    words(ctx, line1, TEXT_Y1, 0.0, t, accent_words=accent_words,
          step=0.16 if len(line1) < 26 else 0.12)
    if line2:
        words(ctx, line2, TEXT_Y2, t2, t, accent_words=accent_words)

def label(ctx, text, x, y, a, size=30, col=(0.75, 0.75, 0.75), align="center", bold=False):
    """Small static label (alpha a). align: center | left | right."""
    if a <= 0:
        return
    _font(ctx, size, bold)
    w = ctx.text_extents(text).x_advance
    ctx.set_source_rgba(*col, a)
    ctx.move_to(x + {"center": -w / 2, "left": 0, "right": -w}[align], y)
    ctx.show_text(text)
    ctx.new_path()


# ---------- shapes ----------
def rounded_rect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()

def ellipse(ctx, cx, cy, rx, ry):
    ctx.new_path()
    ctx.save(); ctx.translate(cx, cy); ctx.scale(1, ry / rx)
    ctx.arc(0, 0, rx, 0, 2 * math.pi)
    ctx.restore()

def polyline(ctx, pts, close=False):
    ctx.new_path()
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()

def vgrad(y0, y1, c0, c1):
    """Vertical linear gradient from rgba c0 at y0 to rgba c1 at y1."""
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgba(0, *c0); g.add_color_stop_rgba(1, *c1)
    return g

def halo(ctx, x, y, radius, col=(1, 1, 1), a=0.22):
    """Soft radial light behind something important."""
    if a <= 0:
        return
    rg = cairo.RadialGradient(x, y, 8, x, y, radius)
    rg.add_color_stop_rgba(0, *col, a); rg.add_color_stop_rgba(1, *col, 0)
    ctx.set_source(rg); ctx.paint()

def beam(ctx, x, top, ground, a, col=None, top_w=40, bottom_w=170):
    """Spotlight cone from above onto (x, ground) with a lit floor ellipse."""
    if a <= 0:
        return
    col = col or accent()
    polyline(ctx, [(x - top_w, top), (x + top_w, top), (x + bottom_w, ground + 20),
                   (x - bottom_w, ground + 20)], close=True)
    ctx.set_source(vgrad(top, ground + 20, (*col, 0.0), (*col, 0.30 * a))); ctx.fill()
    ellipse(ctx, x, ground + 4, bottom_w, bottom_w * 0.18)
    ctx.set_source_rgba(*col, 0.35 * a); ctx.fill()


# ---------- stick figure ----------
# Angles are radians measured from straight down; positive swings toward the facing direction.
# hip=0 standing, hip=1 sitting on the ground.
STAND = dict(lean=0.03, th_f=0.13, sh_f=0.10, th_b=-0.13, sh_b=-0.10,
             ua_f=0.20, fa_f=0.30, ua_b=-0.18, fa_b=-0.08, hip=0.0)
SIT = dict(lean=0.38, th_f=2.25, sh_f=0.30, th_b=2.10, sh_b=0.22,
           ua_f=0.55, fa_f=0.25, ua_b=0.45, fa_b=0.15, hip=1.0)
SLUMP = dict(lean=0.55, th_f=0.10, sh_f=0.05, th_b=-0.05, sh_b=-0.05,
             ua_f=0.05, fa_f=0.00, ua_b=-0.05, fa_b=-0.05, hip=0.0)
ARMS_UP = dict(lean=0.0, th_f=0.15, sh_f=0.12, th_b=-0.15, sh_b=-0.12,
               ua_f=2.7, fa_f=2.9, ua_b=-2.7, fa_b=-2.9, hip=0.0)
PUSH = dict(lean=0.55, th_f=0.35, sh_f=0.10, th_b=-0.55, sh_b=-0.55,
            ua_f=1.45, fa_f=1.55, ua_b=1.35, fa_b=1.50, hip=0.0)
PULL = dict(lean=-0.42, th_f=0.55, sh_f=0.20, th_b=-0.20, sh_b=-0.30,
            ua_f=1.50, fa_f=1.55, ua_b=1.40, fa_b=1.50, hip=0.0)      # leaning back, hauling a rope
DANGLE = dict(lean=0.10, th_f=0.12, sh_f=-0.10, th_b=-0.02, sh_b=-0.25,
              ua_f=2.30, fa_f=1.70, ua_b=-2.30, fa_b=-1.70, hip=0.0)  # puppet: arms lifted, legs limp
PHONE = dict(lean=0.50, th_f=2.25, sh_f=0.30, th_b=2.10, sh_b=0.22,
             ua_f=0.45, fa_f=1.65, ua_b=0.35, fa_b=1.55, hip=1.0)     # sitting, hunched over a phone
CROUCH = dict(lean=0.50, th_f=1.10, sh_f=-0.30, th_b=0.90, sh_b=-0.40,
              ua_f=-0.60, fa_f=-0.30, ua_b=-0.70, fa_b=-0.40, hip=0.35)
LEAP = dict(lean=0.35, th_f=1.20, sh_f=0.20, th_b=-0.60, sh_b=-1.20,
            ua_f=2.60, fa_f=2.80, ua_b=2.20, fa_b=2.50, hip=0.0)     # mid-air, reaching forward
KNEEL = dict(lean=0.10, th_f=1.55, sh_f=0.0, th_b=0.05, sh_b=-1.50,
             ua_f=0.30, fa_f=0.50, ua_b=0.15, fa_b=0.30, hip=0.61)    # one knee down
LIE = dict(lean=1.57, th_f=-1.57, sh_f=-1.57, th_b=-1.50, sh_b=-1.50,
           ua_f=-1.45, fa_f=-1.50, ua_b=-1.40, fa_b=-1.45, hip=1.0)  # flat on the ground, head toward facing side
CARRY = dict(lean=0.05, th_f=0.13, sh_f=0.10, th_b=-0.13, sh_b=-0.10,
             ua_f=0.90, fa_f=1.60, ua_b=0.80, fa_b=1.50, hip=0.0)    # arms forward holding something
THINK = dict(lean=0.0, th_f=0.10, sh_f=0.08, th_b=-0.10, sh_b=-0.08,
             ua_f=0.45, fa_f=3.45, ua_b=0.20, fa_b=1.60, hip=0.0)    # hand to chin
HEAD_IN_HANDS = dict(lean=0.60, th_f=2.25, sh_f=0.30, th_b=2.10, sh_b=0.22,
                     ua_f=1.00, fa_f=2.80, ua_b=0.90, fa_b=2.70, hip=1.0)
SIT_CHAIR = dict(lean=0.05, th_f=1.57, sh_f=0.0, th_b=1.50, sh_b=-0.05,
                 ua_f=0.30, fa_f=1.20, ua_b=0.20, fa_b=1.10, hip=0.5)  # put a chair/box under the hip

def climb(ph):
    """Climbing a ladder/wall (side view): alternating reach and step."""
    s = math.sin(ph)
    return dict(lean=0.08, th_f=0.70 + 0.45 * s, sh_f=-0.20 + 0.45 * s, th_b=0.70 - 0.45 * s,
                sh_b=-0.20 - 0.45 * s, ua_f=2.75 + 0.25 * s, fa_f=2.95, ua_b=2.75 - 0.25 * s,
                fa_b=2.95, hip=0.0)

def wave(ph):
    p = dict(STAND)
    p.update(ua_f=2.5, fa_f=2.9 + 0.35 * math.sin(ph))
    return p

def walk(ph, stride=0.45):
    """Walk cycle pose at phase ph (radians; 2*pi = two steps)."""
    s = math.sin(ph)
    return dict(lean=0.07,
                th_f=stride * s, sh_f=stride * s - 0.65 * max(0, math.cos(ph)),
                th_b=-stride * s, sh_b=-stride * s - 0.65 * max(0, -math.cos(ph)),
                ua_f=-0.40 * s, fa_f=-0.40 * s + 0.45,
                ua_b=0.40 * s, fa_b=0.40 * s + 0.45, hip=0.0)

def run(ph):
    p = walk(ph, stride=0.8)
    p.update(lean=0.25, ua_f=-0.9 * math.sin(ph), fa_f=-0.9 * math.sin(ph) + 1.4,
             ua_b=0.9 * math.sin(ph), fa_b=0.9 * math.sin(ph) + 1.4)
    return p

def mix(p, q, k):
    """Blend two poses (k=0 -> p, k=1 -> q)."""
    return {key: lerp(p[key], q[key], k) for key in p}

def figure_height(s):
    return (0.56 + 0.56 + 1.0 + 0.14 + 0.60) * s

def figure(ctx, x, ground, s, pose, col=(1, 1, 1), alpha=1.0, d=1, bob=0.0):
    """Pictogram stick figure with feet on `ground` at x. s = torso length (≈ height/2.9).
    d = 1 faces right, -1 faces left. Back limbs are drawn darker for depth.
    Returns joint positions: head, neck, shoulder, hip, hand_f, hand_b, foot_f, foot_b (+ r =
    head radius) so you can attach ropes, strings, props."""
    T, L1, L2, A1, A2 = s, 0.56 * s, 0.56 * s, 0.46 * s, 0.44 * s
    r, lw = 0.30 * s, 0.24 * s
    hy = ground - lerp(L1 + L2, 0.20 * s, pose["hip"]) - bob

    def seg(p, ang, L):
        return (p[0] + d * L * math.sin(ang), p[1] + L * math.cos(ang))

    ln = pose["lean"]
    ux, uy = d * math.sin(ln), -math.cos(ln)
    hip = (x, hy)
    neck = (x + ux * T, hy + uy * T)
    sh = (x + ux * T * 0.86, hy + uy * T * 0.86)
    head = (x + ux * (T + 0.14 * s + r), hy + uy * (T + 0.14 * s + r))
    ctx.new_path()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(lw)

    def limb(p0, a1, l1, a2, l2, shade):
        p1 = seg(p0, a1, l1)
        p2 = seg(p1, a2, l2)
        ctx.set_source_rgba(*(c * shade for c in col), alpha)
        ctx.move_to(*p0); ctx.line_to(*p1); ctx.line_to(*p2); ctx.stroke()
        return p2

    hand_b = limb(sh, pose["ua_b"], A1, pose["fa_b"], A2, 0.5)
    foot_b = limb(hip, pose["th_b"], L1, pose["sh_b"], L2, 0.5)
    ctx.set_source_rgba(*col, alpha)
    ctx.move_to(*hip); ctx.line_to(*neck); ctx.stroke()
    foot_f = limb(hip, pose["th_f"], L1, pose["sh_f"], L2, 1.0)
    hand_f = limb(sh, pose["ua_f"], A1, pose["fa_f"], A2, 1.0)
    ctx.set_source_rgba(*col, alpha)
    ctx.arc(head[0], head[1], r, 0, 2 * math.pi)
    ctx.fill()
    return dict(head=head, neck=neck, shoulder=sh, hip=hip, hand_f=hand_f, hand_b=hand_b,
                foot_f=foot_f, foot_b=foot_b, r=r)


def camera(ctx, zoom, fx=CX, fy=1140):
    """Zoom the world around focal point (fx, fy), which stays fixed on screen.
    Use between ctx.save()/ctx.restore(); draw captions after restoring."""
    ctx.translate(fx, fy); ctx.scale(zoom, zoom); ctx.translate(-fx, -fy)


# ---------- timeline + render ----------
_EP = None

def load_episode(path):
    spec = importlib.util.spec_from_file_location("episode", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["episode"] = mod
    spec.loader.exec_module(mod)
    ep = mod.EPISODE
    for k in STYLE:
        if k in ep:
            STYLE[k] = ep[k]
    scenes = ep["scenes"]
    starts = np.cumsum([0] + [s.duration for s in scenes])
    return dict(scenes=scenes, starts=starts, total=float(starts[-1]))

def _init(path):
    global _EP
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    _EP = load_episode(path)

def _watermark(ctx):
    if STYLE["watermark"]:
        ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(20)
        txt = STYLE["watermark"].upper()
        w = ctx.text_extents(txt).x_advance
        ctx.set_source_rgba(1, 1, 1, 0.22)
        ctx.move_to((W - w) / 2, H - 260)
        ctx.show_text(txt)

def render_frame(fi):
    """Return one frame as BGR bytes."""
    scenes, starts = _EP["scenes"], _EP["starts"]
    t = fi / FPS
    idx = min(int(np.searchsorted(starts, t, side="right")) - 1, len(scenes) - 1)
    sc = scenes[idx]
    lt = t - starts[idx]
    black, fin = STYLE["black"], STYLE["fade_in"]
    a_in = 1.0 if idx == 0 else ease((lt - black) / fin)   # first scene starts fully visible (hook)
    out = STYLE["end_fade"] if idx == len(scenes) - 1 else STYLE["fade_out"]
    a_out = 1 - ease((lt - (sc.duration - out)) / out)
    alpha = min(a_in, a_out)

    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    ctx.set_source_rgb(0, 0, 0); ctx.paint()
    if alpha > 0:
        layer = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        sc.draw(cairo.Context(layer), max(lt - black, 0) if idx else lt)
        ctx.set_source_surface(layer)
        ctx.paint_with_alpha(alpha)
    _watermark(ctx)
    surf.flush()
    arr = np.ndarray((H, W, 4), np.uint8, surf.get_data())[:, :, :3].astype(np.float32)
    if STYLE["bloom"] > 0:
        small = Image.fromarray(arr.astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
        glow = np.asarray(small.filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BILINEAR),
                          np.float32)
        arr = arr + STYLE["bloom"] * glow
    return np.clip(arr, 0, 255).astype(np.uint8).tobytes()

def _rgb(fi):
    return np.frombuffer(render_frame(fi), np.uint8).reshape(H, W, 3)[:, :, ::-1]

def preview(path, out, per_scene=4):
    """Contact sheet: `per_scene` frames from every scene, one row per scene."""
    _init(path)
    rows = []
    for i, sc in enumerate(_EP["scenes"]):
        st = _EP["starts"][i]
        ts = [st + sc.duration * (k + 1) / (per_scene + 1) for k in range(per_scene)]
        rows.append([Image.fromarray(_rgb(int(tt * FPS))).resize((270, 480)) for tt in ts])
    sheet = Image.new("RGB", (270 * per_scene, 480 * len(rows)))
    for r, row in enumerate(rows):
        for c, im in enumerate(row):
            sheet.paste(im, (c * 270, r * 480))
    sheet.save(out)
    print(f"preview: {out}  scenes={len(rows)}  total={_EP['total']:.1f}s")

def stills(path, times, outdir):
    _init(path)
    os.makedirs(outdir, exist_ok=True)
    for tt in times:
        p = os.path.join(outdir, f"frame_{tt:06.2f}.png")
        Image.fromarray(_rgb(int(tt * FPS))).save(p)
        print(p)

def encode(path, out, music=None, music_start=0.0, workers=None):
    _init(path)
    total = _EP["total"]
    n = int(total * FPS)
    if music:
        audio = ["-ss", str(music_start), "-i", music]
        afilter = ["-af", f"afade=t=in:d=0.3,afade=t=out:st={max(total - 1.2, 0):.2f}:d=1.2"]
    else:
        audio = ["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=44100:cl=stereo"]
        afilter = []
    cmd = (["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"] + audio +
           ["-map", "0:v", "-map", "1:a", "-t", f"{total:.3f}"] + afilter +
           ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers or os.cpu_count(), initializer=_init, initargs=(path,)) as pool:
        for b in pool.imap(render_frame, range(n), chunksize=8):
            ff.stdin.write(b)
    ff.stdin.close()
    if ff.wait() != 0:
        sys.exit("ffmpeg failed")
    print(f"video: {out}  {total:.1f}s  {n} frames  music={'yes' if music else 'none (silent)'}")
    log_history(path, out)


HISTORY_FILE = "stickfigure_history.json"

def log_history(path, out):
    """Append this episode's scene list to stickfigure_history.json next to the video, so
    later episodes can avoid repeating the same visuals."""
    import datetime, json
    hp = os.path.join(os.path.dirname(os.path.abspath(out)), HISTORY_FILE)
    try:
        hist = json.load(open(hp))
    except (OSError, ValueError):
        hist = []
    ep = sys.modules["episode"].EPISODE
    hist.append(dict(date=datetime.date.today().isoformat(), video=os.path.basename(out),
                     title=ep.get("title", ""),
                     scenes=[dict(template=s.name, caption=s.caption) for s in _EP["scenes"]]))
    json.dump(hist, open(hp, "w"), indent=1)
    print(f"history: {hp}")


def _cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--preview")
    ap.add_argument("--frames", help="comma-separated times in seconds")
    ap.add_argument("--outdir", default="frames")
    ap.add_argument("--out")
    ap.add_argument("--music")
    ap.add_argument("--music-start", type=float, default=0.0)
    a = ap.parse_args()
    if a.preview:
        preview(a.episode, a.preview)
    if a.frames:
        stills(a.episode, [float(x) for x in a.frames.split(",")], a.outdir)
    if a.out:
        encode(a.episode, a.out, a.music, a.music_start)


if __name__ == "__main__":
    # Re-import as `engine` so episodes/scenes doing `from engine import ...` share STYLE with us.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import engine
    engine._cli()
