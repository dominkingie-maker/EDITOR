"""Prop library — reusable objects drawn in the house style (grey/white shapes, optional
accent). Combine them with figures to build custom scenes quickly.

Conventions: `x, y` is the centre unless the argument is called `ground` (then the prop
stands on that line). `s` scales the prop (1 = default size), `a` is alpha, `t` is the
scene time for props that animate by themselves (flicker, waves, flapping).
See assets/props_gallery.png for what each one looks like.
"""
import math
from engine import *  # noqa: F401,F403


def _grey(ctx, g, a):
    ctx.set_source_rgba(g, g, g, a)


# ---------- sky ----------
def sun(ctx, x, y, r=60, a=1.0, col=None, rays=True, t=0.0):
    col = col or (1.0, 0.9, 0.6)
    halo(ctx, x, y, r * 4, col=col, a=0.25 * a)
    if rays:
        ctx.set_line_width(4); ctx.set_source_rgba(*col, 0.7 * a)
        for k in range(12):
            ang = k * math.pi / 6 + t * 0.2
            ctx.move_to(x + math.cos(ang) * r * 1.3, y + math.sin(ang) * r * 1.3)
            ctx.line_to(x + math.cos(ang) * r * 1.7, y + math.sin(ang) * r * 1.7)
        ctx.stroke()
    ctx.arc(x, y, r, 0, 2 * math.pi); ctx.set_source_rgba(*col, a); ctx.fill()


def moon(ctx, x, y, r=40, a=1.0):
    halo(ctx, x, y, r * 3, a=0.15 * a)
    ctx.push_group()
    ctx.arc(x, y, r, 0, 2 * math.pi); _grey(ctx, 0.95, 1); ctx.fill()
    ctx.set_operator(cairo.OPERATOR_CLEAR)
    ctx.arc(x + r * 0.45, y - r * 0.25, r * 0.85, 0, 2 * math.pi); ctx.fill()
    ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)


def star(ctx, x, y, r=12, a=1.0, col=(1, 1, 1), points=5, rot=0.0):
    ctx.new_path()
    for k in range(points * 2):
        rr = r if k % 2 == 0 else r * 0.45
        ang = -math.pi / 2 + rot + k * math.pi / points
        ctx.line_to(x + rr * math.cos(ang), y + rr * math.sin(ang))
    ctx.close_path(); ctx.set_source_rgba(*col, a); ctx.fill()


def cloud(ctx, x, y, s=1.0, a=1.0, shade=0.28):
    ctx.new_path()
    for ox, oy, r in ((-60, 10, 40), (-15, -12, 52), (40, 0, 44), (78, 14, 30), (10, 22, 40)):
        ctx.new_sub_path(); ctx.arc(x + ox * s, y + oy * s, r * s, 0, 2 * math.pi)
    _grey(ctx, shade, a); ctx.fill()


def rain(ctx, x0, y0, w, h, t, a=1.0, density=14, speed=1.6):
    """Falling streaks inside the rectangle (x0, y0, w, h)."""
    ctx.set_line_width(2.5); ctx.set_source_rgba(0.65, 0.68, 0.75, 0.7 * a)
    for k in range(density):
        fx = (k * 0.618) % 1
        ph = (t * speed + k * 0.37) % 1
        px, py = x0 + fx * w, y0 + ph * h
        ctx.move_to(px, py); ctx.line_to(px - 6, py + 26)
    ctx.stroke()


# ---------- nature ----------
def tree(ctx, x, ground, s=1.0, a=1.0, shade=0.32, leaves=True, sway=0.0):
    ctx.set_line_width(16 * s); _grey(ctx, shade + 0.1, a)
    top = (x + sway * 10 * s, ground - 170 * s)
    ctx.move_to(x, ground); ctx.line_to(*top); ctx.stroke()
    ctx.set_line_width(7 * s)
    ctx.move_to(x, ground - 90 * s); ctx.line_to(x - 45 * s, ground - 150 * s)
    ctx.move_to(x, ground - 110 * s); ctx.line_to(x + 50 * s, ground - 165 * s); ctx.stroke()
    if leaves:
        ctx.new_path()
        for ox, oy, r in ((0, -230, 75), (-60, -185, 55), (60, -190, 58), (-25, -270, 50), (35, -265, 52)):
            ctx.new_sub_path(); ctx.arc(top[0] + ox * s, ground + oy * s, r * s, 0, 2 * math.pi)
        _grey(ctx, shade, a); ctx.fill()


def trunk(ctx, x, ground, h=700, w=26, a=1.0, shade=0.18):
    """Bare vertical trunk (stack several at different shades for a forest)."""
    ctx.rectangle(x - w / 2, ground - h, w, h); _grey(ctx, shade, a); ctx.fill()


def grass(ctx, x0, x1, ground, t=0.0, a=1.0, step=14):
    ctx.set_line_width(2); _grey(ctx, 0.45, a)
    x = x0
    while x < x1:
        h = 14 + 10 * math.sin(x * 0.7)
        sw = 4 * math.sin(t * 2 + x * 0.05)
        ctx.move_to(x, ground); ctx.line_to(x + sw, ground - h)
        x += step
    ctx.stroke()


def flower(ctx, x, ground, h=120, bloom=1.0, col=None, a=1.0, t=0.0):
    """Stem grows with bloom (0..0.5) then petals open (0.5..1)."""
    g = clamp(bloom * 2)
    top = (x + 4 * math.sin(t * 1.5), ground - h * g)
    ctx.set_line_width(4); _grey(ctx, 0.6, a)
    ctx.move_to(x, ground); ctx.curve_to(x - 10, ground - h * 0.4 * g, x + 8, ground - h * 0.7 * g, *top)
    ctx.stroke()
    o = clamp(bloom * 2 - 1)
    if o > 0:
        col = col or accent()
        for k in range(6):
            ang = k * math.pi / 3
            ctx.new_path(); ctx.save(); ctx.translate(top[0] + math.cos(ang) * 14 * o, top[1] + math.sin(ang) * 14 * o)
            ctx.rotate(ang); ctx.scale(16 * o, 9 * o); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
            ctx.set_source_rgba(*col, a); ctx.fill()
        ctx.arc(*top, 8 * o, 0, 2 * math.pi); _grey(ctx, 1, a); ctx.fill()


def rock(ctx, x, ground, s=1.0, a=1.0, text=""):
    pts = [(-70, 0), (-60, -45), (-20, -75), (35, -70), (68, -35), (72, 0)]
    polyline(ctx, [(x + px * s, ground + py * s) for px, py in pts], close=True)
    _grey(ctx, 0.2, a); ctx.fill_preserve(); _grey(ctx, 0.6, a); ctx.set_line_width(3); ctx.stroke()
    if text:
        label(ctx, text, x, ground - 30 * s, a, size=int(22 * s), col=(1, 1, 1))


def hill(ctx, cx, ground, w=500, h=120, a=1.0, shade=0.2):
    ctx.new_path(); ctx.move_to(cx - w / 2, ground)
    ctx.curve_to(cx - w / 4, ground - h, cx + w / 4, ground - h, cx + w / 2, ground)
    ctx.close_path(); ctx.set_source(vgrad(ground - h, ground, (shade, shade, shade, a), (0, 0, 0, a))); ctx.fill()


def waves(ctx, x0, x1, y, t, amp=6, a=1.0, rows=3):
    for r in range(rows):
        ctx.new_path()
        for xx in range(int(x0), int(x1) + 1, 8):
            ctx.line_to(xx, y + r * 26 + amp * math.sin(xx / 40 + t * 2 + r))
        ctx.set_line_width(2.5); _grey(ctx, 0.7 - r * 0.2, a); ctx.stroke()


# ---------- built things ----------
def house(ctx, x, ground, s=1.0, a=1.0, lit=False):
    w, h = 160 * s, 120 * s
    ctx.rectangle(x - w / 2, ground - h, w, h); _grey(ctx, 0.18, a); ctx.fill_preserve()
    _grey(ctx, 0.7, a); ctx.set_line_width(3); ctx.stroke()
    polyline(ctx, [(x - w / 2 - 15 * s, ground - h), (x, ground - h - 80 * s), (x + w / 2 + 15 * s, ground - h)],
             close=True)
    _grey(ctx, 0.28, a); ctx.fill_preserve(); _grey(ctx, 0.7, a); ctx.stroke()
    ctx.rectangle(x - 22 * s, ground - h + 35 * s, 44 * s, 40 * s)
    if lit:
        ctx.set_source_rgba(1, 0.85, 0.5, a); ctx.fill()
        halo(ctx, x, ground - h + 55 * s, 120 * s, col=(1, 0.85, 0.5), a=0.25 * a)
    else:
        _grey(ctx, 0.05, a); ctx.fill()


def lamp_post(ctx, x, ground, h=320, a=1.0, on=True):
    ctx.set_line_width(8); _grey(ctx, 0.5, a)
    ctx.move_to(x, ground); ctx.line_to(x, ground - h); ctx.line_to(x + 50, ground - h); ctx.stroke()
    if on:
        polyline(ctx, [(x + 35, ground - h + 4), (x + 65, ground - h + 4), (x + 110, ground + 2), (x - 10, ground + 2)],
                 close=True)
        ctx.set_source(vgrad(ground - h, ground, (1, 0.95, 0.8, 0.25 * a), (1, 0.95, 0.8, 0.0))); ctx.fill()
    ctx.arc(x + 50, ground - h + 8, 10, 0, 2 * math.pi)
    ctx.set_source_rgba(1, 0.95, 0.8, a if on else 0.3 * a); ctx.fill()


def ladder(ctx, x, ground, h=400, w=90, rungs=None, a=1.0):
    """rungs: how many rungs to draw (None = all); lets a ladder 'build' as you climb."""
    n = int(h / 55)
    ctx.set_line_width(6); _grey(ctx, 0.75, a)
    ctx.move_to(x - w / 2, ground); ctx.line_to(x - w / 2, ground - h)
    ctx.move_to(x + w / 2, ground); ctx.line_to(x + w / 2, ground - h); ctx.stroke()
    ctx.set_line_width(5)
    for k in range(n if rungs is None else min(n, rungs)):
        y = ground - 40 - k * 55
        ctx.move_to(x - w / 2, y); ctx.line_to(x + w / 2, y)
    ctx.stroke()


def signpost(ctx, x, ground, texts, a=1.0, dirs=None):
    """Post with one board per text; dirs = list of +1/-1 (arrow direction)."""
    ctx.set_line_width(10); _grey(ctx, 0.5, a)
    ctx.move_to(x, ground); ctx.line_to(x, ground - 120 - 70 * len(texts)); ctx.stroke()
    for k, txt in enumerate(texts):
        d = (dirs or [1, -1] * 4)[k]
        y = ground - 170 - k * 70
        bw = 200
        x0 = x if d > 0 else x - bw
        polyline(ctx, [(x0, y - 22), (x0 + bw, y - 22), (x0 + bw + 22 * d, y), (x0 + bw, y + 22), (x0, y + 22)]
                 if d > 0 else [(x0 + bw, y - 22), (x0, y - 22), (x0 - 22, y), (x0, y + 22), (x0 + bw, y + 22)],
                 close=True)
        _grey(ctx, 0.22, a); ctx.fill_preserve(); _grey(ctx, 0.75, a); ctx.set_line_width(2.5); ctx.stroke()
        label(ctx, txt, x0 + bw / 2, y + 8, a, size=22, col=(1, 1, 1))


def train(ctx, x, ground, cars=3, a=1.0):
    """Side view train; x is the front of the engine, it extends to the left."""
    _grey(ctx, 0.75, a); ctx.set_line_width(3)
    for c in range(cars + 1):
        cx = x - c * 230
        w = 210
        rounded_rect(ctx, cx - w, ground - 150, w, 120, 14)
        ctx.set_source_rgba(0.16, 0.16, 0.16, a); ctx.fill_preserve(); _grey(ctx, 0.75, a); ctx.stroke()
        for wx in range(3):
            ctx.rectangle(cx - w + 22 + wx * 64, ground - 132, 46, 36)
            ctx.set_source_rgba(1, 0.9, 0.6, 0.85 * a); ctx.fill()
        for wh in (cx - w + 40, cx - 40):
            ctx.arc(wh, ground - 24, 20, 0, 2 * math.pi); _grey(ctx, 0.6, a); ctx.fill()


def boat(ctx, x, y, s=1.0, a=1.0, t=0.0):
    rock_ = 0.05 * math.sin(t * 1.8)
    ctx.save(); ctx.translate(x, y); ctx.rotate(rock_); ctx.scale(s, s)
    polyline(ctx, [(-70, 0), (70, 0), (50, 28), (-50, 28)], close=True)
    _grey(ctx, 0.75, a); ctx.fill()
    ctx.set_line_width(3); ctx.move_to(0, 0); ctx.line_to(0, -90); ctx.stroke()
    polyline(ctx, [(4, -86), (50, -10), (4, -10)], close=True); _grey(ctx, 0.9, a); ctx.fill()
    ctx.restore()


# ---------- small objects ----------
def phone(ctx, x, y, s=1.0, a=1.0, glow=1.0, angle=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(angle)
    if glow > 0:
        halo(ctx, 0, 0, 110 * s, col=(0.7, 0.85, 1.0), a=0.3 * glow * a)
    rounded_rect(ctx, -22 * s, -40 * s, 44 * s, 80 * s, 8 * s)
    _grey(ctx, 0.2, a); ctx.fill_preserve(); _grey(ctx, 0.8, a); ctx.set_line_width(3); ctx.stroke()
    rounded_rect(ctx, -17 * s, -33 * s, 34 * s, 64 * s, 4 * s)
    ctx.set_source_rgba(0.75, 0.88, 1.0, (0.15 + 0.85 * glow) * a); ctx.fill()
    ctx.restore()


def coin(ctx, x, y, r=22, a=1.0, col=None):
    col = col or GOLD
    ctx.arc(x, y, r, 0, 2 * math.pi); ctx.set_source_rgba(*col, a); ctx.fill()
    ctx.arc(x, y, r * 0.7, 0, 2 * math.pi); ctx.set_source_rgba(0, 0, 0, 0.25 * a); ctx.set_line_width(2)
    ctx.stroke()


def heart(ctx, x, y, s=1.0, a=1.0, col=None):
    col = col or RED
    ctx.new_path(); ctx.move_to(x, y + 30 * s)
    ctx.curve_to(x - 60 * s, y - 10 * s, x - 30 * s, y - 55 * s, x, y - 25 * s)
    ctx.curve_to(x + 30 * s, y - 55 * s, x + 60 * s, y - 10 * s, x, y + 30 * s)
    ctx.set_source_rgba(*col, a); ctx.fill()


def key(ctx, x, y, s=1.0, a=1.0, angle=0.0, col=None):
    col = col or GOLD
    ctx.save(); ctx.translate(x, y); ctx.rotate(angle); ctx.scale(s, s)
    ctx.set_source_rgba(*col, a); ctx.set_line_width(7)
    ctx.new_path(); ctx.arc(-40, 0, 18, 0, 2 * math.pi); ctx.stroke()
    ctx.move_to(-22, 0); ctx.line_to(45, 0); ctx.move_to(30, 0); ctx.line_to(30, 16)
    ctx.move_to(42, 0); ctx.line_to(42, 12); ctx.stroke()
    ctx.restore()


def lock(ctx, x, y, s=1.0, a=1.0, open_=0.0):
    ctx.set_line_width(9 * s); _grey(ctx, 0.75, a)
    ctx.new_path(); ctx.arc(x + 0, y - 30 * s - 25 * s * open_, 30 * s, math.pi, 0); ctx.stroke()
    rounded_rect(ctx, x - 45 * s, y - 30 * s, 90 * s, 75 * s, 10 * s)
    _grey(ctx, 0.25, a); ctx.fill_preserve(); _grey(ctx, 0.8, a); ctx.set_line_width(3); ctx.stroke()
    ctx.arc(x, y + 2 * s, 8 * s, 0, 2 * math.pi); _grey(ctx, 0.05, a); ctx.fill()


def bird(ctx, x, y, s=1.0, flap=0.0, a=1.0):
    f = math.sin(flap)
    ctx.set_line_width(4 * s); _grey(ctx, 0.9, a); ctx.new_path()
    ctx.move_to(x - 30 * s, y - 14 * s * f); ctx.curve_to(x - 15 * s, y - 18 * s * f - 6 * s, x - 6 * s, y - 4 * s, x, y)
    ctx.curve_to(x + 6 * s, y - 4 * s, x + 15 * s, y - 18 * s * f - 6 * s, x + 30 * s, y - 14 * s * f)
    ctx.stroke()


def flame(ctx, x, base_y, h=60, t=0.0, a=1.0, col=(1.0, 0.82, 0.5)):
    fl = 1 + 0.12 * math.sin(t * 17) + 0.08 * math.sin(t * 29)
    halo(ctx, x, base_y - h * 0.4, h * 3, col=col, a=0.25 * a)
    ctx.new_path(); ctx.move_to(x, base_y - h * fl)
    ctx.curve_to(x + h * 0.4, base_y - h * 0.5, x + h * 0.3, base_y, x, base_y)
    ctx.curve_to(x - h * 0.3, base_y, x - h * 0.4, base_y - h * 0.5, x, base_y - h * fl)
    ctx.set_source_rgba(*col, a); ctx.fill()


def arrow(ctx, x, y, angle=0.0, length=140, a=1.0, col=(1, 1, 1)):
    """Projectile arrow; (x, y) is the tip."""
    ctx.save(); ctx.translate(x, y); ctx.rotate(angle)
    ctx.set_source_rgba(*col, a); ctx.set_line_width(4)
    ctx.move_to(0, 0); ctx.line_to(-length, 0); ctx.stroke()
    polyline(ctx, [(4, 0), (-18, -9), (-18, 9)], close=True); ctx.fill()
    for dy in (-1, 1):
        polyline(ctx, [(-length, 0), (-length - 14, dy * 12), (-length + 14, dy * 12), (-length + 26, 0)], close=True)
        ctx.fill()
    ctx.restore()


def speech_bubble(ctx, x, y, text, a=1.0, size=26, tail=-1, col=(1, 1, 1)):
    """Bubble centred at (x, y); tail = -1 (bottom-left) or 1 (bottom-right)."""
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL); ctx.set_font_size(size)
    w = ctx.text_extents(text).x_advance + size * 1.4
    h = size * 2.0
    rounded_rect(ctx, x - w / 2, y - h / 2, w, h, h / 2.2)
    ctx.move_to(x + tail * w * 0.15, y + h / 2 - 2); ctx.line_to(x + tail * w * 0.32, y + h / 2 + 22)
    ctx.line_to(x + tail * w * 0.02, y + h / 2 - 2)
    ctx.set_source_rgba(0.12, 0.12, 0.12, 0.9 * a); ctx.fill_preserve()
    ctx.set_source_rgba(0.75, 0.75, 0.75, a); ctx.set_line_width(2.5); ctx.stroke()
    label(ctx, text, x, y + size * 0.35, a, size=size, col=col)


def thought_bubble(ctx, x, y, w=260, h=150, a=1.0, from_xy=None):
    ctx.new_path()
    for k in range(9):
        ang = k * 2 * math.pi / 9
        ctx.new_sub_path(); ctx.arc(x + math.cos(ang) * w * 0.38, y + math.sin(ang) * h * 0.36, h * 0.3, 0, 2 * math.pi)
    ctx.new_sub_path(); ctx.save(); ctx.translate(x, y); ctx.scale(w * 0.42, h * 0.4); ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(0.14, 0.14, 0.14, a); ctx.fill()
    if from_xy:
        for k, r in enumerate((14, 9, 6)):
            px = lerp(x, from_xy[0], 0.55 + k * 0.15); py = lerp(y + h * 0.4, from_xy[1], 0.55 + k * 0.15)
            ctx.arc(px, py, r, 0, 2 * math.pi); ctx.set_source_rgba(0.3, 0.3, 0.3, a); ctx.fill()


def trophy(ctx, x, ground, s=1.0, a=1.0, col=None):
    col = col or GOLD
    ctx.set_source_rgba(*col, a)
    ctx.rectangle(x - 40 * s, ground - 18 * s, 80 * s, 18 * s); ctx.fill()
    ctx.rectangle(x - 8 * s, ground - 55 * s, 16 * s, 40 * s); ctx.fill()
    ctx.new_path(); ctx.move_to(x - 50 * s, ground - 140 * s); ctx.line_to(x + 50 * s, ground - 140 * s)
    ctx.curve_to(x + 50 * s, ground - 80 * s, x + 20 * s, ground - 55 * s, x, ground - 55 * s)
    ctx.curve_to(x - 20 * s, ground - 55 * s, x - 50 * s, ground - 80 * s, x - 50 * s, ground - 140 * s); ctx.fill()
    ctx.set_line_width(7 * s)
    for d in (-1, 1):  # handles
        ctx.new_path()
        if d > 0:
            ctx.arc(x + 52 * s, ground - 112 * s, 20 * s, -math.pi / 2, math.pi / 2)
        else:
            ctx.arc_negative(x - 52 * s, ground - 112 * s, 20 * s, -math.pi / 2, math.pi / 2)
        ctx.stroke()


def book(ctx, x, y, s=1.0, a=1.0, open_=1.0):
    """Closed (open_=0) it is a cover; open (1) it shows two pages with text lines."""
    o = clamp(open_)
    lw = 80 * s * o
    polyline(ctx, [(x, y - 50 * s), (x - lw, y - 56 * s), (x - lw, y + 46 * s), (x, y + 50 * s)], close=True)
    _grey(ctx, 0.75, a); ctx.fill()
    polyline(ctx, [(x, y - 50 * s), (x + 80 * s, y - 56 * s), (x + 80 * s, y + 46 * s), (x, y + 50 * s)], close=True)
    _grey(ctx, 0.9 if o > 0.3 else 0.35, a); ctx.fill()
    if o > 0.5:
        ctx.set_line_width(2); _grey(ctx, 0.35, a * (o - 0.5) * 2)
        for k in range(5):
            yy = y - 32 * s + k * 16 * s
            ctx.move_to(x + 12 * s, yy); ctx.line_to(x + 66 * s, yy - 2 * s)
            ctx.move_to(x - 12 * s, yy); ctx.line_to(x - lw + 14 * s, yy - 2 * s)
        ctx.stroke()


def backpack(ctx, x, y, s=1.0, a=1.0, fill_=0.0):
    rounded_rect(ctx, x - 45 * s, y - 60 * s, 90 * s, 120 * s, 22 * s)
    _grey(ctx, 0.3, a); ctx.fill_preserve(); _grey(ctx, 0.75, a); ctx.set_line_width(3); ctx.stroke()
    rounded_rect(ctx, x - 30 * s, y + 5 * s, 60 * s, 38 * s, 8 * s); ctx.stroke()
    ctx.set_line_width(6 * s); ctx.new_path(); ctx.arc(x, y - 60 * s, 22 * s, math.pi, 0); ctx.stroke()


PROPS = [sun, moon, star, cloud, rain, tree, trunk, grass, flower, rock, hill, waves, house, lamp_post,
         ladder, signpost, train, boat, phone, coin, heart, key, lock, bird, flame, arrow,
         speech_bubble, thought_bubble, trophy, book, backpack]
