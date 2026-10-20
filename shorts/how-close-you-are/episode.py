"""YOU CAN'T ALWAYS SEE HOW CLOSE YOU ARE — 35 s, music only, story told in captions.

Hook: frame 0 is a tight close-up of him running on shaking legs; at 0.75 s his knees slam into the
road (thud, shake, flash, dust) and the camera snaps back to an empty road vanishing into the dark.
Darkness on the right edge is what he can't see; it lifts in the crane shot and at the crest.

  python3 <skill>/scripts/engine.py episode.py --preview sheet.png
  python3 <skill>/scripts/engine.py episode.py --out short.mp4 --music music.wav
"""
import math
import random

import cairo
from engine import (GOLD, SIT, STAND, Scene, accent, caption, clamp, ease, eio, halo, label, lerp,
                    mix, run, walk, words)

G = 1400
S = 62
XK = 712                       # where his knees hit the road
XS = XK + 150                  # where he sits down
HC, HW, HH = XS + 520, 440, 110  # hill crest, half-width, height
XF = HC + 240                  # the finish line, just beyond the crest

FALL = dict(lean=0.95, th_f=0.85, sh_f=-0.25, th_b=-0.35, sh_b=-0.95,
            ua_f=1.55, fa_f=1.25, ua_b=1.25, fa_b=1.0, hip=0.33)
HANDS_DOWN = dict(lean=0.95, th_f=0.15, sh_f=-1.45, th_b=0.05, sh_b=-1.50,
                  ua_f=0.25, fa_f=-0.05, ua_b=0.20, fa_b=-0.10, hip=0.61)
KNEEL_UP = dict(lean=0.12, th_f=0.05, sh_f=-1.50, th_b=-0.02, sh_b=-1.55,
                ua_f=0.15, fa_f=0.25, ua_b=0.05, fa_b=0.15, hip=0.61)
ONE_KNEE = dict(lean=0.55, th_f=1.35, sh_f=-0.10, th_b=0.05, sh_b=-1.50,
                ua_f=0.70, fa_f=0.40, ua_b=0.50, fa_b=0.30, hip=0.61)
SIT_UP = dict(SIT, lean=0.12)
SIT_DOWN = dict(SIT, lean=0.85, ua_f=0.75, fa_f=0.45, ua_b=0.65, fa_b=0.35)
LOOK_HANDS = dict(SIT, lean=0.40, ua_f=1.00, fa_f=2.30, ua_b=0.90, fa_b=2.20)
TIRED = dict(STAND, lean=0.14)


def pose_with(p, **kw):
    q = dict(p); q.update(kw)
    return q


def road_y(x):
    if abs(x - HC) < HW:
        return G - HH * (0.5 + 0.5 * math.cos(math.pi * (x - HC) / HW))
    return G


def struggle_run(ph):
    return pose_with(mix(walk(ph, 0.5), run(ph), 0.55), lean=0.30)


# ---------- drawing ----------
def fig(ctx, x, ground, s, pose, col=(1, 1, 1), a=1.0, d=1, knee_shake=0.0, face=None, hand_shake=0.0):
    """engine.figure plus trembling knees / hands and an optional side-view face for close-ups."""
    T, L1, L2, A1, A2 = s, 0.56 * s, 0.56 * s, 0.46 * s, 0.44 * s
    r = 0.30 * s
    hy = ground - lerp(L1 + L2, 0.20 * s, pose["hip"])

    def seg(p, ang, L):
        return (p[0] + d * L * math.sin(ang), p[1] + L * math.cos(ang))

    ln = pose["lean"]
    ux, uy = d * math.sin(ln), -math.cos(ln)
    hip = (x, hy)
    neck = (x + ux * T, hy + uy * T)
    sh = (x + ux * T * 0.86, hy + uy * T * 0.86)
    head = (x + ux * (T + 0.14 * s + r), hy + uy * (T + 0.14 * s + r))
    ctx.new_path()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(0.22 * s)

    def limb(p0, a1, l1, a2, l2, shade, jx=0.0, jy=0.0):
        p1 = seg(p0, a1, l1); p1 = (p1[0] + jx, p1[1])
        p2 = seg(p1, a2, l2); p2 = (p2[0] + jx * 0.5, p2[1] + jy)
        ctx.set_source_rgba(*(c * shade for c in col), a)
        ctx.move_to(*p0); ctx.line_to(*p1); ctx.line_to(*p2); ctx.stroke()
        return p2

    hand_b = limb(sh, pose["ua_b"], A1, pose["fa_b"], A2, 0.5, hand_shake * 0.7, -hand_shake)
    limb(hip, pose["th_b"], L1, pose["sh_b"], L2, 0.5, -knee_shake)
    ctx.set_source_rgba(*col, a); ctx.move_to(*hip); ctx.line_to(*neck); ctx.stroke()
    limb(hip, pose["th_f"], L1, pose["sh_f"], L2, 1.0, knee_shake)
    hand_f = limb(sh, pose["ua_f"], A1, pose["fa_f"], A2, 1.0, -hand_shake, hand_shake * 0.8)
    ctx.set_source_rgba(*col, a); ctx.arc(*head, r, 0, 2 * math.pi); ctx.fill()
    if face:
        ex, ey = head[0] + d * 0.42 * r, head[1] - 0.12 * r
        ctx.set_source_rgba(0, 0, 0, a); ctx.set_line_width(0.12 * r); ctx.new_path()
        if face == "strain":
            ctx.move_to(ex - d * 0.16 * r, ey - 0.14 * r); ctx.line_to(ex + d * 0.06 * r, ey)
            ctx.line_to(ex - d * 0.16 * r, ey + 0.14 * r); ctx.stroke()
            ctx.arc(head[0] + d * 0.55 * r, head[1] + 0.42 * r, 0.12 * r, 0, 2 * math.pi); ctx.fill()
        elif face == "closed":
            ctx.arc(ex, ey - 0.05 * r, 0.15 * r, 0.15 * math.pi, 0.85 * math.pi); ctx.stroke()
        elif face == "open":
            ctx.arc(ex, ey, 0.09 * r, 0, 2 * math.pi); ctx.fill()
        elif face == "wide":
            ctx.arc(ex, ey, 0.14 * r, 0, 2 * math.pi); ctx.fill()
            ctx.arc(head[0] + d * 0.55 * r, head[1] + 0.45 * r, 0.10 * r, 0, 2 * math.pi); ctx.stroke()
    return dict(head=head, hand_f=hand_f, hand_b=hand_b, r=r, hip=hip)


_rng = random.Random(4)
STARS = [(_rng.uniform(-600, 3400), _rng.uniform(250, 1180), _rng.uniform(1.2, 3.0), _rng.uniform(0, 6))
         for _ in range(140)]
CONFETTI = [(_rng.uniform(-150, 150), _rng.uniform(0, 1), _rng.uniform(0.6, 1.4), _rng.random() < 0.6)
            for _ in range(46)]


def world(ctx, t, finish_glow=0.0, stars=0.5, finish_a=0.0):
    """finish_a: the finish line only exists for us once it is revealed (0 = hidden)."""
    for x, y, r, ph in STARS:
        a = stars * (0.35 + 0.35 * math.sin(t * 1.3 + ph))
        if a > 0.02:
            ctx.new_path(); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, a); ctx.fill()
    xs = range(-700, 3600, 16)
    ctx.new_path()
    for x in xs:
        ctx.line_to(x, road_y(x))
    for x in reversed(xs):
        ctx.line_to(x, road_y(x) + 40)
    ctx.close_path(); ctx.set_source_rgba(0.075, 0.075, 0.075, 1); ctx.fill()
    ctx.new_path()
    for x in xs:
        ctx.line_to(x, road_y(x))
    ctx.set_source_rgba(0.45, 0.45, 0.45, 1); ctx.set_line_width(3); ctx.stroke()
    ctx.set_source_rgba(0.28, 0.28, 0.28, 1); ctx.set_line_width(3)
    for x in range(-700, 3600, 80):
        ctx.move_to(x, road_y(x) + 20); ctx.line_to(x + 34, road_y(x + 34) + 20)
    ctx.stroke()
    if finish_a > 0:
        ctx.push_group(); finish(ctx, finish_glow); ctx.pop_group_to_source(); ctx.paint_with_alpha(finish_a)


def finish(ctx, glow):
    yf = road_y(XF)
    gold = accent()
    if glow > 0:
        halo(ctx, XF, yf - 150, 340, col=gold, a=0.30 * glow)
    col = tuple(lerp(0.45, c, 0.4 + 0.6 * glow) for c in gold)
    ctx.new_path(); ctx.set_line_width(7); ctx.set_source_rgba(*col, 1)
    for px in (XF - 95, XF + 95):
        ctx.move_to(px, road_y(px)); ctx.line_to(px, yf - 250)
    ctx.stroke()
    ctx.rectangle(XF - 112, yf - 268, 224, 48); ctx.set_source_rgba(0.12, 0.10, 0.06, 1); ctx.fill_preserve()
    ctx.set_source_rgba(*col, 1); ctx.set_line_width(3); ctx.stroke()
    label(ctx, "FINISH", XF, yf - 234, 1.0, size=28, col=col, bold=True)
    for k in range(19):  # chequered line across the road
        x = XF - 95 + k * 10
        ctx.rectangle(x, road_y(x) + 2 + (k % 2) * 8, 10, 8)
        ctx.set_source_rgba(*col, 0.9); ctx.fill()


def confetti(ctx, t, x0, y0):
    if t <= 0:
        return
    for dx, ph, sp, is_gold in CONFETTI:
        y = y0 - 260 + ((t * 140 * sp + ph * 300) % 420)
        x = x0 + dx * (1 + 0.4 * t) + 14 * math.sin(t * 3 + ph * 9)
        a = min(1.0, t * 3) * 0.9
        ctx.save(); ctx.translate(x, y); ctx.rotate(t * 4 * sp + ph * 6)
        ctx.rectangle(-5, -2.5, 10, 5)
        ctx.set_source_rgba(*(accent() if is_gold else (1, 1, 1)), a); ctx.fill(); ctx.restore()


def dust(ctx, x, y, k, spread=1.0):
    if not 0 < k < 1:
        return
    for sd in (-1, 1):
        for i in range(3):
            ctx.new_path()
            ctx.arc(x + sd * spread * (12 + 40 * k + 14 * i), y - 4 - 10 * k * i, 5 + 11 * k, 0, 2 * math.pi)
            ctx.set_source_rgba(0.6, 0.6, 0.6, 0.45 * (1 - k)); ctx.fill()


def tremble(t, amt):
    return amt * (math.sin(t * 61) * 0.6 + math.sin(t * 37 + 1) * 0.4)


def cam(ctx, z, wx, wy, sx=540, sy=1200):
    ctx.rectangle(0, 705, 1080, 1215); ctx.clip()
    ctx.translate(sx, sy); ctx.scale(z, z); ctx.translate(-wx, -wy)


def darkness(ctx, amt, x0=560):
    """What he can't see: the right side of the frame sinks into black."""
    if amt <= 0:
        return
    g = cairo.LinearGradient(x0, 0, 1080, 0)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(0.6, 0, 0, 0, 0.85 * amt)
    g.add_color_stop_rgba(1, 0, 0, 0, amt)
    ctx.rectangle(0, 705, 1080, 1215); ctx.set_source(g); ctx.fill()


# ---------- scenes ----------
def s1_hook(duration=3.5):
    t_hit = 0.75

    def draw(ctx, t):
        imp = t - t_hit
        hit = imp > 0
        x = 600 + 150 * min(t, t_hit) + (8 * ease(imp / 0.2) if hit else 0)
        if t < 0.45:
            pose = struggle_run(x / 26)
        elif not hit:
            pose = mix(struggle_run(x / 26), FALL, eio((t - 0.45) / 0.3))
        else:
            pose = mix(mix(FALL, HANDS_DOWN, ease(imp / 0.12)), KNEEL_UP, eio((t - 1.5) / 0.9))
            pose = pose_with(pose, lean=pose["lean"] + 0.05 * math.sin(t * 9) * ease((t - 1.5) / 0.5))
        pull = eio((t - 1.0) / 1.3)
        ctx.save()
        if hit:
            ctx.translate(9 * math.exp(-7 * imp) * math.sin(55 * imp), 8 * math.exp(-8 * imp) * math.sin(63 * imp))
        cam(ctx, lerp(2.4 + 0.25 * clamp(t / t_hit), 0.95, pull), lerp(x + 10, XK + 300, pull),
            lerp(G - 85, G - 150, pull), 540, lerp(1150, 1200, pull))
        world(ctx, t)
        fig(ctx, x, G, S, pose, face="strain", knee_shake=tremble(t, 2.2 if not hit else 1.0))
        if hit:
            dust(ctx, x + 10, G, imp / 0.7, spread=1.3)
        ctx.restore()
        darkness(ctx, 0.9 * pull)
        if hit:
            ctx.set_source_rgba(1, 1, 1, 0.20 * math.exp(-10 * imp)); ctx.paint()
        caption(ctx, t, "His legs were shaking.", "Then they gave out.", t2=1.2)
    return Scene(draw, duration, "custom:knees_hit_hook", "His legs were shaking. / Then they gave out.")


def s2_no_finish(duration=4.5):
    def draw(ctx, t):
        ctx.save()
        cam(ctx, 0.95, XK + 300, G - 150)
        world(ctx, t)
        x = XK + 150 * eio((t - 2.8) / 1.1)
        if t < 1.6:
            pose = pose_with(KNEEL_UP, lean=-0.04 + 0.04 * math.sin(t * 8))
        elif t < 2.8:
            pose = mix(mix(KNEEL_UP, HANDS_DOWN, eio((t - 1.6) / 0.4)), TIRED, eio((t - 2.0) / 0.7))
        elif t < 3.9:
            pose = mix(TIRED, struggle_run((x - XK) / 26), ease((t - 2.8) / 0.3))
        else:
            pose = mix(struggle_run((x - XK) / 26), ONE_KNEE, eio((t - 3.9) / 0.3))
        fig(ctx, x, G, S, pose, knee_shake=tremble(t, 1.6))
        ctx.restore()
        darkness(ctx, 0.9)
        caption(ctx, t, "He looked ahead.", "No finish line in sight.", t2=1.3)
    return Scene(draw, duration, "custom:no_finish_in_sight", "He looked ahead. / No finish line in sight.")


def s3_sit(duration=4.0):
    head = (XS + 26, G - 98)

    def draw(ctx, t):
        push = eio((t - 1.8) / 2.0)
        ctx.save()
        cam(ctx, lerp(0.95, 2.2, push), lerp(XK + 300, head[0], push), lerp(G - 150, head[1], push),
            540, lerp(1200, 1150, push))
        world(ctx, t)
        x = lerp(XK + 150, XS, eio(t / 0.9))
        pose = mix(mix(ONE_KNEE, SIT_UP, eio(t / 0.9)), SIT_DOWN, eio((t - 1.0) / 1.2))
        pose = pose_with(pose, lean=pose["lean"] + 0.03 * math.sin(t * 5))
        fig(ctx, x, G, S, pose, face="closed" if t > 3.0 else "open", knee_shake=tremble(t, 0.8))
        ctx.restore()
        darkness(ctx, 0.9 * (1 - push * 0.5))
        caption(ctx, t, "Exhausted, he sat down.", "And closed his eyes.", t2=2.4)
    return Scene(draw, duration, "custom:sits_eyes_closed", "Exhausted, he sat down. / And closed his eyes.")


def s4_crane(duration=5.5):
    head = (XS + 26, G - 98)

    def draw(ctx, t):
        k = eio((t - 0.2) / 4.0)
        reveal = ease((t - 1.6) / 1.6)
        ctx.save()
        cam(ctx, math.exp(lerp(math.log(2.2), math.log(0.58), k)), lerp(head[0], (XS + XF) / 2 + 60, k),
            lerp(head[1], G - 360, k), 540, lerp(1150, 1260, k))
        world(ctx, t, finish_glow=reveal, stars=0.5 + 0.5 * k, finish_a=ease((t - 1.2) / 1.2))
        fig(ctx, XS, G, S, pose_with(SIT_DOWN, lean=SIT_DOWN["lean"] + 0.03 * math.sin(t * 2)), face="closed")
        dots = ease((t - 3.0) / 1.5)
        if dots > 0:  # the few steps between him and the line
            n = int(16 * dots)
            for i in range(n):
                px = lerp(XS + 70, XF - 20, i / 15)
                ctx.new_path(); ctx.arc(px, road_y(px) - 14, 5, 0, 2 * math.pi)
                ctx.set_source_rgba(*accent(), 0.75); ctx.fill()
        ctx.restore()
        darkness(ctx, 0.9 * (1 - ease((t - 0.6) / 1.8)))
        caption(ctx, t, "Just beyond that hill...", "only a few steps away.", t2=2.7)
    return Scene(draw, duration, "custom:crane_reveal", "Just beyond that hill... / only a few steps away.")


def s5_stand(duration=5.0):
    def draw(ctx, t):
        up = eio((t - 3.6) / 1.1)
        ctx.save()
        cam(ctx, lerp(1.9, 1.45, up), XS + 40, lerp(G - 85, G - 110, up), 540, 1180)
        world(ctx, t)
        lift = eio((t - 0.8) / 0.6)
        hands = ease((t - 1.6) / 0.4) * (1 - ease((t - 2.8) / 0.3))
        down = eio((t - 2.9) / 0.6)
        pose = mix(SIT_DOWN, SIT_UP, lift)
        pose = mix(pose, LOOK_HANDS, hands)
        pose = mix(pose, HANDS_DOWN, down)
        pose = mix(pose, TIRED, up)
        j = fig(ctx, XS + 20 * down, G, S, pose, face="closed" if t < 0.7 else "open",
                knee_shake=tremble(t, 1.0 + 1.5 * up), hand_shake=tremble(t * 1.3, 2.5 * hands))
        if hands > 0:
            halo(ctx, j["hand_f"][0], j["hand_f"][1], 60, a=0.35 * hands)
        ctx.restore()
        darkness(ctx, 0.9)
        caption(ctx, t, "He couldn't see it.", "But he stood up anyway.", t2=3.0)
    return Scene(draw, duration, "custom:stands_again", "He couldn't see it. / But he stood up anyway.")


def s6_crest(duration=6.0):
    def draw(ctx, t):
        x = XS + 20 + 60 * eio((t - 0.2) / 1.4) + (HC - XS - 80) * clamp((t - 1.6) / 1.6) ** 1.1
        x += (XF + 40 - HC) * eio((t - 4.1) / 1.6)
        frozen = 3.2 < t < 4.1
        walking = (0.2 < t < 3.2) or (4.1 < t < 5.7)
        pose = pose_with(walk((x - XS) / 30, 0.36), lean=0.10) if walking else TIRED
        if frozen:
            pose = pose_with(STAND, lean=-0.04)
        punch = math.sin(math.pi * clamp((t - 3.1) / 1.2))
        ctx.save()
        cam(ctx, 1.0 + 0.35 * punch, lerp(x + 220, x + 60, punch), road_y(x) - lerp(150, 110, punch))
        crossed = t - 5.35
        world(ctx, t, finish_glow=ease((t - 2.4) / 0.8), finish_a=ease((t - 2.3) / 0.9))
        fig(ctx, x, road_y(x), S, pose, face="wide" if t > 3.2 else "open", knee_shake=tremble(t, 0.9))
        confetti(ctx, crossed, XF, road_y(XF) - 40)
        ctx.restore()
        darkness(ctx, 0.9 * (1 - clamp((x - XS) / (HC - XS)) ** 1.5))
        caption(ctx, t, "One step. Then another.", "There it was.", t2=3.25)
    return Scene(draw, duration, "custom:crest_and_cross", "One step. Then another. / There it was.")


def s7_pull_away(duration=3.0):
    def draw(ctx, t):
        k = eio(t / duration)
        ctx.save()
        cam(ctx, math.exp(lerp(math.log(1.5), math.log(0.55), k)), XF + 20, road_y(XF) - lerp(130, 320, k),
            540, 1250)
        world(ctx, t, finish_glow=1.0, stars=0.5 + 0.5 * k, finish_a=1.0)
        halo(ctx, XF + 40, road_y(XF) - 100, 200, col=accent(), a=0.25)
        fig(ctx, XF + 40, road_y(XF + 40), S, pose_with(STAND, lean=0.0, ua_f=0.35, fa_f=0.5))
        confetti(ctx, t + 0.65, XF, road_y(XF) - 40)
        ctx.restore()
    return Scene(draw, duration, "custom:under_the_line", "")


def s8_message(duration=3.5):
    def draw(ctx, t):
        words(ctx, "YOU CAN'T ALWAYS SEE", 900, 0.15, t, size=54, step=0.14)
        words(ctx, "HOW CLOSE YOU ARE.", 975, 0.75, t, size=54, step=0.16, accent_words={"CLOSE"})
        a = ease((t - 1.6) / 0.8)
        if a > 0:
            halo(ctx, 540, 1080, 90, col=accent(), a=0.3 * a)
            ctx.new_path(); ctx.set_source_rgba(*accent(), a); ctx.set_line_width(3)
            ctx.move_to(490, 1080); ctx.line_to(590, 1080); ctx.stroke()
    return Scene(draw, duration, "custom:final_message", "YOU CAN'T ALWAYS SEE / HOW CLOSE YOU ARE.")


EPISODE = dict(
    title="How Close You Are",
    accent=GOLD,
    watermark="",
    fade_out=0.3, black=1 / 30, fade_in=0.35, end_fade=0.6,
    scenes=[s1_hook(), s2_no_finish(), s3_sit(), s4_crane(), s5_stand(), s6_crest(), s7_pull_away(),
            s8_message()],
)
