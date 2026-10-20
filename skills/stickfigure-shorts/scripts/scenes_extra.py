"""More scene templates — each uses a different kind of motion or framing so episodes
can look different from each other: zoom-out reveals, chain reactions, transformations,
top-down views, physics, text-led scenes."""
import math
import random
from engine import *  # noqa: F401,F403


def _cap(line1, line2):
    return " / ".join(x for x in (line1, line2) if x)


def _sub(ctx, text, x, y, a, size=26, col=(0.7, 0.7, 0.7)):
    label(ctx, text, x, y, a, size=size, col=col)


# ---------------------------------------------------------------- chain reaction
def domino(line1, line2="", first="1 habit", last="Your life", count=7, duration=6.6, t2=2.8):
    """A tiny figure flicks the first tiny domino; each next one is bigger; the last one is
    huge and lands with a shake. Theme: small habits compound, one decision changes everything."""
    hs = [min(36 * 1.40 ** i, 290) for i in range(count)]
    ws = [h * 0.24 for h in hs]
    gaps = [h * 0.62 for h in hs]
    total = sum(ws) + sum(gaps[:-1]) + hs[-1]  # the last one ends up lying flat
    lefts, x = [], CX - total / 2 + 30
    for i in range(count):
        lefts.append(x)
        x += ws[i] + gaps[i]
    gy = 1360
    t0s = [1.25 + i * 0.40 for i in range(count)]
    fds = [0.30 + 0.05 * i for i in range(count)]
    rest = [math.asin(min(1.0, (gaps[i] + 2) / hs[i])) for i in range(count - 1)] + [math.pi / 2]

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        land = t0s[-1] + fds[-1]
        shake = 7 * math.exp(-8 * (t - land)) * math.sin(60 * (t - land)) if t > land else 0
        ctx.save(); ctx.translate(0, shake)
        ctx.set_line_width(3); ctx.set_source_rgba(0.4, 0.4, 0.4, 1)
        ctx.move_to(lefts[0] - 170, gy); ctx.line_to(lefts[-1] + ws[-1] + hs[-1] + 20, gy); ctx.stroke()
        flick = ease((t - 0.7) / 0.5)
        figure(ctx, lefts[0] - 48, gy, 26, mix(STAND, PUSH, flick))
        for i in range(count):
            k = clamp((t - t0s[i]) / fds[i])
            ang = rest[i] * k * k
            ctx.save()
            ctx.translate(lefts[i] + ws[i], gy); ctx.rotate(ang)
            ctx.rectangle(-ws[i], -hs[i], ws[i], hs[i])
            last_lit = i == count - 1 and k >= 1
            ctx.set_source_rgba(0.14, 0.14, 0.14, 1); ctx.fill_preserve()
            ctx.set_source_rgba(*(accent() if last_lit else (0.9, 0.9, 0.9)), 1)
            ctx.set_line_width(2 + i * 0.5); ctx.stroke()
            for py in (0.27, 0.73):
                ctx.arc(-ws[i] / 2, -hs[i] * py, ws[i] * 0.13, 0, 2 * math.pi)
                ctx.fill()
            ctx.move_to(-ws[i] * 0.85, -hs[i] / 2); ctx.line_to(-ws[i] * 0.15, -hs[i] / 2); ctx.stroke()
            ctx.restore()
        _sub(ctx, first, lefts[0] + ws[0] / 2, gy + 50, ease((t - 0.3) / 0.4))
        _sub(ctx, last, lefts[-1] + ws[-1] + hs[-1] / 2, gy + 50, ease((t - land) / 0.4),
             size=30, col=accent())
        ctx.restore()
    return Scene(draw, duration, "domino", _cap(line1, line2))


# ---------------------------------------------------------------- breaking free
def _chain(ctx, p0, p1, a=1.0):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    if L < 4:
        return
    n = max(2, int(L / 22))
    ang = math.atan2(dy, dx)
    ctx.set_source_rgba(0.75, 0.75, 0.75, a); ctx.set_line_width(3)
    for k in range(n):
        cx, cy = p0[0] + dx * (k + 0.5) / n, p0[1] + dy * (k + 0.5) / n
        ctx.new_path(); ctx.save(); ctx.translate(cx, cy); ctx.rotate(ang)
        if k % 2 == 0:
            ctx.scale(1, 0.5); ctx.arc(0, 0, 13, 0, 2 * math.pi); ctx.restore()
        else:
            ctx.move_to(-11, 0); ctx.line_to(11, 0); ctx.restore()
        ctx.stroke()


def chain_break(line1, line2="", weight="Excuses", duration=6.4, t2=2.8, snap=2.7):
    """Figure strains against a ball-and-chain, the chain snaps with a flash, figure runs free.
    Theme: excuses, bad habits, past, fear holding you back."""
    gy, bx, R = 1330, 270, 72

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        ctx.set_line_width(3); ctx.set_source_rgba(0.35, 0.35, 0.35, 1)
        ctx.move_to(120, gy); ctx.line_to(W - 120, gy); ctx.stroke()
        anchor = (bx + R * 0.95, gy - R * 0.45)
        if t < snap:
            x = 560 + 3 * math.sin(t * 23) * ease(t / 0.4)
            p = walk(t * 7.5, stride=0.30); p["lean"] = 0.5
            j = figure(ctx, x, gy, 58, p)
            ankle = j["foot_b"]
            _chain(ctx, anchor, ankle)
        else:
            u = clamp((t - snap) / (duration - snap - 0.9))
            x = 560 + 330 * eio(u)
            pose = run((x - 560) / 30) if u < 1 else STAND
            halo(ctx, x, gy - 100, 240, a=0.18 * ease((t - snap - 0.4) / 0.6))
            j = figure(ctx, x, gy, 58, pose)
            mid = ((anchor[0] + 470) / 2, gy - 24)
            fall = ease((t - snap) / 0.3)
            _chain(ctx, anchor, (lerp(mid[0], mid[0] - 30, fall), lerp(mid[1], gy - 6, fall)),
                   a=lerp(1, 0.45, fall))
            ankle = j["foot_b"]
            _chain(ctx, ankle, (ankle[0] - lerp(70, 40, fall), gy - 5), a=0.8)
            halo(ctx, 470, gy - 30, 160, a=0.6 * (1 - ease((t - snap) / 0.45)))
        ctx.arc(bx, gy - R, R, 0, 2 * math.pi)
        ctx.set_source_rgba(0.16, 0.16, 0.16, 1); ctx.fill_preserve()
        ctx.set_source_rgba(0.7, 0.7, 0.7, 1); ctx.set_line_width(4); ctx.stroke()
        label(ctx, weight, bx, gy - R + 9, ease(t / 0.4), size=24, col=(1, 1, 1))
    return Scene(draw, duration, "chain_break", _cap(line1, line2))


# ---------------------------------------------------------------- self vs self
def mirror(line1, line2="", reflection="Yesterday", duration=6.4, t2=2.8):
    """Figure looks in a mirror; the reflection becomes a slumped grey 'yesterday' version
    while the real figure straightens, glows and steps forward. Theme: compete with yourself."""
    gy, mx0, mx1, my0 = 1340, 560, 840, 960

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        ctx.set_line_width(3); ctx.set_source_rgba(0.35, 0.35, 0.35, 1)
        ctx.move_to(130, gy); ctx.line_to(W - 130, gy); ctx.stroke()
        rounded_rect(ctx, mx0, my0, mx1 - mx0, gy - 20 - my0, 20)
        ctx.set_source(vgrad(my0, gy, (0.10, 0.11, 0.12, 1), (0.03, 0.03, 0.03, 1))); ctx.fill()
        change = eio((t - 1.8) / 0.9)
        rx = 2 * mx0 - 430  # reflection of the figure's starting spot
        ctx.save()
        rounded_rect(ctx, mx0, my0, mx1 - mx0, gy - 20 - my0, 20); ctx.clip()
        shade = lerp(0.7, 0.33, change)
        figure(ctx, rx, gy - 20, 58, mix(STAND, SLUMP, change), col=(shade,) * 3, d=-1)
        for k in range(3):  # glass glints
            ctx.set_source_rgba(1, 1, 1, 0.05)
            ctx.move_to(mx0 + 30 + k * 60, my0); ctx.line_to(mx0 - 40 + k * 60, gy); ctx.set_line_width(14)
            ctx.stroke()
        ctx.restore()
        rounded_rect(ctx, mx0, my0, mx1 - mx0, gy - 20 - my0, 20)
        ctx.set_source_rgba(0.75, 0.75, 0.75, 1); ctx.set_line_width(6); ctx.stroke()
        for lx in (mx0 + 30, mx1 - 30):
            ctx.move_to(lx, gy - 20); ctx.line_to(lx + (12 if lx > CX else -12), gy); ctx.stroke()
        _sub(ctx, reflection, (mx0 + mx1) / 2, my0 - 24, ease((t - 2.3) / 0.4))
        step = eio((t - 3.4) / 1.4)
        x = 430 + 60 * step
        pose = walk((x - 430) / 34) if 0 < step < 1 else STAND
        halo(ctx, x, gy - 110, 260, a=0.22 * ease((t - 2.4) / 0.8))
        figure(ctx, x, gy, 58, pose)
    return Scene(draw, duration, "mirror", _cap(line1, line2))


def tug_of_war(line1, line2="", left="Old you", right="New you", duration=6.4, t2=2.8):
    """Two figures pull a rope; it wobbles, then the bright one wins and the grey one
    stumbles. Theme: inner battle, habits vs goals, discipline vs comfort."""
    gy = 1330

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        win = eio((t - 3.0) / 1.3)
        shift = 22 * math.sin(t * 2.4) * (1 - win) + 150 * win
        ctx.set_line_width(3); ctx.set_source_rgba(0.35, 0.35, 0.35, 1)
        ctx.move_to(110, gy); ctx.line_to(W - 110, gy); ctx.stroke()
        ctx.set_source_rgba(0.6, 0.6, 0.6, 1)
        ctx.move_to(CX, gy - 14); ctx.line_to(CX, gy + 14); ctx.stroke()
        jit = 2 * math.sin(t * 31)
        lpose = mix(PULL, SLUMP, ease((t - 4.0) / 0.6))
        lj = figure(ctx, 330 + shift + jit, gy, 54, lpose, col=(0.38,) * 3,
                    alpha=lerp(1, 0.55, win))
        halo(ctx, 750 + shift, gy - 100, 240, a=0.18 * win)
        rj = figure(ctx, 750 + shift - jit, gy, 54, mix(PULL, STAND, ease((t - 4.4) / 0.6)), d=-1)
        a, b = lj["hand_f"], rj["hand_f"]
        if win < 0.95 or t < 4.4:
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 10
            ctx.set_source_rgba(0.85, 0.8, 0.7, 1); ctx.set_line_width(6)
            ctx.move_to(*a); ctx.curve_to(mx, my, mx, my, *b); ctx.stroke()
            ctx.set_source_rgba(*accent(), 1)
            polyline(ctx, [(mx - 12, my - 4), (mx + 12, my - 4), (mx, my + 30)], close=True); ctx.fill()
        _sub(ctx, left, 330 + shift, gy + 60, ease(t / 0.4) * lerp(1, 0.5, win))
        _sub(ctx, right, 750 + shift, gy + 60, ease(t / 0.4), col=(1, 1, 1))
    return Scene(draw, duration, "tug_of_war", _cap(line1, line2))


def marionette(line1, line2="", control="Their opinions", duration=6.4, t2=2.8, cut=2.8):
    """Figure dangles from puppet strings swayed by a control bar; the strings snap,
    the figure drops, then stands on its own and glows. Theme: living for others, control, freedom."""
    gy, by = 1360, 840

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        ctx.set_line_width(3); ctx.set_source_rgba(0.35, 0.35, 0.35, 1)
        ctx.move_to(200, gy); ctx.line_to(W - 200, gy); ctx.stroke()
        sway = 45 * math.sin(t * 1.7) * (1 - ease((t - cut) / 0.4))
        bar_a = 1 - ease((t - cut - 0.2) / 0.6)
        bar_y = by - 60 * ease((t - cut) / 0.8)
        bx = CX + sway
        x = CX + sway * 0.55
        if t < cut:
            pose, lift = DANGLE, 14 + 6 * math.sin(t * 3.4)
        else:
            u = t - cut
            lift = 14 * (1 - ease(u / 0.25))
            pose = mix(mix(DANGLE, SLUMP, ease(u / 0.3)), STAND, eio((u - 0.7) / 0.8))
        halo(ctx, x, gy - 110, 250, a=0.2 * ease((t - cut - 1.0) / 0.8))
        j = figure(ctx, x, gy, 56, pose, bob=lift)
        if bar_a > 0:
            ctx.set_source_rgba(0.85, 0.85, 0.85, bar_a); ctx.set_line_width(9)
            ctx.move_to(bx - 130, bar_y); ctx.line_to(bx + 130, bar_y); ctx.stroke()
            ctx.move_to(bx, bar_y - 45); ctx.line_to(bx, bar_y + 45); ctx.stroke()
            _sub(ctx, control, bx, bar_y - 70, bar_a * ease(t / 0.4))
            ends = [((bx - 130, bar_y), j["hand_b"]), ((bx + 130, bar_y), j["hand_f"]),
                    ((bx, bar_y + 45), (j["head"][0], j["head"][1] - j["r"]))]
            retract = ease((t - cut) / 0.35)
            ctx.set_line_width(1.6)
            for top, low in ends:
                end = (lerp(low[0], top[0], retract), lerp(low[1], top[1], retract))
                ctx.set_source_rgba(0.75, 0.75, 0.75, bar_a)
                ctx.move_to(*top); ctx.line_to(*end); ctx.stroke()
    return Scene(draw, duration, "marionette", _cap(line1, line2))


# ---------------------------------------------------------------- growth / transformation
def _butterfly(ctx, x, y, size, flap, a=1.0):
    f = 0.2 + 0.8 * abs(math.cos(flap))
    col = accent()
    for side in (-1, 1):
        for (ox, oy, rx, ry, al) in ((0.55, -0.32, 0.62, 0.48, 0.95), (0.42, 0.34, 0.44, 0.34, 0.7)):
            ctx.new_path(); ctx.save()
            ctx.translate(x + side * ox * size * f, y + oy * size); ctx.scale(rx * size * f, ry * size)
            ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
            ctx.set_source_rgba(*col, al * a); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, a); ctx.set_line_width(size * 0.12)
    ctx.move_to(x, y - size * 0.55); ctx.line_to(x, y + size * 0.6); ctx.stroke()


def cocoon(line1, line2="", duration=6.6, t2=3.0, burst=2.7):
    """A cocoon hangs from a branch, shakes, bursts with light, and an accent-coloured
    butterfly flutters out and away. Theme: transformation, the struggle is the process."""
    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        ctx.set_source_rgba(0.55, 0.55, 0.55, 1); ctx.set_line_width(10)
        ctx.move_to(170, 850); ctx.curve_to(400, 830, 600, 880, 900, 860); ctx.stroke()
        ctx.set_line_width(5)
        ctx.move_to(330, 842); ctx.line_to(290, 790); ctx.move_to(720, 868); ctx.line_to(770, 820)
        ctx.stroke()
        top = (560, 866)
        shake = 0.13 * math.sin(t * 38) * ease((t - 1.3) / 0.4) if t < burst else 0
        swing = 0.05 * math.sin(t * 1.4) + shake
        open_ = ease((t - burst) / 0.5)
        ctx.save(); ctx.translate(*top); ctx.rotate(swing)
        ctx.set_source_rgba(0.6, 0.6, 0.6, 1); ctx.set_line_width(2)
        ctx.move_to(0, 0); ctx.line_to(0, 40); ctx.stroke()
        for side in ((-1, 1) if open_ > 0 else (0,)):  # whole cocoon, or two halves splitting
            ctx.save()
            ctx.translate(side * 30 * open_, 150 + 10 * open_); ctx.rotate(side * 0.35 * open_)
            if side:
                ctx.rectangle(0 if side > 0 else -60, -120, 60, 240); ctx.clip()
            ctx.new_path(); ctx.save(); ctx.scale(46, 108); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
            ctx.set_source(vgrad(-108, 108, (0.32, 0.30, 0.27, 1), (0.10, 0.10, 0.09, 1)))
            ctx.fill_preserve()
            ctx.set_source_rgba(0.7, 0.68, 0.62, 1); ctx.set_line_width(3); ctx.stroke()
            ctx.restore()
        ctx.restore()
        if t >= burst:
            u = t - burst
            halo(ctx, 560, 1020, 300, col=accent(), a=0.35 * (1 - ease(u / 0.9)) + 0.06)
            fl = eio((u - 0.4) / (duration - burst - 1.2))
            bx = lerp(560, 820, fl) + 40 * math.sin(fl * 7)
            byy = lerp(1020, 780, fl) - 60 * math.sin(fl * 3.1)
            for k in range(1, 9):
                p = clamp(fl - k * 0.025)
                ctx.arc(lerp(560, 820, p) + 40 * math.sin(p * 7), lerp(1020, 780, p) - 60 * math.sin(p * 3.1),
                        3, 0, 2 * math.pi)
                ctx.set_source_rgba(*accent(), 0.5 * (1 - k / 9) * ease(u / 0.6)); ctx.fill()
            _butterfly(ctx, bx, byy, 70 * ease(u / 0.5), u * 13)
    return Scene(draw, duration, "cocoon", _cap(line1, line2))


def roots(line1, line2="", seen="what people see", hidden="what you build", duration=6.4, t2=2.8):
    """Cut-away of the ground: a huge root system grows underground first, then a tiny
    accent sprout appears on top. Theme: invisible progress, patience, foundations."""
    gy = 1080

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        ctx.set_line_width(3); ctx.set_source_rgba(0.6, 0.6, 0.6, 1)
        ctx.move_to(140, gy); ctx.line_to(940, gy); ctx.stroke()
        label(ctx, seen, 160, gy - 20, 0.6 * ease(t / 0.4), size=22, align="left")
        label(ctx, hidden, 160, gy + 40, 0.6 * ease(t / 0.4), size=22, align="left")
        g = eio((t - 0.3) / 3.2)

        def branch(x, y, ang, length, depth):
            if depth == 0 or g <= 0:
                return
            L = length * g
            x2, y2 = x + L * math.sin(ang), y + L * math.cos(ang)
            ctx.set_line_width(1.5 + depth * 1.6)
            ctx.set_source_rgba(1, 1, 1, 0.25 + 0.15 * depth)
            ctx.move_to(x, y); ctx.line_to(x2, y2); ctx.stroke()
            for da in (-0.45, 0.4):
                branch(x2, y2, ang + da, length * 0.68, depth - 1)
        branch(600, gy, 0.0, 170, 5)
        s = eio((t - 3.4) / 1.4)
        if s > 0:
            ctx.set_line_width(5); ctx.set_source_rgba(*accent(), 1)
            ctx.move_to(600, gy); ctx.line_to(600, gy - 90 * s); ctx.stroke()
            ctx.arc(600 + 22 * s, gy - 85 * s, 16 * s, 0, 2 * math.pi); ctx.fill()
        figure(ctx, 400, gy, 58, STAND)
    return Scene(draw, duration, "roots", _cap(line1, line2))


# ---------------------------------------------------------------- data-ish / text-led
def habit_grid(line1, line2="", days=30, cols=5, counter="Day", duration=6.4, t2=2.8):
    """Calendar grid of days filling one by one, slowly then faster; the last day lights up
    in the accent colour with a counter below. Theme: streaks, consistency, don't break the chain."""
    rows = math.ceil(days / cols)
    cell, gap = 92, 18
    gw, gh = cols * cell + (cols - 1) * gap, rows * cell + (rows - 1) * gap
    x0, y0 = CX - gw / 2, 1150 - gh / 2
    times = [0.6 + 4.0 * math.sqrt((k + 1) / days) for k in range(days)]

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        filled = 0
        for k in range(days):
            r, c = divmod(k, cols)
            x, y = x0 + c * (cell + gap), y0 + r * (cell + gap)
            rounded_rect(ctx, x, y, cell, cell, 14)
            ctx.set_source_rgba(0.35, 0.35, 0.35, 1); ctx.set_line_width(2); ctx.stroke()
            u = clamp((t - times[k]) / 0.16)
            if u > 0:
                filled = k + 1
                sc = 0.6 + 0.4 * eio(u)
                last = k == days - 1
                pulse = 0.85 + 0.15 * math.cos((t - times[k]) * 5) if last else 1
                rounded_rect(ctx, x + cell * (1 - sc) / 2, y + cell * (1 - sc) / 2, cell * sc, cell * sc, 14 * sc)
                ctx.set_source_rgba(*(accent() if last else (1, 1, 1)), u * pulse); ctx.fill()
        done = filled == days
        label(ctx, f"{counter} {max(filled, 1)}", CX, y0 + gh + 70, ease(t / 0.4), size=34,
              col=accent() if done else (1, 1, 1))
    return Scene(draw, duration, "habit_grid", _cap(line1, line2))


def checklist(items, line1="", line2="", duration=6.4, t2=2.6):
    """Kinetic to-do list: up to 5 items appear and get ticked one by one, the last in the
    accent colour. No figure — a calm text-led breather between busy scenes.
    Theme: routines, morning habits, the steps of a plan."""
    items = list(items)[:5]
    n = len(items)
    step = min(0.9, (duration - 2.2) / max(n, 1))

    def tick(ctx, x, y, p, col):
        pts = [(x + 12, y + 30), (x + 25, y + 43), (x + 46, y + 13)]
        segs = [math.dist(pts[0], pts[1]), math.dist(pts[1], pts[2])]
        L = p * sum(segs)
        ctx.set_line_width(7); ctx.set_source_rgba(*col, 1)
        ctx.move_to(*pts[0])
        if L <= segs[0]:
            k = L / segs[0]; ctx.line_to(lerp(pts[0][0], pts[1][0], k), lerp(pts[0][1], pts[1][1], k))
        else:
            k = (L - segs[0]) / segs[1]
            ctx.line_to(*pts[1]); ctx.line_to(lerp(pts[1][0], pts[2][0], k), lerp(pts[1][1], pts[2][1], k))
        ctx.stroke()

    def draw(ctx, t):
        if line1:
            caption(ctx, t, line1, line2, t2)
        y_start = 1140 - (n - 1) * 60
        for i, item in enumerate(items):
            ti = 0.5 + i * step
            a = ease((t - ti) / 0.35)
            if a <= 0:
                continue
            y = y_start + i * 120
            x = 250
            col = accent() if i == n - 1 else (1, 1, 1)
            rounded_rect(ctx, x, y - 42, 56, 56, 12)
            ctx.set_source_rgba(0.8, 0.8, 0.8, a); ctx.set_line_width(3); ctx.stroke()
            done = eio((t - ti - 0.35) / 0.3)
            if done > 0:
                tick(ctx, x + 2, y - 44, done, col)
            label(ctx, item, x + 90, y, a * (1 - 0.35 * done * (i < n - 1)), size=40, col=col, align="left")
    return Scene(draw, duration, "checklist", " / ".join(items))


# ---------------------------------------------------------------- camera moves
def mountain_reveal(line1, line2="", small="Small win", duration=6.6, t2=3.0):
    """Close-up of a figure planting a flag on a little hill, then the camera pulls back to
    reveal a giant mountain behind with an accent flag at the summit.
    Theme: celebrate small wins but keep climbing; bigger goals; perspective."""
    fx, fy = 470, 1312
    mtn = [(-150, 1420), (170, 1180), (320, 1230), (520, 960), (600, 1010), (780, 740), (900, 900),
           (1010, 850), (1250, 1420)]
    hill = [(250, 1420), (360, 1340), (470, fy), (580, 1340), (700, 1420)]

    def draw(ctx, t):
        z = math.exp(lerp(math.log(2.7), 0.0, eio((t - 2.0) / 2.3)))
        ctx.save(); camera(ctx, z, fx, fy - 60)
        m_a = ease((t - 2.0) / 1.4)
        polyline(ctx, mtn, close=True)
        ctx.set_source(vgrad(740, 1420, (0.17, 0.17, 0.18, m_a), (0.02, 0.02, 0.02, m_a))); ctx.fill()
        polyline(ctx, mtn)
        ctx.set_source_rgba(0.5, 0.5, 0.5, m_a); ctx.set_line_width(3); ctx.stroke()
        polyline(ctx, [(745, 790), (780, 740), (815, 785), (795, 778), (780, 795), (765, 780)], close=True)
        ctx.set_source_rgba(0.9, 0.9, 0.9, m_a); ctx.fill()
        fa = ease((t - 4.3) / 0.5)
        if fa > 0:
            ctx.set_source_rgba(1, 1, 1, fa); ctx.set_line_width(4)
            ctx.move_to(780, 740); ctx.line_to(780, 670); ctx.stroke()
            polyline(ctx, [(780, 670), (830, 684), (780, 698)], close=True)
            ctx.set_source_rgba(*accent(), fa); ctx.fill()
            halo(ctx, 790, 690, 120, col=accent(), a=0.25 * fa)
        polyline(ctx, hill, close=True)
        ctx.set_source(vgrad(fy, 1420, (0.3, 0.3, 0.3, 1), (0.05, 0.05, 0.05, 1))); ctx.fill()
        plant = eio((t - 0.4) / 0.8)
        ctx.set_source_rgba(1, 1, 1, 1); ctx.set_line_width(3)
        pole_x = fx + 34
        ctx.move_to(pole_x, fy - 60 * (1 - plant)); ctx.line_to(pole_x, fy - 60 * (1 - plant) - 70); ctx.stroke()
        top = fy - 60 * (1 - plant) - 70
        polyline(ctx, [(pole_x, top), (pole_x + 32, top + 10), (pole_x, top + 20)], close=True); ctx.fill()
        figure(ctx, fx, fy, 24, mix(STAND, ARMS_UP, ease((t - 1.2) / 0.5)))
        label(ctx, small, fx, fy - 112, ease((t - 0.8) / 0.4) * (1 - m_a * 0.6), size=14, col=(1, 1, 1))
        ctx.restore()
        caption(ctx, t, line1, line2, t2)
    return Scene(draw, duration, "mountain_reveal", _cap(line1, line2))


def planet_zoom(line1, line2="", problem="Your problem", duration=6.6, t2=3.0):
    """A figure stands on a tiny planet under a storm cloud; the camera zooms out until the
    planet is a speck among stars ('you are here'). Theme: perspective, problems feel huge."""
    C, R = (540, 1180), 170
    rng = random.Random(11)
    stars = [(C[0] + rng.uniform(-40000, 40000), C[1] + rng.uniform(-40000, 40000), rng.uniform(0.3, 1))
             for _ in range(2600)]
    stars += [(C[0] + rng.uniform(-700, 700), C[1] + rng.uniform(-900, 600), rng.uniform(0.2, 0.6))
              for _ in range(30)]

    def draw(ctx, t):
        z = math.exp(lerp(0.0, math.log(0.03), eio((t - 2.1) / 2.6)))
        for sx, sy, b in stars:
            px, py = C[0] + (sx - C[0]) * z, C[1] + (sy - C[1]) * z
            edge = ease((py - 700) / 120) * ease((1660 - py) / 120)  # soft top/bottom edges
            if 0 < px < W and edge > 0 and math.hypot(px - C[0], py - C[1]) > R * z + 6:
                ctx.arc(px, py, 1.2 + 1.3 * b, 0, 2 * math.pi)
                ctx.set_source_rgba(1, 1, 1, (0.25 + 0.6 * b) * edge); ctx.fill()
        ctx.save(); camera(ctx, z, *C)
        rg = cairo.RadialGradient(C[0] - 60, C[1] - 60, 10, C[0], C[1], R)
        rg.add_color_stop_rgba(0, 0.3, 0.3, 0.32, 1); rg.add_color_stop_rgba(1, 0.06, 0.06, 0.07, 1)
        ctx.arc(*C, R, 0, 2 * math.pi); ctx.set_source(rg); ctx.fill_preserve()
        ctx.set_source_rgba(0.6, 0.6, 0.6, 1); ctx.set_line_width(max(3, 1.5 / z)); ctx.stroke()
        figure(ctx, C[0], C[1] - R + 2, 30, SLUMP)
        cy = C[1] - R - 175
        for ox, oy, r in ((-60, 10, 40), (-15, -12, 52), (40, 0, 44), (78, 14, 30)):
            ctx.arc(C[0] + ox, cy + oy, r, 0, 2 * math.pi)
            ctx.set_source_rgba(0.28, 0.28, 0.3, 1); ctx.fill()
        ctx.set_line_width(2.5); ctx.set_source_rgba(0.6, 0.6, 0.65, 0.8)
        for k in range(6):
            rx = C[0] - 70 + k * 28
            ph = (t * 2.2 + k * 0.37) % 1
            ctx.move_to(rx, cy + 40 + ph * 50); ctx.line_to(rx - 6, cy + 60 + ph * 50); ctx.stroke()
        label(ctx, problem, C[0], cy + 9, ease(t / 0.4), size=20, col=(1, 1, 1))
        ctx.restore()
        here = ease((t - 4.6) / 0.5)
        if here > 0:
            ctx.arc(*C, 9, 0, 2 * math.pi); ctx.set_source_rgba(*accent(), here); ctx.set_line_width(2.5)
            ctx.stroke()
            ctx.move_to(C[0] + 12, C[1] - 12); ctx.line_to(C[0] + 70, C[1] - 70); ctx.stroke()
            label(ctx, "you are here", C[0] + 80, C[1] - 78, here, size=26, col=accent(), align="left")
        caption(ctx, t, line1, line2, t2)
    return Scene(draw, duration, "planet_zoom", _cap(line1, line2))


# ---------------------------------------------------------------- action
def jump_gap(line1, line2="", gap_label="Fear", duration=6.4, t2=2.9):
    """Figure runs to a cliff edge and leaps a chasm in slow motion, landing on the far side.
    Theme: leap of faith, take the risk, courage."""
    gy, e1, e2 = 1300, 390, 690

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        for pts in ([(0, gy), (e1, gy), (e1 - 25, gy + 90), (e1 + 5, gy + 180), (e1 - 30, 1640), (0, 1640)],
                    [(W, gy), (e2, gy), (e2 + 20, gy + 110), (e2 - 10, gy + 220), (e2 + 25, 1640), (W, 1640)]):
            polyline(ctx, pts, close=True)
            ctx.set_source(vgrad(gy, 1640, (0.16, 0.16, 0.16, 1), (0, 0, 0, 1))); ctx.fill()
            polyline(ctx, pts[:3]); ctx.set_source_rgba(0.7, 0.7, 0.7, 1); ctx.set_line_width(4); ctx.stroke()
        _sub(ctx, gap_label, CX, 1520, ease((t - 0.6) / 0.5) * 0.8, col=(0.5, 0.5, 0.5))
        if t < 0.5:
            x, pose, bob = 120, STAND, 0
        elif t < 1.9:
            u = (t - 0.5) / 1.4
            x = lerp(120, e1 - 20, u * u * (2 - u) * 0.9 + 0.1 * u)
            pose, bob = run((x - 120) / 30), 0
        elif t < 3.3:
            u = (t - 1.9) / 1.4
            s = u + 0.12 * math.sin(2 * math.pi * u)
            x = lerp(e1 - 20, e2 + 60, s)
            bob = 170 * 4 * s * (1 - s)
            pose = mix(CROUCH, LEAP, ease(u / 0.15)) if u < 0.5 else mix(LEAP, CROUCH, ease((u - 0.85) / 0.15))
        else:
            x, bob = e2 + 60, 0
            pose = mix(CROUCH, STAND, eio((t - 3.3) / 0.5))
        halo(ctx, x, gy - 100 - bob, 240, a=0.18 * ease((t - 3.4) / 0.6))
        figure(ctx, x, gy, 50, pose, bob=bob)
    return Scene(draw, duration, "jump_gap", _cap(line1, line2))


def candle(line1, line2="", label_text="Your time", duration=6.6, t2=3.0, look_up=3.4):
    """A candle burns down fast while a figure sits hunched over a glowing phone; the phone
    goes dark and the figure stands to face the candle. Theme: time is running, wake up."""
    gy, cx = 1330, 330

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        ctx.set_line_width(3); ctx.set_source_rgba(0.35, 0.35, 0.35, 1)
        ctx.move_to(150, gy); ctx.line_to(W - 150, gy); ctx.stroke()
        h = lerp(380, 70, clamp(t / duration))
        ellipse(ctx, cx, gy - 4, 70, 12); ctx.set_source_rgba(0.75, 0.72, 0.65, 0.8); ctx.fill()
        ctx.rectangle(cx - 36, gy - h, 72, h)
        g = cairo.LinearGradient(cx - 36, 0, cx + 36, 0)
        g.add_color_stop_rgba(0, 0.55, 0.53, 0.5, 1); g.add_color_stop_rgba(0.4, 0.95, 0.93, 0.88, 1)
        g.add_color_stop_rgba(1, 0.5, 0.48, 0.45, 1)
        ctx.set_source(g); ctx.fill()
        for dx, dl in ((-22, 40), (14, 70), (26, 28)):
            ctx.rectangle(cx + dx, gy - h, 8, dl); ctx.arc(cx + dx + 4, gy - h + dl, 4, 0, math.pi)
            ctx.set_source_rgba(0.95, 0.93, 0.88, 1); ctx.fill()
        ctx.set_source_rgba(0.3, 0.3, 0.3, 1); ctx.set_line_width(3)
        ctx.move_to(cx, gy - h); ctx.line_to(cx, gy - h - 16); ctx.stroke()
        fl = 1 + 0.12 * math.sin(t * 17) + 0.08 * math.sin(t * 29)
        fy = gy - h - 16
        warm = (1.0, 0.82, 0.5)
        halo(ctx, cx, fy - 25, 230, col=warm, a=0.25)
        ctx.move_to(cx, fy - 62 * fl)
        ctx.curve_to(cx + 24, fy - 30, cx + 18, fy + 2, cx, fy + 2)
        ctx.curve_to(cx - 18, fy + 2, cx - 24, fy - 30, cx, fy - 62 * fl)
        ctx.set_source_rgba(*warm, 1); ctx.fill()
        _sub(ctx, label_text, cx, gy + 55, ease(t / 0.4))
        up = eio((t - look_up) / 0.9)
        d = 1 if up < 0.5 else -1
        j = figure(ctx, 720, gy, 52, mix(PHONE, STAND, up), d=d)
        ph = 1 - ease((t - look_up + 0.3) / 0.3)
        if ph > 0:
            hx, hy = j["hand_f"]
            halo(ctx, hx, hy, 90, col=(0.7, 0.85, 1.0), a=0.35 * ph)
            rounded_rect(ctx, hx - 4, hy - 30, 22, 38, 5)
            ctx.set_source_rgba(0.8, 0.9, 1.0, ph); ctx.fill()
    return Scene(draw, duration, "candle", _cap(line1, line2))


def scale_balance(line1, line2="", light=("Likes", "Comfort", "Excuses"), heavy="Peace",
                  duration=6.4, t2=2.9):
    """Balance scale: several small labelled boxes drop on the left and tip it; then one
    accent block drops on the right and outweighs them all with a damped wobble.
    Theme: priorities, what really matters, quality over quantity."""
    px, py, arm, hang = CX, 930, 270, 200
    light = list(light)[:3]
    drops = [0.6 + i * 0.45 for i in range(len(light))]
    heavy_t = 2.7

    def theta(t):
        th = 0.0
        for k, td in enumerate(drops):
            if t >= td + 0.3:
                th = -0.07 * (k + 1)
        if t >= heavy_t + 0.3:
            u = t - heavy_t - 0.3
            return 0.30 + (th - 0.30) * math.exp(-3 * u) * math.cos(9 * u)
        return th

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        th = theta(t)
        ctx.set_source_rgba(0.7, 0.7, 0.7, 1); ctx.set_line_width(8)
        ctx.move_to(px, py); ctx.line_to(px, 1360); ctx.stroke()
        polyline(ctx, [(px - 90, 1370), (px + 90, 1370), (px, 1320)], close=True); ctx.fill()
        ends = []
        for side in (-1, 1):
            ends.append((px + side * arm * math.cos(th), py + side * arm * math.sin(th)))
        ctx.set_source_rgba(0.9, 0.9, 0.9, 1); ctx.set_line_width(9)
        ctx.move_to(*ends[0]); ctx.line_to(*ends[1]); ctx.stroke()
        ctx.arc(px, py, 14, 0, 2 * math.pi); ctx.fill()
        pans = []
        for ex, ey in ends:
            pan_y = ey + hang
            ctx.set_line_width(2); ctx.set_source_rgba(0.6, 0.6, 0.6, 1)
            ctx.move_to(ex, ey); ctx.line_to(ex - 85, pan_y); ctx.move_to(ex, ey); ctx.line_to(ex + 85, pan_y)
            ctx.stroke()
            ctx.set_line_width(5); ctx.set_source_rgba(0.85, 0.85, 0.85, 1)
            ctx.move_to(ex - 95, pan_y); ctx.curve_to(ex - 60, pan_y + 26, ex + 60, pan_y + 26, ex + 95, pan_y)
            ctx.stroke()
            pans.append((ex, pan_y))
        lx, ly = pans[0]
        for k, (txt, td) in enumerate(zip(light, drops)):
            u = eio((t - td) / 0.3)
            if u <= 0:
                continue
            by = lerp(ly - 400, ly - 6 - k * 44, u)
            rounded_rect(ctx, lx - 75, by - 40, 150, 40, 6)
            ctx.set_source_rgba(0.2, 0.2, 0.2, 1); ctx.fill_preserve()
            ctx.set_source_rgba(0.7, 0.7, 0.7, 1); ctx.set_line_width(2); ctx.stroke()
            label(ctx, txt, lx, by - 12, 1, size=22, col=(0.85, 0.85, 0.85))
        u = eio((t - heavy_t) / 0.3)
        if u > 0:
            rx, ry = pans[1]
            by = lerp(ry - 500, ry - 6, u)
            rounded_rect(ctx, rx - 70, by - 110, 140, 110, 10)
            ctx.set_source_rgba(*accent(), 1); ctx.fill()
            label(ctx, heavy, rx, by - 45, 1, size=28, col=(0.05, 0.05, 0.05), bold=True)
            halo(ctx, rx, by - 55, 200, col=accent(), a=0.15 * ease((t - heavy_t - 0.3) / 0.5))
    return Scene(draw, duration, "scale_balance", _cap(line1, line2))


def maze(line1, line2="", duration=6.6, t2=3.0, cols=7, rows=8, seed=4):
    """Top-down maze: a glowing dot explores, hits dead ends, backtracks, and finally reaches
    the accent exit; the true path lights up. Theme: wrong turns teach, failure, finding your way."""
    rng = random.Random(seed)
    walls = {(c, r): {"N", "S", "E", "W"} for c in range(cols) for r in range(rows)}
    moves = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
    opp = {"N": "S", "S": "N", "E": "W", "W": "E"}
    seen, stack = {(0, 0)}, [(0, 0)]
    while stack:
        c = stack[-1]
        nb = [(d, (c[0] + dx, c[1] + dy)) for d, (dx, dy) in moves.items()
              if (c[0] + dx, c[1] + dy) in walls and (c[0] + dx, c[1] + dy) not in seen]
        if not nb:
            stack.pop(); continue
        d, n = rng.choice(nb)
        walls[c].discard(d); walls[n].discard(opp[d])
        seen.add(n); stack.append(n)
    goal = (cols - 1, rows - 1)
    seq, vis = [], set()
    rng2 = random.Random(seed + 7)

    def explore(c):
        seq.append(c); vis.add(c)
        if c == goal:
            return True
        ds = [d for d in moves if d not in walls[c]]
        rng2.shuffle(ds)
        for d in ds:
            n = (c[0] + moves[d][0], c[1] + moves[d][1])
            if n not in vis and explore(n):
                return True
            if n in vis and seq[-1] != c:
                seq.append(c)
        return False
    explore((0, 0))
    stacks, st = [], []
    for c in seq:
        if len(st) >= 2 and st[-2] == c:
            st.pop()
        elif not st or st[-1] != c:
            st.append(c)
        stacks.append(list(st))
    cell = 88
    x0, y0 = CX - cols * cell / 2, 1180 - rows * cell / 2
    ctr = lambda c: (x0 + (c[0] + 0.5) * cell, y0 + (c[1] + 0.5) * cell)
    t_start, t_end = 0.6, duration - 1.3

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2)
        ctx.set_line_width(4); ctx.set_source_rgba(0.42, 0.42, 0.42, 1)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for (c, r), ws_ in walls.items():
            x, y = x0 + c * cell, y0 + r * cell
            if "N" in ws_ and not (c == 0 and r == 0):
                ctx.move_to(x, y); ctx.line_to(x + cell, y)
            if "W" in ws_:
                ctx.move_to(x, y); ctx.line_to(x, y + cell)
            if "S" in ws_ and (c, r) != goal:
                ctx.move_to(x, y + cell); ctx.line_to(x + cell, y + cell)
            if "E" in ws_:
                ctx.move_to(x + cell, y); ctx.line_to(x + cell, y + cell)
        ctx.stroke()
        gx, gy_ = ctr(goal)
        ctx.arc(gx, gy_, 16, 0, 2 * math.pi); ctx.set_source_rgba(*accent(), 0.9); ctx.fill()
        p = clamp((t - t_start) / (t_end - t_start)) * (len(seq) - 1)
        i = int(p); f = p - i
        visited = seq[:i + 1]
        ctx.set_line_width(10); ctx.set_source_rgba(1, 1, 1, 0.16)
        for a_, b_ in zip(visited, visited[1:]):
            ctx.move_to(*ctr(a_)); ctx.line_to(*ctr(b_))
        ctx.stroke()
        done = i >= len(seq) - 1
        path = stacks[min(i, len(stacks) - 1)]
        col = accent() if done else (1, 1, 1)
        ctx.set_line_width(8); ctx.set_source_rgba(*col, 0.95)
        ctx.move_to(*ctr(path[0]))
        for c in path[1:]:
            ctx.line_to(*ctr(c))
        a = ctr(seq[i]); b = ctr(seq[min(i + 1, len(seq) - 1)])
        pos = (lerp(a[0], b[0], f), lerp(a[1], b[1], f))
        ctx.line_to(*pos); ctx.stroke()
        halo(ctx, *pos, 70, col=col, a=0.35)
        ctx.arc(*pos, 13, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    return Scene(draw, duration, "maze", _cap(line1, line2))


EXTRA_TEMPLATES = {
    "domino": domino, "chain_break": chain_break, "mirror": mirror, "tug_of_war": tug_of_war,
    "marionette": marionette, "cocoon": cocoon, "roots": roots, "habit_grid": habit_grid,
    "checklist": checklist, "mountain_reveal": mountain_reveal, "planet_zoom": planet_zoom,
    "jump_gap": jump_gap, "candle": candle, "scale_balance": scale_balance, "maze": maze,
}
