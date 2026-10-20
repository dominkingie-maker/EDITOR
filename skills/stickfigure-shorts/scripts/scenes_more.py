"""22 more scene templates, built from the ideas bank with the prop library.
Each has its own kind of motion so they don't look like each other."""
import math
import random
from engine import *  # noqa: F401,F403
from props import (arrow, backpack, boat, cloud, flame, flower, lamp_post, moon, phone, rain, rock,
                   signpost, star, train as train_prop, trunk, waves)


def _cap(line1, line2):
    return " / ".join(x for x in (line1, line2) if x)


def _ground(ctx, y, x0=130, x1=W - 130, g=0.35):
    ctx.set_line_width(3); ctx.set_source_rgba(g, g, g, 1)
    ctx.move_to(x0, y); ctx.line_to(x1, y); ctx.stroke()


def _spiky(ctx, x, y, r, spikes=9, jag=0.45, rot=0.0):
    ctx.new_path()
    for k in range(spikes * 2):
        rr = r * (1 + jag) if k % 2 == 0 else r
        ang = rot + k * math.pi / spikes
        ctx.line_to(x + rr * math.cos(ang), y + rr * math.sin(ang))
    ctx.close_path()


# ------------------------------------------------------------------ repetition
def water_drop(line1, line2="", stone="Your goal", duration=6.6, t2=3.0):
    """Drops fall one after another onto a stone; a groove deepens until it breaks through
    and light shines out. Counter ticks up. Theme: consistency beats intensity."""
    top_y, sx0, sx1, sy0, sy1 = 790, 380, 700, 1180, 1380
    period = 0.32
    end_t = duration - 1.6

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        ctx.set_source_rgba(0.5, 0.5, 0.5, 1)
        polyline(ctx, [(500, top_y - 30), (580, top_y - 30), (548, top_y + 10), (532, top_y + 10)], close=True)
        ctx.fill()
        depth = (sy1 - sy0) * eio(t / end_t)
        broke = t > end_t
        split = 26 * ease((t - end_t) / 0.4) if broke else 0
        for side in (-1, 1):  # stone halves meet in the middle until the groove breaks through
            if side < 0:
                pts = [(sx0, sy0 + 10), (540, sy0), (540, sy1), (sx0, sy1)]
            else:
                pts = [(540, sy0), (sx1, sy0 + 10), (sx1, sy1), (540, sy1)]
            polyline(ctx, [(px + side * split, py) for px, py in pts], close=True)
            ctx.set_source(vgrad(sy0, sy1, (0.3, 0.3, 0.3, 1), (0.1, 0.1, 0.1, 1))); ctx.fill()
        polyline(ctx, [(sx0 - split, sy0 + 10), (540, sy0), (sx1 + split, sy0 + 10), (sx1 + split, sy1),
                       (sx0 - split, sy1)], close=True)
        ctx.set_source_rgba(0.65, 0.65, 0.65, 1); ctx.set_line_width(3); ctx.stroke()
        if not broke:
            polyline(ctx, [(522, sy0), (558, sy0), (546, sy0 + depth), (534, sy0 + depth)], close=True)
            ctx.set_source_rgba(0, 0, 0, 1); ctx.fill()
        else:
            ctx.rectangle(540 - split, sy0 - 2, 2 * split, sy1 - sy0 + 4); ctx.set_source_rgba(0, 0, 0, 1); ctx.fill()
        if broke:
            halo(ctx, 540, (sy0 + sy1) / 2, 320, col=accent(), a=0.45 * ease((t - end_t) / 0.5))
        label(ctx, stone, 540, sy1 + 50, ease(t / 0.4), size=26)
        n = int(t / period)
        if not broke:
            ph = (t % period) / period
            dy = lerp(top_y + 14, sy0 + depth - 8, ph * ph)
            ctx.new_path(); ctx.move_to(540, dy - 18); ctx.curve_to(552, dy, 550, dy + 10, 540, dy + 10)
            ctx.curve_to(530, dy + 10, 528, dy, 540, dy - 18)
            ctx.set_source_rgba(0.75, 0.88, 1.0, 1); ctx.fill()
            if ph < 0.25 and n > 0:
                sp = ph / 0.25
                ctx.set_line_width(2); ctx.set_source_rgba(0.75, 0.88, 1.0, 1 - sp)
                for d in (-1, 1):
                    ctx.move_to(540 + d * 8, sy0 + depth - 8); ctx.line_to(540 + d * (8 + 30 * sp), sy0 + depth - 8 - 25 * sp)
                ctx.stroke()
        shown = int(lerp(1, 10000, (t / end_t) ** 3)) if not broke else 10000
        label(ctx, f"× {shown:,}", 760, 1000, ease(t / 0.4), size=30, col=accent() if broke else (0.8, 0.8, 0.8))
    return Scene(draw, duration, "water_drop", _cap(line1, line2))


def snowball(line1, line2="", start="1%", end_label="Momentum", duration=6.4, t2=2.8):
    """A tiny snowball rolls down a long slope, growing until it fills the frame.
    Theme: compounding, momentum, small things grow."""
    ax, ay, bx, by = 110, 820, 1000, 1470
    ang = math.atan2(by - ay, bx - ax)

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        polyline(ctx, [(ax, ay), (bx, by), (bx, by + 80), (ax, by + 80)], close=True)
        ctx.set_source(vgrad(ay, by + 80, (0.16, 0.16, 0.17, 1), (0.02, 0.02, 0.02, 1))); ctx.fill()
        ctx.set_line_width(3); ctx.set_source_rgba(0.75, 0.75, 0.8, 1)
        ctx.move_to(ax, ay); ctx.line_to(bx, by); ctx.stroke()
        u = clamp((t - 0.4) / (duration - 1.6))
        p = 0.04 + 0.78 * u ** 1.7
        r = 10 + 190 * u ** 1.5
        px, py = lerp(ax, bx, p), lerp(ay, by, p)
        cx, cy = px + r * math.sin(ang), py - r * math.cos(ang)
        dist = math.hypot(px - ax, py - ay)
        rot = dist / max(r, 1)
        for k in range(1, 6):  # trail of packed snow
            q = clamp(p - k * 0.02)
            ctx.arc(lerp(ax, bx, q), lerp(ay, by, q) - 2, 3, 0, 2 * math.pi)
        ctx.set_source_rgba(0.85, 0.85, 0.9, 0.5); ctx.fill()
        rg = cairo.RadialGradient(cx - r * 0.3, cy - r * 0.3, r * 0.1, cx, cy, r)
        rg.add_color_stop_rgba(0, 1, 1, 1, 1); rg.add_color_stop_rgba(1, 0.6, 0.62, 0.68, 1)
        ctx.arc(cx, cy, r, 0, 2 * math.pi); ctx.set_source(rg); ctx.fill()
        ctx.set_line_width(max(1.5, r * 0.04)); ctx.set_source_rgba(0.45, 0.47, 0.55, 0.8)
        for k in range(3):
            a0 = rot + k * 2.1
            ctx.new_path(); ctx.arc(cx, cy, r * 0.65, a0, a0 + 0.9); ctx.stroke()
        label(ctx, start, ax + 70, ay - 30, ease(t / 0.4) * (1 - ease((t - 2) / 0.5)), size=26)
        if r > 90:
            label(ctx, end_label, cx, cy + 10, ease((r - 90) / 40), size=int(min(40, r * 0.24)),
                  col=(0, 0, 0), bold=True)
    return Scene(draw, duration, "snowball", _cap(line1, line2))


# ------------------------------------------------------------------ fear / reveal
def shadow_monster(line1, line2="", real="Fear", duration=6.6, t2=3.2, reveal=2.9):
    """A huge clawed shadow looms on the wall over a cowering figure; the ceiling light
    switches on and it's just a tiny creature. Theme: fear is bigger in your head."""
    gy = 1360
    ox, oy = 330, gy - 26

    def draw(ctx, t):
        on = ease((t - reveal) / 0.25)
        ctx.rectangle(120, 760, W - 240, gy - 760)
        ctx.set_source_rgba(0.1 + 0.12 * on, 0.1 + 0.12 * on, 0.11 + 0.12 * on, 1); ctx.fill()
        ctx.set_source(vgrad(gy - 300, gy, (1, 0.85, 0.6, 0.0), (1, 0.85, 0.6, 0.18 * (1 - on))))
        ctx.rectangle(120, gy - 300, W - 240, 300); ctx.fill()
        sh = 1 - ease((t - reveal) / 0.4)
        if sh > 0:
            breathe = 1 + 0.04 * math.sin(t * 2.5)
            _spiky(ctx, 620, 1060, 230 * breathe, spikes=11, jag=0.5, rot=t * 0.15)
            ctx.set_source_rgba(0, 0, 0, sh); ctx.fill()
            for ex in (560, 680):
                ctx.new_path(); ctx.save(); ctx.translate(ex, 1010); ctx.scale(26, 9)
                ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
                ctx.set_source_rgba(1, 1, 1, 0.85 * sh); ctx.fill()
        _ground(ctx, gy, 120, W - 120)
        flame(ctx, 230, gy, 34, t=t, a=1 - on)
        bulb_a = on
        if bulb_a > 0:
            ctx.set_line_width(2); ctx.set_source_rgba(0.6, 0.6, 0.6, 1)
            ctx.move_to(540, 760); ctx.line_to(540, 820); ctx.stroke()
            halo(ctx, 540, 840, 420, col=(1, 0.95, 0.85), a=0.3 * bulb_a)
            ctx.arc(540, 840, 20, 0, 2 * math.pi); ctx.set_source_rgba(1, 0.97, 0.9, bulb_a); ctx.fill()
        _spiky(ctx, ox, oy, 15, spikes=9, jag=0.5)
        ctx.set_source_rgba(0.75, 0.75, 0.75, 1); ctx.fill()
        for ex in (ox - 5, ox + 6):
            ctx.arc(ex, oy - 3, 3, 0, 2 * math.pi); ctx.set_source_rgba(0, 0, 0, 1); ctx.fill()
        label(ctx, real, ox, oy - 45, on, size=24, col=accent())
        shake = 2.5 * math.sin(t * 40) * (1 - on)
        pose = mix(CROUCH, THINK, eio((t - reveal - 0.4) / 0.6))
        figure(ctx, 800 + shake, gy, 56, pose, d=-1)
        caption(ctx, t, line1, line2, t2)
    return Scene(draw, duration, "shadow_monster", _cap(line1, line2))


def lighthouse(line1, line2="", duration=6.6, t2=3.0):
    """A lighthouse alone in a storm; its beam sweeps across the dark sea and small boats
    follow it to safety. Theme: be the light, purpose, standing alone, leadership."""
    sea = 1330

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        rain(ctx, 100, 720, W - 200, 640, t, a=0.8, density=40)
        polyline(ctx, [(120, sea + 20), (190, sea - 40), (330, sea - 55), (420, sea - 20), (460, sea + 20)], close=True)
        ctx.set_source_rgba(0.2, 0.2, 0.2, 1); ctx.fill()
        base, top, xc = sea - 50, 900, 300
        polyline(ctx, [(xc - 60, base), (xc + 60, base), (xc + 38, top), (xc - 38, top)], close=True)
        ctx.set_source_rgba(0.85, 0.85, 0.85, 1); ctx.fill()
        for k in range(3):
            y0 = base - 70 - k * 120
            w0 = lerp(60, 38, (base - y0) / (base - top))
            ctx.rectangle(xc - w0, y0 - 40, 2 * w0, 40); ctx.set_source_rgba(0.25, 0.25, 0.25, 1); ctx.fill()
        ctx.rectangle(xc - 34, top - 70, 68, 70); ctx.set_source_rgba(0.2, 0.2, 0.2, 1); ctx.fill()
        polyline(ctx, [(xc - 46, top - 70), (xc + 46, top - 70), (xc, top - 115)], close=True); ctx.fill()
        lamp = (xc, top - 35)
        ph = t * 1.6
        reach = math.cos(ph)
        if reach > 0:
            spread = 60 + 140 * reach
            polyline(ctx, [lamp, (W + 40, lamp[1] - spread), (W + 40, lamp[1] + spread)], close=True)
            g = cairo.LinearGradient(lamp[0], 0, W, 0)
            g.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.45 * reach); g.add_color_stop_rgba(1, 1, 0.95, 0.75, 0)
            ctx.set_source(g); ctx.fill()
        halo(ctx, *lamp, 120, col=(1, 0.95, 0.75), a=0.6)
        ctx.arc(*lamp, 16, 0, 2 * math.pi); ctx.set_source_rgba(1, 0.97, 0.85, 1); ctx.fill()
        for k, (start_x, y) in enumerate(((1000, sea - 10), (1150, sea + 40), (1320, sea + 15))):
            bx = start_x - 95 * t * (0.8 + 0.15 * k)
            if 420 < bx < W + 100:
                boat(ctx, bx, y, 0.55 - 0.08 * k, a=0.9, t=t + k)
        ctx.rectangle(100, sea + 10, W - 200, 300)
        ctx.set_source(vgrad(sea, sea + 300, (0.06, 0.07, 0.09, 1), (0, 0, 0, 1))); ctx.fill()
        waves(ctx, 440, W - 100, sea + 20, t, amp=7, a=0.8)
    return Scene(draw, duration, "lighthouse", _cap(line1, line2))


# ------------------------------------------------------------------ setbacks / pressure
def bow_arrow(line1, line2="", setback="Setback", duration=6.2, t2=2.8, release=2.7):
    """An archer draws an arrow further and further back ('Setback'), then releases it and
    it flies off with a streak. Theme: setbacks set you up, being pulled back before launch."""
    gy = 1330

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        _ground(ctx, gy)
        draw_k = eio(t / release) if t < release else 0.0
        pose = dict(STAND)
        pose.update(lean=-0.05 - 0.08 * draw_k, th_f=0.35, sh_f=0.25, th_b=-0.30, sh_b=-0.30,
                    ua_f=1.57, fa_f=1.57, ua_b=lerp(1.45, 1.25, draw_k), fa_b=lerp(1.4, -1.3, draw_k))
        j = figure(ctx, 330, gy, 58, pose)
        hx, hy = j["hand_f"]
        nock = j["hand_b"] if t < release else (hx - 8, hy)
        ctx.set_line_width(6); ctx.set_source_rgba(0.9, 0.85, 0.7, 1)
        ctx.new_path(); ctx.arc(hx - 70, hy, 110, -1.05, 1.05); ctx.stroke()
        tips = [(hx - 70 + 110 * math.cos(a_), hy + 110 * math.sin(a_)) for a_ in (-1.05, 1.05)]
        ctx.set_line_width(2); ctx.set_source_rgba(0.85, 0.85, 0.85, 1)
        ctx.move_to(*tips[0]); ctx.line_to(*nock); ctx.line_to(*tips[1]); ctx.stroke()
        if t < release:
            arrow(ctx, hx + 30, hy, 0, length=hx + 30 - nock[0])
            label(ctx, setback, nock[0] - 20, hy - 120, ease((t - 0.6) / 0.4) * (1 - ease((t - release) / 0.2)),
                  size=26, col=(0.8, 0.8, 0.8))
            halo(ctx, nock[0], hy, 90, a=0.25 * draw_k)
        else:
            u = (t - release) / 0.55
            ax = lerp(hx + 30, W + 300, eio(u) if u < 1 else 1)
            if u < 1.2:
                ctx.set_line_width(3)
                for k in range(4):
                    ctx.set_source_rgba(*accent(), 0.5 - k * 0.1)
                    ctx.move_to(ax - 160 - k * 60, hy + (k - 1.5) * 4); ctx.line_to(ax - 160 - k * 60 - 120, hy + (k - 1.5) * 4)
                ctx.stroke()
                arrow(ctx, ax, hy, 0, length=150, col=accent())
            halo(ctx, W - 40, hy, 260, col=accent(), a=0.4 * ease((u - 0.8) / 0.3) * (1 - ease((u - 1.6) / 1.5)))
    return Scene(draw, duration, "bow_arrow", _cap(line1, line2))


def diamond(line1, line2="", pressure="Pressure", duration=6.4, t2=3.0, burst=2.8):
    """Two press plates crush a lump of coal, cracks glow, a flash — the plates lift and a
    faceted accent diamond turns in the light. Theme: pressure makes you, hard times."""
    cy = 1130

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        squeeze = eio(t / burst) if t < burst else 1 - eio((t - burst - 0.2) / 0.8)
        gap = lerp(320, 150, squeeze)
        shake = 3 * math.sin(t * 45) * squeeze * (t < burst)
        for d in (-1, 1):
            y = cy + d * gap / 2
            ctx.rectangle(260 + shake, y if d > 0 else y - 70, 560, 70)
            ctx.set_source_rgba(0.28, 0.28, 0.28, 1); ctx.fill_preserve()
            ctx.set_source_rgba(0.7, 0.7, 0.7, 1); ctx.set_line_width(3); ctx.stroke()
            ctx.rectangle(520 + shake, y - 300 if d < 0 else y + 70, 40, 230); ctx.set_source_rgba(0.4, 0.4, 0.4, 1)
            ctx.fill()
        label(ctx, pressure, 540 + shake, cy - gap / 2 - 25, ease(t / 0.4) * (1 - ease((t - burst) / 0.3)), size=26,
              col=(1, 1, 1))
        if t < burst:
            r = lerp(80, 60, squeeze)
            rng = random.Random(3)
            ctx.new_path()
            for k in range(11):
                a_ = k * 2 * math.pi / 11
                rr = r * (0.8 + 0.3 * rng.random())
                ctx.line_to(540 + rr * math.cos(a_), cy + rr * 0.9 * math.sin(a_))
            ctx.close_path(); ctx.set_source_rgba(0.12, 0.12, 0.12, 1); ctx.fill()
            ctx.set_line_width(3); ctx.set_source_rgba(*accent(), squeeze)
            for k in range(4):
                a_ = 0.6 + k * 1.5
                ctx.move_to(540, cy); ctx.line_to(540 + r * 0.8 * math.cos(a_), cy + r * 0.7 * math.sin(a_))
            ctx.stroke()
        else:
            u = t - burst
            halo(ctx, 540, cy, 380, col=accent(), a=0.5 * (1 - ease(u / 0.8)) + 0.12)
            spin = math.cos(u * 2.2)
            w, h = 95 * (0.35 + 0.65 * abs(spin)), 110
            top = [(540 - w, cy - 25), (540 - w * 0.5, cy - 60), (540 + w * 0.5, cy - 60), (540 + w, cy - 25)]
            polyline(ctx, top + [(540, cy + h - 30)], close=True)
            ctx.set_source_rgba(*accent(), 1); ctx.fill()
            ctx.set_line_width(2); ctx.set_source_rgba(1, 1, 1, 0.8)
            for p_ in top:
                ctx.move_to(*p_); ctx.line_to(540, cy + h - 30)
            ctx.move_to(540 - w, cy - 25); ctx.line_to(540 + w, cy - 25); ctx.stroke()
            for k in range(4):
                tw = ease((u - 0.3 - k * 0.25) / 0.2) * (1 - ease((u - 0.7 - k * 0.25) / 0.3))
                star(ctx, 540 + (-1) ** k * (120 + 30 * k), cy - 80 + 40 * k, 14, a=tw, points=4)
    return Scene(draw, duration, "diamond", _cap(line1, line2))


# ------------------------------------------------------------------ patience
def bamboo(line1, line2="", duration=6.8, t2=3.4, burst=3.9):
    """'Year 1… Year 4': nothing above ground while roots spread below; 'Year 5': the bamboo
    shoots up past the top of the frame. Theme: patience, invisible progress, late bloomers."""
    gy = 1150

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        _ground(ctx, gy, 140, 940, g=0.55)
        ctx.rectangle(140, gy, 800, 420)
        ctx.set_source(vgrad(gy, gy + 420, (0.1, 0.09, 0.08, 1), (0, 0, 0, 1))); ctx.fill()
        g = clamp(t / burst)
        rng = random.Random(5)
        ctx.set_line_width(2)
        for k in range(22):
            a_ = rng.uniform(-1.2, 1.2)
            L = rng.uniform(80, 330) * g
            ctx.set_source_rgba(1, 1, 1, 0.35)
            ctx.move_to(600, gy)
            ctx.curve_to(600 + L * 0.3 * math.sin(a_), gy + L * 0.4, 600 + L * math.sin(a_) * 0.8, gy + L * 0.8,
                         600 + L * math.sin(a_), gy + L * math.cos(a_ * 0.5))
            ctx.stroke()
        year = min(5, 1 + int(t / (burst / 4))) if t < burst else 5
        label(ctx, f"Year {year}", 300, gy - 200, ease(t / 0.3), size=40,
              col=accent() if year == 5 else (1, 1, 1), align="left")
        if t >= burst:
            ctx.save(); ctx.rectangle(0, 720, W, H); ctx.clip()  # keep the shoot below the captions
            u = eio((t - burst) / 1.2)
            h = 1300 * u
            ctx.set_line_width(22); ctx.set_source_rgba(0.85, 0.9, 0.75, 1)
            ctx.move_to(600, gy); ctx.line_to(600, gy - h); ctx.stroke()
            ctx.set_line_width(4); ctx.set_source_rgba(0.3, 0.35, 0.25, 1)
            yy = gy - 70
            while yy > gy - h:
                ctx.move_to(586, yy); ctx.line_to(614, yy)
                yy -= 90
            ctx.stroke()
            for k in range(int(h / 180)):
                ly = gy - 120 - k * 180
                d = (-1) ** k
                ctx.new_path(); ctx.save(); ctx.translate(600 + d * 50, ly); ctx.rotate(d * 0.5); ctx.scale(48, 12)
                ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore(); ctx.set_source_rgba(*accent(), 0.9); ctx.fill()
            ctx.restore()
        up = eio((t - burst - 0.3) / 0.6)
        figure(ctx, 790, gy, 50, mix(mix(STAND, SLUMP, ease((t - 1.5) / 1.5)), ARMS_UP, up), d=-1)
    return Scene(draw, duration, "bamboo", _cap(line1, line2))


# ------------------------------------------------------------------ direction
def compass(line1, line2="", target="Your why", duration=6.4, t2=3.0, lock=3.0):
    """A big compass needle spins wildly, slows, and locks onto an accent star with a label.
    Theme: purpose, direction, knowing your why, finding your path."""
    C, R = (540, 1150), 230
    lock_ang = math.atan2(800 - C[1], 830 - C[0])

    def needle_angle(t):
        if t < lock:
            return -math.pi / 2 + t * 9 + 1.5 * math.sin(t * 3.1)
        u = t - lock
        start = -math.pi / 2 + lock * 9 + 1.5 * math.sin(lock * 3.1)
        start = lock_ang + ((start - lock_ang + math.pi) % (2 * math.pi)) - math.pi
        return lock_ang + (start - lock_ang) * math.exp(-4 * u) * math.cos(10 * u)

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        ctx.arc(*C, R, 0, 2 * math.pi); ctx.set_source_rgba(0.1, 0.1, 0.1, 1); ctx.fill_preserve()
        ctx.set_source_rgba(0.85, 0.85, 0.85, 1); ctx.set_line_width(8); ctx.stroke()
        for k in range(36):
            a_ = k * math.pi / 18
            r0 = R - (30 if k % 9 == 0 else 16)
            ctx.move_to(C[0] + r0 * math.cos(a_), C[1] + r0 * math.sin(a_))
            ctx.line_to(C[0] + (R - 6) * math.cos(a_), C[1] + (R - 6) * math.sin(a_))
        ctx.set_line_width(3); ctx.stroke()
        for txt, a_ in (("N", -math.pi / 2), ("E", 0), ("S", math.pi / 2), ("W", math.pi)):
            label(ctx, txt, C[0] + (R - 60) * math.cos(a_), C[1] + (R - 60) * math.sin(a_) + 12, 0.8, size=32)
        a_ = needle_angle(t)
        ux, uy = math.cos(a_), math.sin(a_)
        px, py = -uy, ux
        L, Wd = R - 40, 26
        polyline(ctx, [(C[0] + ux * L, C[1] + uy * L), (C[0] + px * Wd, C[1] + py * Wd), (C[0] - px * Wd, C[1] - py * Wd)],
                 close=True)
        ctx.set_source_rgba(*accent(), 1); ctx.fill()
        polyline(ctx, [(C[0] - ux * L, C[1] - uy * L), (C[0] + px * Wd, C[1] + py * Wd), (C[0] - px * Wd, C[1] - py * Wd)],
                 close=True)
        ctx.set_source_rgba(0.55, 0.55, 0.55, 1); ctx.fill()
        ctx.arc(*C, 12, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
        on = ease((t - lock - 0.5) / 0.6)
        star(ctx, 830, 800, 26, a=0.25 + 0.75 * on, col=accent() if on > 0.5 else (0.6, 0.6, 0.6))
        halo(ctx, 830, 800, 140, col=accent(), a=0.35 * on)
        label(ctx, target, 830, 760, on, size=28, col=accent())
    return Scene(draw, duration, "compass", _cap(line1, line2))


def paper_plane(line1, line2="", word="Rejected", duration=6.6, t2=3.0):
    """A crumpled page labelled 'Rejected' unfolds flat, folds itself into a paper plane and
    flies off in a loop. Theme: rejection → redirection, turn failure into fuel."""
    C = (540, 1180)
    rng = random.Random(9)
    ball = [(math.cos(k * 2 * math.pi / 8) * rng.uniform(55, 80), math.sin(k * 2 * math.pi / 8) * rng.uniform(55, 80))
            for k in range(8)]
    sheet = [(-150, -110), (0, -110), (150, -110), (150, 0), (150, 110), (0, 110), (-150, 110), (-150, 0)]
    plane = [(-130, -10), (40, -18), (150, 0), (40, 6), (-90, 30), (-40, 8), (-120, 12), (-110, 0)]

    def shape(t):
        if t < 1.0:
            return ball, 0
        if t < 2.2:
            k = eio((t - 1.0) / 0.8)
            return [(lerp(a[0], b[0], k), lerp(a[1], b[1], k)) for a, b in zip(ball, sheet)], ease((t - 1.5) / 0.3)
        k = eio((t - 2.4) / 0.8)
        return [(lerp(a[0], b[0], k), lerp(a[1], b[1], k)) for a, b in zip(sheet, plane)], 1 - k

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        pts, txt_a = shape(t)
        fly = eio((t - 3.4) / (duration - 4.2))
        path = lambda f: (lerp(C[0], 830, f) - 200 * math.sin(f * math.pi * 1.5) * (1 - f),
                          C[1] - 330 * f - 110 * math.sin(f * math.pi * 2))
        ox, oy = path(fly)
        if fly > 0:
            for k in range(1, 14):
                q = clamp(fly - k * 0.03)
                ctx.arc(*path(q), 3, 0, 2 * math.pi)
                ctx.set_source_rgba(*accent(), 0.6 * (1 - k / 14)); ctx.fill()
        ang = -0.35 * fly
        ctx.save(); ctx.translate(ox, oy); ctx.rotate(ang)
        if t > 2.4:
            ctx.scale(1.5, 1.5)
        polyline(ctx, pts, close=True)
        ctx.set_source_rgba(0.8, 0.8, 0.78, 1); ctx.fill_preserve()
        ctx.set_source_rgba(0.5, 0.5, 0.5, 1); ctx.set_line_width(2); ctx.stroke()
        if t > 2.4:
            ctx.move_to(-130, -10); ctx.line_to(150, 0); ctx.stroke()
        ctx.restore()
        if txt_a > 0:
            label(ctx, word, ox, oy + 12, txt_a, size=38, col=(0.55, 0.05, 0.05), bold=True)
    return Scene(draw, duration, "paper_plane", _cap(line1, line2))


def kite(line1, line2="", winds=("Doubt", "Criticism"), duration=6.4, t2=2.9):
    """A figure flies a kite that climbs higher precisely because wind streaks labelled
    'Doubt' / 'Criticism' blow against it. Theme: adversity lifts you, opposition makes you rise."""
    gy = 1380

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        _ground(ctx, gy)
        ctx.set_line_width(3)
        for k in range(10):
            y = 820 + k * 50
            x = W - ((t * 520 + k * 211) % (W + 400))
            ctx.set_source_rgba(0.6, 0.65, 0.75, 0.5)
            ctx.move_to(x, y); ctx.curve_to(x + 60, y - 10, x + 120, y + 10, x + 200, y)
        ctx.stroke()
        for k, w_ in enumerate(winds[:2]):
            x = W - ((t * 300 + k * 520) % (W + 300))
            label(ctx, w_, x, 900 + k * 260, 0.85, size=28, col=(0.75, 0.8, 0.9))
        j = figure(ctx, 280, gy, 54, mix(STAND, dict(STAND, ua_f=2.3, fa_f=2.5), 1))
        u = eio(t / (duration - 0.8))
        kx = lerp(420, 760, u) + 25 * math.sin(t * 2)
        ky = lerp(1150, 820, u) + 20 * math.sin(t * 2.7)
        hx, hy = j["hand_f"]
        ctx.set_line_width(1.6); ctx.set_source_rgba(0.85, 0.85, 0.85, 1)
        ctx.move_to(hx, hy); ctx.curve_to(hx + 120, hy - 60, kx - 140, ky + 160, kx, ky + 60); ctx.stroke()
        rot = 0.25 + 0.1 * math.sin(t * 2.2)
        ctx.save(); ctx.translate(kx, ky); ctx.rotate(rot)
        polyline(ctx, [(0, -70), (45, 0), (0, 70), (-45, 0)], close=True)
        ctx.set_source_rgba(*accent(), 1); ctx.fill()
        ctx.set_line_width(2); ctx.set_source_rgba(1, 1, 1, 0.8)
        ctx.move_to(0, -70); ctx.line_to(0, 70); ctx.move_to(-45, 0); ctx.line_to(45, 0); ctx.stroke()
        ctx.new_path(); ctx.move_to(0, 70)
        for k in range(1, 9):
            ctx.line_to(14 * math.sin(t * 6 + k), 70 + k * 18)
        ctx.stroke()
        ctx.restore()
    return Scene(draw, duration, "kite", _cap(line1, line2))


# ------------------------------------------------------------------ letting go
def backpack_drop(line1, line2="", burdens=("What ifs", "Grudges", "Regret"), duration=6.6, t2=3.2, drop=3.0):
    """Labelled rocks fall into a figure's backpack one by one and it bends under the weight;
    it drops the pack, straightens, glows and walks on. Theme: letting go, overthinking, baggage."""
    gy = 1360
    burdens = list(burdens)[:3]

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        _ground(ctx, gy)
        loads = sum(1 for k in range(len(burdens)) if t > 0.5 + k * 0.75 + 0.35)
        bend = clamp(loads / 3) if t < drop else 1 - eio((t - drop - 0.3) / 0.6)
        walk_u = eio((t - drop - 1.0) / (duration - drop - 1.6))
        x = 480 + 230 * walk_u
        pose = mix(STAND, SLUMP, bend * 0.9)
        if 0 < walk_u < 1:
            pose = walk((x - 480) / 34)
        halo(ctx, x, gy - 110, 240, a=0.2 * ease((t - drop - 0.6) / 0.6))
        j = figure(ctx, x, gy, 58, pose)
        if t < drop:
            sx, sy = j["shoulder"]
            bx, by = sx - 40, sy + 40
        else:
            u = clamp((t - drop) / 0.35)
            bx, by = lerp(j["shoulder"][0] - 40, 400, u) if t < drop + 0.35 else 400, lerp(1180, gy - 60, u * u)
        backpack(ctx, bx, by, 0.85)
        for k, txt in enumerate(burdens):
            t0 = 0.5 + k * 0.75
            u = eio((t - t0) / 0.35)
            if u <= 0:
                continue
            if t < drop:
                rx, ry = lerp(bx, bx, u), lerp(760, by - 70 - k * 4, u)
                a_ = 1 - ease((t - t0 - 0.35) / 0.25)
                rock(ctx, rx, ry, 0.55, a=max(a_, 0))
                label(ctx, txt, rx + 90, ry - 18, max(a_, 0), size=24, align="left")
            else:
                spill = ease((t - drop - 0.3) / 0.4)
                rx = 400 - 120 + k * 120 * spill + 40
                rock(ctx, lerp(400, rx, spill), gy, 0.5, a=spill * 0.8)
                label(ctx, txt, lerp(400, rx, spill), gy + 40, spill * 0.6, size=20)
    return Scene(draw, duration, "backpack_drop", _cap(line1, line2))


def notification_swarm(line1, line2="", duration=6.6, t2=3.2, off=3.0):
    """Notification badges swarm a figure hunched over a phone, faster and denser; the phone
    goes dark, the badges pop away, the figure stands up in calm under a moon.
    Theme: distraction, peace, reclaim your attention, social media."""
    gy = 1370
    rng = random.Random(4)
    dots = [(rng.uniform(0, 6.28), rng.uniform(140, 330), rng.uniform(1.2, 3.2), rng.choice(["1", "3", "9+", "2", "!"]),
             rng.uniform(0, 2.4)) for _ in range(26)]

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        _ground(ctx, gy)
        calm = ease((t - off - 0.6) / 0.8)
        moon(ctx, 820, 850, 34, a=calm)
        up = eio((t - off - 0.4) / 0.9)
        j = figure(ctx, 540, gy, 56, mix(PHONE, STAND, up))
        if t < off + 0.3:
            phone(ctx, j["hand_f"][0] + 6, j["hand_f"][1] - 10, 0.55, glow=1 - ease((t - off) / 0.2), angle=-0.4)
        cx, cy = 540, gy - 140
        for ang0, r, sp, txt, born in dots:
            if t < born:
                continue
            pop = (off + 0.1 + (ang0 % 1) * 0.5)
            a_ = ease((t - born) / 0.3) * (1 - ease((t - pop) / 0.12))
            if a_ <= 0:
                continue
            ang = ang0 + t * sp
            x, y = cx + r * math.cos(ang), cy + r * 0.7 * math.sin(ang)
            sc = 1 + 0.6 * ease((t - pop + 0.1) / 0.1) if t > pop - 0.1 else 1
            ctx.arc(x, y, 20 * sc, 0, 2 * math.pi); ctx.set_source_rgba(0.85, 0.85, 0.85, a_); ctx.fill()
            label(ctx, txt, x, y + 7, a_, size=18, col=(0.05, 0.05, 0.05), bold=True)
        halo(ctx, 540, gy - 110, 260, a=0.15 * calm)
    return Scene(draw, duration, "notification_swarm", _cap(line1, line2))


# ------------------------------------------------------------------ missed chances
def train_leaving(line1, line2="", sign="Someday", duration=6.4, t2=3.0):
    """A figure runs onto the platform just as the train (lit windows) pulls away and
    leaves; it stops and slumps under a sign. Theme: 'someday' never comes, missed chances, act now."""
    gy = 1330

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        ctx.rectangle(110, gy, W - 220, 30); ctx.set_source_rgba(0.25, 0.25, 0.25, 1); ctx.fill()
        _ground(ctx, gy + 60, 110, W - 110, g=0.3)
        signpost(ctx, 250, gy, [sign])
        go = clamp((t - 0.8) / 3.0)
        front = 1180 + 1500 * go * go
        ctx.save(); ctx.translate(0, 0)
        train_prop(ctx, front, gy + 55, cars=4)
        ctx.restore()
        u = clamp((t - 0.6) / 2.6)
        x = lerp(-60, 760, u)
        if u < 1:
            pose = run((x + 60) / 30)
        else:
            pose = mix(STAND, SLUMP, ease((t - 3.4) / 0.6))
        figure(ctx, x, gy, 52, pose)
        if u >= 1:
            ctx.set_line_width(2); ctx.set_source_rgba(0.7, 0.7, 0.7, 1 - ease((t - 4.5) / 0.5))
            for k in range(3):
                ctx.move_to(x + 40 + k * 8, gy - 200 - k * 10); ctx.line_to(x + 50 + k * 8, gy - 214 - k * 10)
            ctx.stroke()
    return Scene(draw, duration, "train_leaving", _cap(line1, line2))


# ------------------------------------------------------------------ comparison
def bloom_row(line1, line2="", duration=6.6, t2=3.0):
    """Five plants in a row bloom at different times; the last, latest one opens biggest
    in the accent colour. Theme: everyone blooms in their own time, don't compare."""
    gy = 1360
    xs = [220, 380, 540, 700, 860]
    times = [0.4, 1.0, 1.9, 2.6, 3.6]
    heights = [150, 120, 170, 135, 240]

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        _ground(ctx, gy)
        for k, (x, t0, h) in enumerate(zip(xs, times, heights)):
            last = k == len(xs) - 1
            b = clamp((t - t0) / (1.4 if last else 0.9))
            if last:
                halo(ctx, x, gy - h, 200, col=accent(), a=0.3 * ease((b - 0.6) / 0.4))
            flower(ctx, x, gy, h, bloom=max(b, 0.02), col=accent() if last else (0.85, 0.85, 0.85), t=t + k)
            if last and b > 0.5:  # bigger second ring of petals for the late bloomer
                o = ease((b - 0.5) / 0.5)
                for q in range(8):
                    ang = q * math.pi / 4 + 0.4
                    ctx.new_path(); ctx.save(); ctx.translate(x + math.cos(ang) * 30 * o, gy - h + math.sin(ang) * 30 * o)
                    ctx.rotate(ang); ctx.scale(26 * o, 12 * o); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
                    ctx.set_source_rgba(*accent(), 0.6); ctx.fill()
            polyline(ctx, [(x - 32, gy), (x + 32, gy), (x + 24, gy + 50), (x - 24, gy + 50)], close=True)
            ctx.set_source_rgba(0.3, 0.3, 0.3, 1); ctx.fill()
    return Scene(draw, duration, "bloom_row", _cap(line1, line2))


# ------------------------------------------------------------------ resilience
def fall_rise(line1, line2="", falls=7, duration=6.8, t2=3.4):
    """The figure falls and gets back up again and again with a counter; on the last rise it
    stays up, arms raised, counter in accent. Theme: fall seven times, stand up eight."""
    gy = 1340
    cyc = 0.62
    end = 0.4 + falls * cyc

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        _ground(ctx, gy)
        if t < end:
            k = int((t - 0.4) / cyc) if t > 0.4 else -1
            u = ((t - 0.4) % cyc) / cyc if t > 0.4 else 0
            down = ease(u / 0.35) if u < 0.5 else 1 - eio((u - 0.5) / 0.5)
            pose = mix(STAND, LIE, down)
            count = max(k + 1, 0)
            col = (1, 1, 1)
        else:
            pose = mix(STAND, ARMS_UP, eio((t - end - 0.2) / 0.5))
            count = falls + 1
            col = accent()
            halo(ctx, 520, gy - 120, 280, col=accent(), a=0.25 * ease((t - end) / 0.6))
        figure(ctx, 520, gy, 58, pose)
        if count:
            label(ctx, str(count), 760, gy - 160, 1, size=72, col=col, bold=True)
    return Scene(draw, duration, "fall_rise", _cap(line1, line2))


# ------------------------------------------------------------------ focus
def juggle(line1, line2="", balls=("Likes", "Drama", "Money", "Opinions"), keep="Health", duration=6.6, t2=3.0,
           drop=2.9):
    """A figure juggles labelled balls, then lets them all fall and bounce away, holding only
    the one that matters, glowing in accent. Theme: focus, priorities, drop what doesn't matter."""
    gy = 1360
    names = list(balls)[:4] + [keep]
    n = len(names)

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        _ground(ctx, gy)
        hold = eio((t - drop - 0.4) / 0.5)
        j = figure(ctx, 540, gy, 58, mix(dict(STAND, ua_f=1.0, fa_f=2.0, ua_b=-1.0, fa_b=-2.0), CARRY, hold), d=1)
        cx, cy = 540, gy - 330
        for k, name in enumerate(names):
            is_keep = k == n - 1
            ph = t * 2.6 + k * 2 * math.pi / n
            jx, jy = cx + 170 * math.cos(ph), cy - 150 * abs(math.sin(ph))
            if t < drop:
                x, y = jx, jy
            else:
                u = t - drop
                ph0 = drop * 2.6 + k * 2 * math.pi / n
                x0, y0 = cx + 170 * math.cos(ph0), cy - 150 * abs(math.sin(ph0))
                if is_keep:
                    hx, hy = j["hand_f"]
                    x, y = lerp(x0, hx + 20, eio(u / 0.5)), lerp(y0, hy - 30, eio(u / 0.5))
                else:
                    tt = u
                    fall_y = y0 + 900 * tt * tt
                    if fall_y > gy - 32:
                        t_hit = math.sqrt((gy - 32 - y0) / 900)
                        tb = tt - t_hit
                        fall_y = gy - 32 - max(0, 260 * tb - 900 * tb * tb)
                    x = x0 + (-1) ** k * 120 * u
                    y = fall_y
            col = accent() if is_keep and t > drop else (0.85, 0.85, 0.85)
            a_ = 1 if is_keep or t < drop else max(0.35, 1 - (t - drop) / 2)
            if is_keep and t > drop:
                halo(ctx, x, y, 150, col=accent(), a=0.3 * hold)
            ctx.arc(x, y, 38, 0, 2 * math.pi); ctx.set_source_rgba(*col, a_); ctx.fill()
            label(ctx, name, x, y + 6, a_, size=17, col=(0.05, 0.05, 0.05), bold=True)
    return Scene(draw, duration, "juggle", _cap(line1, line2))


def rocket(line1, line2="", stages=("Excuses", "Fear", "Doubt"), duration=6.8, t2=3.2):
    """A rocket lifts off; stages labelled with what holds you back detach one by one and
    fall away, the glowing capsule streaks up through the stars. Theme: shed what weighs you
    down, ambition, launch."""
    stages = list(stages)[:3]
    n = len(stages)
    pad, h = 1420, 90
    rng = random.Random(2)
    stars_ = [(rng.uniform(120, W - 120), rng.uniform(0, 900)) for _ in range(60)]
    drops = [2.0 + k * 0.75 for k in range(n)]          # bottom stage drops first

    def draw(ctx, t):
        rise = max(0.0, t - 0.8)
        alt = 220 * rise * rise
        cb0 = pad - n * h                                   # capsule bottom on the pad
        cb = max(1000.0, cb0 - alt)                         # camera holds the capsule at y=1000
        cam = (cb0 - alt) - cb if cb0 - alt < 1000 else 0.0  # how far the world has scrolled
        speed = 440 * rise
        for sx, sy in stars_:
            y = (sy + cam * 0.5) % 900 + 720
            ctx.set_line_width(2); ctx.set_source_rgba(1, 1, 1, 0.45)
            ctx.move_to(sx, y); ctx.line_to(sx, y - min(60, speed * 0.04)); ctx.stroke()
        if pad - cam < H:
            _ground(ctx, pad - cam, g=0.5)
        attached = n
        for i in range(n):                                  # i = 0 is the stage under the capsule
            k = n - 1 - i                                   # drop order
            y_top = cb + i * h
            label_txt = stages[i]
            if t < drops[k]:
                ctx.rectangle(500, y_top, 80, h); ctx.set_source_rgba(0.75, 0.75, 0.75, 1); ctx.fill()
                ctx.set_line_width(2); ctx.set_source_rgba(0.2, 0.2, 0.2, 1)
                ctx.move_to(500, y_top); ctx.line_to(580, y_top); ctx.stroke()
                label(ctx, label_txt, 600, y_top + h / 2 + 8, 1, size=24, align="left")
            else:
                attached = min(attached, i)
                u = t - drops[k]
                d = (-1) ** i
                y = y_top + 380 * u * u + 160 * u
                ctx.save(); ctx.translate(540 + d * 70 * u, y + h / 2); ctx.rotate(d * 0.9 * u)
                ctx.rectangle(-40, -h / 2, 80, h); ctx.set_source_rgba(0.5, 0.5, 0.5, max(0, 1 - u)); ctx.fill()
                ctx.restore()
                label(ctx, label_txt, 540 + d * (70 * u + 90), y + h / 2, max(0, 1 - u * 1.5), size=22,
                      col=(0.6, 0.6, 0.6), align="left" if d > 0 else "right")
        polyline(ctx, [(500, cb), (580, cb), (580, cb - 60), (540, cb - 140), (500, cb - 60)], close=True)
        ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
        ctx.arc(540, cb - 60, 14, 0, 2 * math.pi); ctx.set_source_rgba(*accent(), 1); ctx.fill()
        if t > 0.6:
            flame(ctx, 540, cb + attached * h + 10 + 60 * min(1, t / 3), 80, t=t, col=accent())
        halo(ctx, 540, cb - 60, 220, col=accent(), a=0.25 * ease((t - drops[-1]) / 0.6))
        caption(ctx, t, line1, line2, t2)
    return Scene(draw, duration, "rocket", _cap(line1, line2))


# ------------------------------------------------------------------ calm
def breathe(line1, line2="", duration=6.6, t2=3.2):
    """A circle slowly expands and contracts ('inhale' / 'exhale'); a jittery figure in the
    middle calms down and syncs with it. Text-led, very calm. Theme: anxiety, slow down, peace."""
    C = (540, 1130)

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        b = 0.5 - 0.5 * math.cos(t * 2 * math.pi / 4.0)
        R = 170 + 130 * b
        halo(ctx, *C, R * 1.4, col=accent(), a=0.10 + 0.12 * b)
        ctx.arc(*C, R, 0, 2 * math.pi); ctx.set_source_rgba(*accent(), 0.8); ctx.set_line_width(4); ctx.stroke()
        for k in range(24):
            a_ = k * math.pi / 12 + t * 0.2
            ctx.arc(C[0] + (R + 26) * math.cos(a_), C[1] + (R + 26) * math.sin(a_), 3, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, 0.4); ctx.fill()
        word = "inhale" if math.sin(t * 2 * math.pi / 4.0) >= 0 else "exhale"
        label(ctx, word, C[0], C[1] + R + 90, 0.8, size=30)
        calm = ease((t - 1.0) / 2.5)
        jit = (1 - calm) * 10 * math.sin(t * 37)
        pose = mix(dict(STAND, ua_f=2.6, fa_f=3.4, ua_b=-2.6, fa_b=-3.4), STAND, calm)
        figure(ctx, C[0] + jit, C[1] + 95, 44, pose, bob=8 * b * calm)
    return Scene(draw, duration, "breathe", _cap(line1, line2))


# ------------------------------------------------------------------ no shortcuts
def shortcut(line1, line2="", short="Shortcut", long_="The long way", duration=6.6, t2=3.2):
    """Two lanes: top figure takes a 'Shortcut' straight into a swamp and sinks; bottom figure
    walks a winding road and reaches the accent flag. Theme: no shortcuts, patience pays."""
    ty, by = 1000, 1440
    road = [(150, by), (300, by - 70), (450, by), (600, by - 70), (750, by), (900, by - 70)]

    def along(pts, f):
        seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
        L = sum(seg) * f
        for (a, b), s_ in zip(zip(pts, pts[1:]), seg):
            if L <= s_:
                k = L / s_
                return (lerp(a[0], b[0], k), lerp(a[1], b[1], k))
            L -= s_
        return pts[-1]

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        ctx.set_line_width(1.5); ctx.set_source_rgba(0.3, 0.3, 0.3, 1)
        ctx.move_to(120, 1150); ctx.line_to(W - 120, 1150); ctx.stroke()
        _ground(ctx, ty, 130, 420)
        ctx.rectangle(420, ty - 4, 520, 120)
        ctx.set_source(vgrad(ty, ty + 120, (0.12, 0.14, 0.1, 1), (0, 0, 0, 1))); ctx.fill()
        for k in range(5):
            ph = (t * 0.8 + k * 0.29) % 1
            ctx.arc(460 + k * 100, ty + 10 - 20 * ph, 6 * (1 - ph), 0, 2 * math.pi)
            ctx.set_source_rgba(0.5, 0.6, 0.45, 1 - ph); ctx.stroke()
        label(ctx, short, 280, ty - 230, ease(t / 0.4), size=28, col=(1, 1, 1))
        u = clamp((t - 0.4) / 1.6)
        x = lerp(160, 520, u)
        sink = 0 if u < 1 else ease((t - 2.0) / 2.0) * 200
        ctx.save(); ctx.rectangle(0, 700, W, ty - 700 + 2); ctx.clip()
        figure(ctx, x, ty + sink, 46, walk((x - 160) / 30) if u < 1 else mix(STAND, ARMS_UP, ease((t - 2.0) / 0.4)),
               col=(0.75, 0.75, 0.75))
        ctx.restore()
        polyline(ctx, road)
        ctx.set_line_width(6); ctx.set_source_rgba(0.45, 0.45, 0.45, 1); ctx.stroke()
        label(ctx, long_, 280, by - 230, ease(t / 0.4), size=28, col=(1, 1, 1))
        f = clamp((t - 0.4) / (duration - 1.8))
        px, py = along(road, f)
        fa = ease((f - 0.95) / 0.05)
        ctx.set_line_width(4); ctx.set_source_rgba(1, 1, 1, 1)
        ctx.move_to(930, by - 70); ctx.line_to(930, by - 190); ctx.stroke()
        polyline(ctx, [(930, by - 190), (985, by - 175), (930, by - 160)], close=True)
        ctx.set_source_rgba(*accent(), 1); ctx.fill()
        halo(ctx, 940, by - 170, 160, col=accent(), a=0.35 * fa)
        figure(ctx, px, py, 46, walk(f * 40) if f < 1 else ARMS_UP)
    return Scene(draw, duration, "shortcut", _cap(line1, line2))


# ------------------------------------------------------------------ journey
def lantern_walk(line1, line2="", duration=6.6, t2=3.2):
    """A figure walks through a dark forest holding a lantern that lights only the nearest
    trunks (three parallax layers), until the trees open onto a dawn glow.
    Theme: you only need to see the next step, faith, walking alone."""
    gy = 1390
    rng = random.Random(6)
    layers = [[(rng.uniform(-200, 3200), rng.uniform(16, 34)) for _ in range(14)] for _ in range(3)]

    def draw(ctx, t):
        speed = 230
        scroll = t * speed
        dawn = ease((t - (duration - 2.6)) / 1.6)
        halo(ctx, W - 80, gy - 120, 600, col=accent(), a=0.35 * dawn)
        ctx.save(); ctx.rectangle(0, 720, W, H); ctx.clip()
        for li, (depth, shade) in enumerate(((0.35, 0.04), (0.6, 0.07), (1.0, 0.10))):
            for tx, w in layers[li]:
                x = (tx - scroll * depth) % 3400 - 200
                if x > W - 200 * dawn - 100 and dawn > 0:
                    continue
                d = abs(x - 520)
                lit = (1 - clamp(d / 340)) ** 2 * (0.12 if li < 2 else 0.3)
                trunk(ctx, x, gy, 670, w * (0.6 + depth * 0.6), shade=shade + lit)
        ctx.restore()
        _ground(ctx, gy, 0, W, g=0.3)
        j = figure(ctx, 520, gy, 50, walk(t * 4.2))
        hx, hy = j["hand_f"]
        ctx.set_line_width(2); ctx.set_source_rgba(0.6, 0.6, 0.6, 1)
        ctx.move_to(hx, hy); ctx.line_to(hx + 6, hy + 30); ctx.stroke()
        rounded_rect(ctx, hx - 10, hy + 30, 32, 40, 6)
        ctx.set_source_rgba(0.3, 0.3, 0.3, 1); ctx.fill()
        flame(ctx, hx + 6, hy + 64, 26, t=t, col=(1, 0.85, 0.55))
        halo(ctx, hx + 6, hy + 50, 330, col=(1, 0.85, 0.55), a=0.22)
        caption(ctx, t, line1, line2, t2)
    return Scene(draw, duration, "lantern_walk", _cap(line1, line2))


# ------------------------------------------------------------------ self-worth
def inner_light(line1, line2="", doubts=("not enough", "too late", "who are you?"), duration=6.6, t2=3.2):
    """A dim slumped figure surrounded by grey doubt words; a small light appears in its
    chest and grows, the figure straightens and the words dissolve as the light reaches them.
    Theme: self-worth, inner strength, confidence."""
    gy = 1360
    spots = [(260, 1000), (800, 960), (330, 1210), (780, 1200)]

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        _ground(ctx, gy, g=0.25)
        g = eio((t - 1.4) / 3.0)
        R = 20 + 520 * g
        rise = eio((t - 2.0) / 1.4)
        col = tuple(lerp(0.35, 1, rise) for _ in range(3))
        j = figure(ctx, 540, gy, 58, mix(SLUMP, dict(STAND, lean=-0.04), rise), col=col)
        cx, cy = lerp(j["hip"][0], j["neck"][0], 0.65), lerp(j["hip"][1], j["neck"][1], 0.65)
        if t > 1.4:
            halo(ctx, cx, cy, R, col=accent(), a=0.35)
            ctx.arc(cx, cy, 6 + 6 * g, 0, 2 * math.pi); ctx.set_source_rgba(*accent(), ease((t - 1.4) / 0.3)); ctx.fill()
        for k, txt in enumerate(list(doubts)[:4]):
            x, y = spots[k]
            d = math.hypot(x - cx, y - cy)
            fade = 1 - ease((R - d + 60) / 120)
            a_ = ease((t - 0.2 - k * 0.3) / 0.4) * fade
            label(ctx, txt, x + 6 * math.sin(t * 1.3 + k), y, a_ * 0.7, size=28, col=(0.55, 0.55, 0.55))
    return Scene(draw, duration, "inner_light", _cap(line1, line2))


# ------------------------------------------------------------------ people
def plank_bridge(line1, line2="", helper="A real friend", planks=6, duration=6.8, t2=3.2):
    """The hero is stuck on a cliff edge; from the other side a friend lays planks one by one
    to bridge the gap, then they stand together. Theme: support, real friends, community."""
    gy, e1, e2 = 1300, 360, 760
    pw = (e2 - e1) / planks

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        for pts in ([(110, gy), (e1, gy), (e1 - 20, gy + 120), (e1 + 10, 1640), (110, 1640)],
                    [(W - 110, gy), (e2, gy), (e2 + 20, gy + 120), (e2 - 10, 1640), (W - 110, 1640)]):
            polyline(ctx, pts, close=True)
            ctx.set_source(vgrad(gy, 1640, (0.16, 0.16, 0.16, 1), (0, 0, 0, 1))); ctx.fill()
            polyline(ctx, pts[:3]); ctx.set_source_rgba(0.7, 0.7, 0.7, 1); ctx.set_line_width(4); ctx.stroke()
        laid = 0
        for k in range(planks):
            t0 = 0.6 + k * 0.42
            u = eio((t - t0) / 0.3)
            if u <= 0:
                continue
            laid = k + 1
            x = e2 - (k + 1) * pw
            ctx.rectangle(x + 2, gy - 6 - 30 * (1 - u), pw - 4, 14)
            ctx.set_source_rgba(0.75, 0.62, 0.45, u); ctx.fill()
        done = 0.6 + planks * 0.42 + 0.3
        hx = 260
        cross = eio((t - done) / 1.2)
        hx = lerp(260, 600, cross)
        figure(ctx, hx, gy, 52, walk((hx - 260) / 32) if 0 < cross < 1 else STAND)
        fx = lerp(e2 + 70, e2 + 30, ease(laid / planks)) if t < done else lerp(e2 + 30, 700, cross)
        busy = t < done
        figure(ctx, fx, gy, 52, mix(CARRY, KNEEL, 0.5 + 0.5 * math.sin(t * 7)) if busy else STAND, d=-1)
        label(ctx, helper, fx, gy + 60, ease((t - 0.3) / 0.4), size=24)
        halo(ctx, (hx + fx) / 2, gy - 110, 260, col=accent(), a=0.25 * ease((cross - 0.8) / 0.2))
    return Scene(draw, duration, "plank_bridge", _cap(line1, line2))


MORE_TEMPLATES = {
    "water_drop": water_drop, "snowball": snowball, "shadow_monster": shadow_monster, "lighthouse": lighthouse,
    "bow_arrow": bow_arrow, "diamond": diamond, "bamboo": bamboo, "compass": compass, "paper_plane": paper_plane,
    "kite": kite, "backpack_drop": backpack_drop, "notification_swarm": notification_swarm,
    "train_leaving": train_leaving, "bloom_row": bloom_row, "fall_rise": fall_rise, "juggle": juggle,
    "rocket": rocket, "breathe": breathe, "shortcut": shortcut, "lantern_walk": lantern_walk,
    "inner_light": inner_light, "plank_bridge": plank_bridge,
}
