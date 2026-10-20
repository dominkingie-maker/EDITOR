"""Ready-made, parameterised scene templates. Each function returns a Scene.

Every template takes the caption as line1 (setup, appears at t=0) and line2
(payoff, appears at t2). Keep lines short: ~2-6 words each.
"""
import math
from engine import *  # noqa: F401,F403  (helpers, poses, constants)


def stairs(line1, line2="", steps=7, duration=6.3, t2=2.4, accent_words=(), top_label=""):
    """Figure climbs a staircase; each step lights up as it lands. Theme: consistency, small steps."""
    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2, accent_words)
        sw, rise = 665 / steps, 365 / steps
        x0, y0 = 250, 1310
        pts = [(x0 - 140, y0), (x0, y0)]
        for i in range(steps):
            pts += [(x0 + i * sw, y0 - (i + 1) * rise), (x0 + (i + 1) * sw, y0 - (i + 1) * rise)]
        pts += [(x0 + steps * sw + 120, y0 - steps * rise)]
        polyline(ctx, pts + [(pts[-1][0], y0 + 40), (pts[0][0], y0 + 40)], close=True)
        ctx.set_source(vgrad(y0 - steps * rise, y0 + 40, (0.13, 0.13, 0.13, 1), (0, 0, 0, 1))); ctx.fill()
        polyline(ctx, pts)
        ctx.set_line_width(3); ctx.set_source_rgba(0.45, 0.45, 0.45, 1); ctx.stroke()
        walk_end = duration - 1.0
        k = steps * eio((t - 0.5) / (walk_end - 0.5)) if t < walk_end else float(steps)
        i = int(min(k, steps - 0.001)); f = k - i
        for j in range(1, steps + 1):
            a = ease((k - (j - 0.35)) / 0.25)
            if a > 0:
                y = y0 - j * rise
                ctx.set_line_width(5); ctx.set_source_rgba(1, 1, 1, a)
                ctx.move_to(x0 + (j - 1) * sw, y); ctx.line_to(x0 + j * sw, y); ctx.stroke()
        if top_label:
            label(ctx, top_label, x0 + steps * sw + 40, y0 - steps * rise - 230,
                  ease((k - steps + 0.3) / 0.3), size=28, col=accent())
        ground = lerp(y0 - i * rise, y0 - (i + 1) * rise, ease(f)) - 14 * math.sin(math.pi * f)
        moving = 0.5 < t < walk_end
        figure(ctx, x0 - 46 + k * sw, ground, 62, walk(k * math.pi) if moving else STAND)
    return Scene(draw, duration, "stairs", " / ".join(x for x in (line1, line2) if x))


def iceberg(line1, line2="", tip="SUCCESS", hidden=("Failures", "Late nights", "Doubt", "Sacrifice",
                                                       "Discipline"), duration=6.6, t2=2.6):
    """Small visible tip vs huge hidden mass revealed below the waterline (up to 5 labels).
    Theme: people see results, not the work."""
    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        wy = 860
        bob = 4 * math.sin(t * 1.6)
        tip_pts = [(440, wy), (480, wy - 50), (515, wy - 105), (556, wy - 118), (598, wy - 70), (640, wy)]
        under = [(640, wy), (760, wy + 70), (830, wy + 230), (800, wy + 420), (690, wy + 560),
                 (540, wy + 600), (380, wy + 540), (270, wy + 380), (300, wy + 190), (360, wy + 60), (440, wy)]
        label(ctx, tip, 545, wy - 150 + bob, ease(t / 0.4), size=26, col=(1, 1, 1))
        polyline(ctx, [(x, y + bob) for x, y in tip_pts], close=True)
        ctx.set_source_rgba(0.92, 0.92, 0.92, 1); ctx.fill()
        reveal = eio((t - 1.6) / 1.6)
        if reveal > 0:
            ctx.save()
            ctx.rectangle(0, wy, W, 640 * reveal); ctx.clip()
            polyline(ctx, [(x, y + bob) for x, y in under], close=True)
            ctx.set_source(vgrad(wy, wy + 600, (0.12, 0.12, 0.13, 1), (0.02, 0.02, 0.02, 1)))
            ctx.fill_preserve()
            ctx.set_source_rgba(0.5, 0.5, 0.5, 1); ctx.set_line_width(2); ctx.stroke()
            ctx.restore()
            spots = [(470, 130), (620, 215), (420, 300), (640, 380), (530, 470)]
            for n, txt in enumerate(hidden[:5]):
                x, dy = spots[n]
                label(ctx, txt, x, wy + dy + bob, ease((t - t2 - n * 0.35) / 0.35), size=28,
                      col=(0.95, 0.95, 0.95))
        ctx.new_path()
        for xx in range(60, W - 59, 6):
            ctx.line_to(xx, wy + 3 * math.sin(xx / 55 + t * 2.2))
        ctx.set_line_width(2.5); ctx.set_source_rgba(0.8, 0.8, 0.8, 0.8); ctx.stroke()
        ctx.rectangle(60, wy, W - 120, 700)
        ctx.set_source(vgrad(wy, wy + 700, (0.25, 0.3, 0.35, 0.18), (0, 0, 0, 0))); ctx.fill()
    return Scene(draw, duration, "iceberg", " / ".join(x for x in (line1, line2) if x))


def zone_exit(line1, line2="", zone="Comfort zone", duration=6.4, t2=3.1):
    """Figure sits inside a dashed ring, stands, walks out and starts to glow; ring dims.
    Theme: leaving comfort, growth, change."""
    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        cx, gy = 470, 1250
        dim = lerp(1.0, 0.3, ease((t - 3.4) / 0.8))
        ellipse(ctx, cx, gy, 190, 49)
        ctx.set_dash([10, 10]); ctx.set_line_width(4)
        ctx.set_source_rgba(0.85, 0.85, 0.85, dim); ctx.stroke(); ctx.set_dash([])
        label(ctx, zone, cx, gy + 105, 0.8 * dim, size=28)
        up = eio((t - 1.6) / 0.8)
        wk = clamp((t - 2.5) / 3.0)
        x = cx + 330 * eio(wk) if t > 2.5 else cx
        pose = mix(SIT, STAND, up) if t < 2.5 else (walk((x - cx) / 38) if wk < 1 else STAND)
        halo(ctx, x, gy - 110, 260, a=0.22 * ease((x - (cx + 190)) / 120))
        figure(ctx, x, gy, 62, pose)
    return Scene(draw, duration, "zone_exit", " / ".join(x for x in (line1, line2) if x))


def meter_drain(line1, line2="", drains=("Scrolling", "Overthinking", "Wrong people", "Drama"),
                duration=6.0, t2=1.6):
    """Battery with 5 bars; each label that appears drains one bar (max 4). Last bar pulses.
    Theme: energy, time, attention being wasted."""
    drains = list(drains)[:4]
    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        bx, by, bw, bh = 540, 1110, 250, 430
        x0, y0 = bx - bw / 2, by - bh / 2
        ctx.set_line_width(7); ctx.set_source_rgba(1, 1, 1, 1)
        rounded_rect(ctx, x0, y0, bw, bh, 26); ctx.stroke()
        ctx.rectangle(bx - 50, y0 - 32, 100, 26); ctx.fill()
        sched = [(txt, (-1, 1)[n % 2], y0 + 70 + n * 90, 2.2 + n * 0.7) for n, txt in enumerate(drains)]
        bar_h, gap = 66, 13
        for b in range(5):
            top = y0 + bh - 22 - (b + 1) * bar_h - b * gap
            d = 4 - b
            a = 1 - ease((t - sched[d][3] - 0.25) / 0.35) if d < len(sched) else 1.0
            if b == 0 and t > 4.9:
                a = 0.75 + 0.25 * math.cos((t - 4.9) * 5)
            ctx.set_source_rgba(1, 1, 1, max(a, 0.06))
            ctx.rectangle(x0 + 22, top, bw - 44, bar_h); ctx.fill()
        for txt, side, y, t0 in sched:
            a = ease((t - t0) / 0.3)
            if a <= 0:
                continue
            edge, end = bx + side * (bw / 2 + 18), bx + side * (bw / 2 + 18 + 90 * a)
            ctx.set_line_width(2); ctx.set_source_rgba(0.7, 0.7, 0.7, a)
            ctx.move_to(edge, y); ctx.line_to(end, y); ctx.stroke()
            label(ctx, txt, end + side * 14, y + 10, a, size=28, align="left" if side > 0 else "right")
    return Scene(draw, duration, "meter_drain", " / ".join(x for x in (line1, line2) if x))


def spotlight(line1, line2="", accent_words=(), duration=6.4, t2=2.9):
    """Rows of dim seated figures; one stands up as an accent-coloured beam hits it.
    Theme: be the one who acts; standing out; the ending payoff. Best as the LAST scene."""
    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2, accent_words)
        hero_x, hero_g = 540, 1330
        b = ease((t - 2.0) / 0.7)
        beam(ctx, hero_x, 720, hero_g, b)
        for gy, s, n, shade in [(1110, 36, 7, 0.16), (1210, 46, 6, 0.24), (1330, 58, 5, 0.32)]:
            span = 150 * n * s / 58
            for k in range(n):
                if gy == hero_g and k == n // 2:
                    continue
                figure(ctx, 540 + (k - (n - 1) / 2) * span / max(n - 1, 1), gy, s, SIT, col=(shade,) * 3)
        col = tuple(lerp(0.32, c, b) for c in (1.0, 0.92, 0.7))
        figure(ctx, hero_x, hero_g, 58, mix(SIT, STAND, eio((t - 2.0) / 0.9)), col=col)
    return Scene(draw, duration, "spotlight", " / ".join(x for x in (line1, line2) if x))


def split_compare(top, bottom, line1="", line2="", duration=6.0, t2=2.6):
    """Two stacked lanes. Top: figure walks forward leaving a glowing trail (progress).
    Bottom: figure sits still with pulsing thought dots (no progress).
    Theme: doer vs thinker, action vs perfection, consistent vs waiting."""
    def draw(ctx, t):
        if line1:
            caption(ctx, t, line1, line2, t2)
        lanes = [(1040, top, True), (1430, bottom, False)]
        ctx.set_line_width(1.5); ctx.set_source_rgba(0.3, 0.3, 0.3, 1)
        ctx.move_to(120, 1130); ctx.line_to(W - 120, 1130); ctx.stroke()
        for gy, name, moving in lanes:
            ctx.set_line_width(3); ctx.set_source_rgba(0.35, 0.35, 0.35, 1)
            ctx.move_to(150, gy); ctx.line_to(W - 150, gy); ctx.stroke()
            label(ctx, name, 150, gy - 250, ease(t / 0.4), size=30, col=(1, 1, 1), align="left")
            if moving:
                p = clamp((t - 0.6) / (duration - 1.4))
                x = lerp(220, W - 240, p)
                ctx.set_line_width(6); ctx.set_source_rgba(1, 1, 1, 0.9)
                ctx.move_to(200, gy); ctx.line_to(x, gy); ctx.stroke()
                halo(ctx, x, gy - 90, 200, a=0.15 * ease(p * 4))
                figure(ctx, x, gy, 52, walk((x - 220) / 32) if p < 1 else STAND)
            else:
                figure(ctx, 230, gy, 52, SIT, col=(0.6, 0.6, 0.6))
                for k in range(3):
                    a = 0.3 + 0.7 * max(0, math.sin(t * 3 - k * 0.6))
                    ctx.arc(300 + k * 26, gy - 190 - k * 14, 6 + k * 2, 0, 2 * math.pi)
                    ctx.set_source_rgba(0.8, 0.8, 0.8, a * ease((t - 0.8) / 0.4)); ctx.fill()
    return Scene(draw, duration, "split_compare", f"{top} vs {bottom}")


def uphill(line1, line2="", load="Your goal", duration=6.4, t2=2.8):
    """Figure pushes a heavy boulder up a long slope, slowly but steadily.
    Theme: struggle, persistence, the hard part, carrying your dream."""
    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        ax, ay, bx_, by_ = 110, 1460, 980, 980
        ang = math.atan2(by_ - ay, bx_ - ax)
        polyline(ctx, [(ax, ay), (bx_, by_), (bx_, ay + 60), (ax, ay + 60)], close=True)
        ctx.set_source(vgrad(by_, ay + 60, (0.12, 0.12, 0.12, 1), (0, 0, 0, 1))); ctx.fill()
        ctx.set_line_width(3); ctx.set_source_rgba(0.5, 0.5, 0.5, 1)
        ctx.move_to(ax, ay); ctx.line_to(bx_, by_); ctx.stroke()
        p = lerp(0.12, 0.62, eio(t / duration))
        fx = lerp(ax, bx_, p)
        gy = lerp(ay, by_, p)
        R = 78
        rx = fx + 95 + R * 0.5
        ry = lerp(ay, by_, (rx - ax) / (bx_ - ax)) - R / math.cos(ang) + 6
        ctx.arc(rx, ry, R, 0, 2 * math.pi)
        ctx.set_source_rgba(0.22, 0.22, 0.22, 1); ctx.fill_preserve()
        ctx.set_source_rgba(0.85, 0.85, 0.85, 1); ctx.set_line_width(4); ctx.stroke()
        label(ctx, load, rx, ry + 10, ease((t - 0.6) / 0.4), size=24, col=(1, 1, 1))
        legs = walk(t * 4.2, stride=0.35)
        pose = dict(PUSH)
        pose.update(th_f=0.35 + legs["th_f"], sh_f=0.1 + legs["sh_f"], th_b=-0.55 + legs["th_b"],
                    sh_b=-0.55 + legs["sh_b"])
        figure(ctx, fx, gy, 58, pose)
    return Scene(draw, duration, "uphill", " / ".join(x for x in (line1, line2) if x))


def title_card(line1, line2="", accent_words=(), duration=4.0, t2=1.2, size=56):
    """Centered text only, with a slow glow behind it. Use sparingly: a final
    call-to-action or a punchline that needs no picture."""
    def draw(ctx, t):
        halo(ctx, CX, 1000, 420, a=0.08 * ease(t / 1.0))
        words(ctx, line1, 980, 0.0, t, size=size, accent_words=accent_words)
        if line2:
            words(ctx, line2, 980 + size * 1.5, t2, t, size=size, accent_words=accent_words)
    return Scene(draw, duration, "title_card", " / ".join(x for x in (line1, line2) if x))


TEMPLATES = {
    "stairs": stairs, "iceberg": iceberg, "zone_exit": zone_exit, "meter_drain": meter_drain,
    "spotlight": spotlight, "split_compare": split_compare, "uphill": uphill, "title_card": title_card,
}

from scenes_extra import *  # noqa: E402,F401,F403  (15 more templates)
from scenes_extra import EXTRA_TEMPLATES  # noqa: E402
TEMPLATES.update(EXTRA_TEMPLATES)
from scenes_more import *  # noqa: E402,F401,F403  (22 more templates built with props)
from scenes_more import MORE_TEMPLATES  # noqa: E402
TEMPLATES.update(MORE_TEMPLATES)
