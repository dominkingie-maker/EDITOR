"""ONE MORE FAVOR — "You're allowed to have limits." 30 s, music only, story told in captions.

Hook: frame 0 is an extreme close-up of his strained face peeking over the parcels he hugs. A box
drops into frame and lands over his face with a thud; the camera pulls back to reveal the scene.

  python3 <skill>/scripts/engine.py episode.py --preview sheet.png
  python3 <skill>/scripts/engine.py episode.py --out short.mp4 --music music.wav
"""
import math

import cairo
from engine import (GOLD, SIT_CHAIR, STAND, TEXT_Y1, TEXT_Y2, Scene, accent, caption, clamp, ease, eio,
                    halo, lerp, mix, rounded_rect, walk, words)
from props import lamp_post, tree

G = 1400
S, OS = 62, 58
OTHER = (0.55, 0.55, 0.55)
GREY_RIM = (0.72, 0.72, 0.72)
BENCH_X = 200                     # where the bench sits once he stops walking

HUG = dict(ua_f=0.55, fa_f=1.20, ua_b=0.45, fa_b=1.10)        # arms around the parcels
REACH = dict(ua_f=1.45, fa_f=1.45)
POINT = dict(ua_f=1.60, fa_f=1.62)
HOLD_OUT = dict(ua_f=1.45, fa_f=1.55, ua_b=1.35, fa_b=1.50)
CARRY_LOW = dict(ua_f=0.90, fa_f=1.60, ua_b=0.80, fa_b=1.50)
HALF_UP = dict(lean=0.42, th_f=0.75, sh_f=-0.35, th_b=0.45, sh_b=-0.55,
               ua_f=0.70, fa_f=0.90, ua_b=0.60, fa_b=0.80, hip=0.20)   # bent, hands near knees
SQUAT_PUT = dict(lean=0.45, th_f=1.10, sh_f=-0.30, th_b=0.90, sh_b=-0.40,
                 ua_f=0.95, fa_f=0.75, ua_b=0.85, fa_b=0.65, hip=0.35)
SLUMP_SIT = dict(SIT_CHAIR, lean=0.48, ua_f=0.55, fa_f=0.95, ua_b=0.45, fa_b=0.85)
REST_SIT = dict(SIT_CHAIR, lean=-0.06, ua_f=0.25, fa_f=1.25, ua_b=0.15, fa_b=1.15)

PARCELS = [(116, 26, 0), (104, 22, 7), (110, 20, -5)]   # hugged against his chest, top at his chin
FACE_BOX = (106, 52, 2)                                 # the "one more" that covers his face


def pose_with(p, **kw):
    q = dict(p); q.update(kw)
    return q


def hug_walk(ph, lean=0.08):
    return pose_with(walk(ph, stride=0.30), lean=lean, **HUG)


# ---------- drawing ----------
def fig(ctx, x, ground, s, pose, col=(1, 1, 1), a=1.0, d=1, head_dx=0.0, knee_shake=0.0, face=None):
    """engine.figure plus a movable head, trembling knees and an optional side-view face."""
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
    head = (x + ux * (T + 0.14 * s + r) + head_dx, hy + uy * (T + 0.14 * s + r))
    ctx.new_path()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(0.22 * s)

    def limb(p0, a1, l1, a2, l2, shade, jitter=0.0):
        p1 = seg(p0, a1, l1); p1 = (p1[0] + jitter, p1[1])
        p2 = seg(p1, a2, l2)
        ctx.set_source_rgba(*(c * shade for c in col), a)
        ctx.move_to(*p0); ctx.line_to(*p1); ctx.line_to(*p2); ctx.stroke()
        return p1, p2

    _, hand_b = limb(sh, pose["ua_b"], A1, pose["fa_b"], A2, 0.5)
    knee_b, _ = limb(hip, pose["th_b"], L1, pose["sh_b"], L2, 0.5, -knee_shake)
    ctx.set_source_rgba(*col, a); ctx.move_to(*hip); ctx.line_to(*neck); ctx.stroke()
    knee_f, _ = limb(hip, pose["th_f"], L1, pose["sh_f"], L2, 1.0, knee_shake)
    _, hand_f = limb(sh, pose["ua_f"], A1, pose["fa_f"], A2, 1.0)
    ctx.set_source_rgba(*col, a); ctx.arc(*head, r, 0, 2 * math.pi); ctx.fill()
    if face == "strain":  # squeezed eye + panting mouth on the facing side
        ex, ey = head[0] + d * 0.42 * r, head[1] - 0.12 * r
        ctx.set_source_rgba(0, 0, 0, a); ctx.set_line_width(0.13 * r)
        ctx.move_to(ex - d * 0.16 * r, ey - 0.14 * r); ctx.line_to(ex + d * 0.06 * r, ey)
        ctx.line_to(ex - d * 0.16 * r, ey + 0.14 * r); ctx.stroke()
        ctx.arc(head[0] + d * 0.55 * r, head[1] + 0.42 * r, 0.12 * r, 0, 2 * math.pi); ctx.fill()
    return dict(head=head, hand_f=hand_f, hand_b=hand_b, r=r, hip=hip, knees=(knee_f, knee_b))


def box(ctx, cx, bottom, w, h, a=1.0, rim=GREY_RIM):
    rounded_rect(ctx, cx - w / 2, bottom - h, w, h, 5)
    ctx.set_source_rgba(0.13, 0.13, 0.13, a); ctx.fill_preserve()
    ctx.set_source_rgba(*rim, a); ctx.set_line_width(3); ctx.stroke()
    ctx.set_source_rgba(*(c * 0.6 for c in rim), a)
    ctx.move_to(cx, bottom - h + 3); ctx.line_to(cx, bottom - h + min(h * 0.45, 22)); ctx.stroke()


def stack(ctx, bx, by, boxes, sway=0.0, squash=1.0, a=1.0):
    """Boxes bottom-up from (bx, by); sway pushes the upper boxes sideways. Returns the top centre."""
    y, lx = 0.0, 0.0
    total = sum(h for _, h, _ in boxes)
    for w, h, off in boxes:
        hh = h * squash
        lx = off + sway * ((-y) / max(total, 1)) ** 1.5
        box(ctx, bx + lx, by + y, w, hh, a)
        y -= hh
    return (bx + lx, by + y)


def hugged(ctx, j, boxes, **kw):
    """Parcels hugged against the chest, centred just in front of the body (they hide the arms)."""
    return stack(ctx, j["hip"][0] + 26, min(j["hand_f"][1], j["hand_b"][1]) + 12, boxes, **kw)


def bench(ctx, x, a=1.0, glow=0.0, col=None):
    col = col or (0.7, 0.7, 0.7)
    if glow > 0:
        halo(ctx, x, G - 60, 220, col=col, a=0.25 * glow)
    ctx.new_path(); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgba(*col, a); ctx.set_line_width(6)
    for sx in (-92, 92):
        ctx.move_to(x + sx, G); ctx.line_to(x + sx, G - 34)
        ctx.move_to(x + sx, G - 34); ctx.line_to(x + sx - 6, G - 104)
    ctx.stroke()
    for y0, h in ((G - 40, 10), (G - 106, 10), (G - 84, 9)):
        dx = -6 if y0 < G - 50 else 0
        rounded_rect(ctx, x - 112 + dx, y0, 224, h, 3)
        ctx.set_source_rgba(0.2, 0.2, 0.2, a); ctx.fill_preserve()
        ctx.set_source_rgba(*col, a); ctx.set_line_width(2.5); ctx.stroke()


def park(ctx, scroll=0.0):
    """Path, dashes and dim trees / lamps drifting by at half speed (parallax)."""
    for k in range(5):
        x = (k * 340 + 120 - scroll * 0.5) % 1700 - 300
        if k % 2:
            lamp_post(ctx, x, G - 6, h=300, a=0.35, on=True)
        else:
            tree(ctx, x, G - 6, s=0.95, a=0.55, shade=0.14)
    ctx.new_path(); ctx.set_line_width(3); ctx.set_source_rgba(0.42, 0.42, 0.42, 1)
    ctx.move_to(0, G + 2); ctx.line_to(1080, G + 2); ctx.stroke()
    ctx.set_line_width(2); ctx.set_source_rgba(0.24, 0.24, 0.24, 1)
    for k in range(14):
        x = (k * 90 - scroll) % 1260 - 90
        ctx.move_to(x, G + 22); ctx.line_to(x + 34, G + 22)
    ctx.stroke()


def dust(ctx, x, y, k, spread=1.0):
    if not 0 < k < 1:
        return
    for sd in (-1, 1):
        for i in range(3):
            ctx.new_path()
            ctx.arc(x + sd * spread * (12 + 40 * k + 14 * i), y - 4 - 10 * k * i, 5 + 11 * k, 0, 2 * math.pi)
            ctx.set_source_rgba(0.6, 0.6, 0.6, 0.4 * (1 - k)); ctx.fill()


def tremble(t, amt):
    return amt * (math.sin(t * 61) * 0.6 + math.sin(t * 37 + 1) * 0.4)


def cam(ctx, z, wx, wy, sx, sy):
    ctx.rectangle(0, 705, 1080, 1215); ctx.clip()
    ctx.translate(sx, sy); ctx.scale(z, z); ctx.translate(-wx, -wy)


def cap(ctx, t, l1, l2, t2, a=1.0):
    if a <= 0 or t < 0:
        return
    ctx.push_group(); caption(ctx, t, l1, l2, t2=t2); ctx.pop_group_to_source(); ctx.paint_with_alpha(a)


def in_front(ctx, draw_fig, draw_props):
    """Draw props first, then the figure on top (figure rendered into a group so we know its joints)."""
    ctx.push_group(); j = draw_fig(); fg = ctx.pop_group()
    out = draw_props(j)
    ctx.set_source(fg); ctx.paint()
    return j, out


def behind(ctx, draw_fig, draw_props):
    j = draw_fig()
    return j, draw_props(j)


# ---------- scenes ----------
HX = 400


def s1_hook(duration=3.0):
    t_hit = 0.55

    def draw(ctx, t):
        imp = t - t_hit
        hit = imp > 0
        pull = eio((t - 0.85) / 1.1)
        dist = 40 * t
        x = HX + tremble(t, 1.5)
        sway = 10 * math.sin(t * 3.4) + (16 * math.exp(-4 * imp) * math.sin(12 * imp) if hit else 0)
        head_w = (HX + 16, G - 158)
        ctx.save()
        if hit:
            ctx.translate(7 * math.exp(-8 * imp) * math.sin(55 * imp), 6 * math.exp(-8 * imp) * math.sin(61 * imp))
        cam(ctx, lerp(2.3, 1.0, pull), lerp(head_w[0], 540, pull), lerp(head_w[1], 1150, pull),
            540, lerp(1060, 1150, pull))
        park(ctx, dist)
        # the "friend" adding one more, from the right
        gx = 560 + 70 * eio((t - 0.7) / 0.8)
        arms = mix(pose_with(STAND, ua_f=2.15, fa_f=2.0, ua_b=2.05, fa_b=1.9), STAND, eio((t - 0.6) / 0.7))
        gj = fig(ctx, gx, G, OS, arms, col=OTHER, d=-1)
        squash = 1 - (0.08 * math.exp(-7 * imp) * abs(math.cos(9 * imp)) if hit else 0)
        pose = hug_walk(dist / 30, lean=0.10)
        j, top = behind(ctx, lambda: fig(ctx, x, G, S, pose, face="strain", knee_shake=tremble(t, 1.5)),
                        lambda j: hugged(ctx, j, PARCELS + ([FACE_BOX] if hit else []), sway=sway, squash=squash))
        if not hit:  # the box comes down into frame from the friend's hands
            u = eio(clamp((t + 0.2) / (t_hit + 0.2)))
            land = stack_top_before_hit(j, sway)
            bx = lerp(gj["hand_f"][0] - 30, land[0] + FACE_BOX[2], u)
            by = lerp(G - 250, land[1], u)
            box(ctx, bx, by, FACE_BOX[0], FACE_BOX[1])
        else:
            dust(ctx, top[0], top[1] + FACE_BOX[1] + 2, imp / 0.6, spread=1.2)
        ctx.restore()
        if hit:
            ctx.set_source_rgba(1, 1, 1, 0.16 * math.exp(-10 * imp)); ctx.paint()
        caption(ctx, t, "One more favor.", "He could barely stand.", t2=1.3)
    return Scene(draw, duration, "custom:face_box_hook", "One more favor. / He could barely stand.")


def stack_top_before_hit(j, sway):
    total = sum(h for _, h, _ in PARCELS)
    return (j["hip"][0] + 26 + PARCELS[-1][2] + sway, min(j["hand_f"][1], j["hand_b"][1]) + 12 - total)


def s2_bench(duration=5.0):
    def draw(ctx, t):
        dist = 70 * t - 42 * max(0.0, min(t, 3.6) - 1.6)   # he slows down beside the bench
        park(ctx, dist)
        bx = 500 - dist
        longing = ease((t - 1.9) / 0.4) * (1 - ease((t - 3.7) / 0.5))
        bench(ctx, bx, glow=longing)
        # the one who keeps him going, ahead on the path, points further on
        point = eio((t - 3.0) / 0.4)
        gp = pose_with(STAND, **{k: lerp(STAND[k], v, point) for k, v in POINT.items()})
        fig(ctx, 830, G, OS, gp, col=OTHER)
        pose = hug_walk(dist / 30, lean=lerp(0.10, -0.05, longing))
        behind(ctx, lambda: fig(ctx, HX + tremble(t, 1.4), G, S, pose, head_dx=-46 * longing,
                                knee_shake=tremble(t + 1, 1.5)),
               lambda j: hugged(ctx, j, PARCELS + [FACE_BOX], sway=9 * math.sin(t * 3.0)))
        caption(ctx, t, "He needed a break.", "But he kept saying yes.", t2=2.6)
    return Scene(draw, duration, "custom:pass_the_bench", "He needed a break. / But he kept saying yes.")


def s3_another(duration=5.0):
    def draw(ctx, t):
        park(ctx, 330)
        bench(ctx, BENCH_X)
        down = eio(t / 1.2)
        rise = eio((t - 1.3) / 0.6) * 0.6              # never gets fully upright
        reach = eio((t - 2.7) / 1.2)
        hp = mix(mix(pose_with(STAND, lean=0.08, **HUG), SQUAT_PUT, down), HALF_UP, rise / 0.6 if rise else 0)
        hp = pose_with(hp, ua_f=lerp(hp["ua_f"], REACH["ua_f"], reach), fa_f=lerp(hp["fa_f"], REACH["fa_f"], reach))
        gx = lerp(1010, 720, eio((t - 1.2) / 0.9))
        gp = walk((1010 - gx) / 34, 0.4) if 1.2 < t < 2.1 else STAND
        gj = fig(ctx, gx, G, OS, pose_with(gp, **HOLD_OUT), col=OTHER, d=-1)
        box(ctx, gj["hand_f"][0] - 24, gj["hand_f"][1] + 8, 72, 56)
        sx = lerp(HX + 26, HX + 110, down)
        sy = lerp(G - 100, G, down)
        stack(ctx, sx, sy, PARCELS + [FACE_BOX])
        fig(ctx, HX + tremble(t, 1.0), G, S, hp, knee_shake=tremble(t + 2, 1.8 * rise))
        caption(ctx, t, "Even when he was exhausted.", "", t2=9)
    return Scene(draw, duration, "custom:offered_another", "Even when he was exhausted.")


def s4_notice(duration=5.0):
    def draw(ctx, t):
        park(ctx, 330)
        look_knees = ease((t - 0.9) / 0.4) * (1 - ease((t - 2.2) / 0.4))
        look_bench = ease((t - 2.4) / 0.4)
        back = eio((t - 3.3) / 1.4)
        bench(ctx, BENCH_X, glow=look_bench)
        gj = fig(ctx, 720, G, OS, pose_with(STAND, **HOLD_OUT), col=OTHER, d=-1)
        box(ctx, gj["hand_f"][0] - 24, gj["hand_f"][1] + 8, 72, 56)
        stack(ctx, HX + 110, G, PARCELS + [FACE_BOX])
        hp = pose_with(HALF_UP, ua_f=lerp(REACH["ua_f"], HALF_UP["ua_f"], back),
                       fa_f=lerp(REACH["fa_f"], HALF_UP["fa_f"], back),
                       lean=HALF_UP["lean"] + 0.18 * look_knees)
        j = fig(ctx, HX + tremble(t, 0.8), G, S, hp, head_dx=-30 * look_bench,
                knee_shake=tremble(t + 2, 1.2 + 2.2 * look_knees))
        for k in j["knees"]:
            halo(ctx, k[0], k[1], 55, a=0.35 * look_knees)
        caption(ctx, t, "This time, he noticed", "what it was costing him.", t2=2.2)
    return Scene(draw, duration, "custom:noticed_cost", "This time, he noticed / what it was costing him.")


def s5_let_down(duration=6.0):
    def draw(ctx, t):
        park(ctx, 330)
        bench(ctx, BENCH_X, glow=0.4)
        stack(ctx, HX + 110, G, PARCELS + [FACE_BOX])
        up = eio(t / 0.8)
        shake = 5 * math.sin(2 * math.pi * 1.6 * (t - 0.9)) * ease((t - 0.9) / 0.2) * (1 - ease((t - 2.2) / 0.3))
        hp = mix(HALF_UP, pose_with(STAND, lean=0.04), up)
        fig(ctx, HX, G, S, hp, head_dx=shake)
        # their shoulders drop... a pause... then they carry it away themselves
        drop = eio((t - 2.1) / 0.6)
        leave = eio((t - 3.7) / 2.0)
        if t < 3.6:
            gp = pose_with(STAND, **HOLD_OUT)
            gp = mix(gp, pose_with(gp, lean=0.42, ua_f=0.9, fa_f=1.1, ua_b=0.8, fa_b=1.0), drop)
            gj = fig(ctx, 720, G, OS, gp, col=OTHER, d=-1)
            box(ctx, gj["hand_f"][0] - 24 + 10 * drop, gj["hand_f"][1] + 8, 72, 56)
        else:
            gx = lerp(720, 1160, leave)
            gp = pose_with(walk((gx - 720) / 34, 0.38), lean=0.12, **CARRY_LOW)
            gj = fig(ctx, gx, G, OS, gp, col=OTHER, d=1)
            box(ctx, gj["hand_f"][0] + 18, gj["hand_f"][1] + 8, 72, 56)
        caption(ctx, t, "They weren't happy.", "He let them be disappointed.", t2=2.7)
    return Scene(draw, duration, "custom:let_them_be", "They weren't happy. / He let them be disappointed.")


def s6_rest(duration=6.0):
    def draw(ctx, t):
        push = eio((t - 2.6) / 3.0)
        ctx.save()
        cam(ctx, lerp(1.0, 1.55, push), lerp(540, BENCH_X + 60, push), lerp(1150, G - 90, push),
            540, lerp(1150, 1200, push))
        park(ctx, 330)
        glow = ease((t - 0.9) / 1.4)
        halo(ctx, BENCH_X + 10, G - 90, 300, col=accent(), a=0.30 * glow)
        bench(ctx, BENCH_X, col=tuple(lerp(c, a, 0.6 * glow) for c, a in zip((0.7, 0.7, 0.7), accent())))
        stack(ctx, HX + 110, G, PARCELS + [FACE_BOX], a=1 - 0.6 * glow)
        sit = eio(t / 0.9)
        relax = eio((t - 0.9) / 1.6)
        hx = lerp(HX, BENCH_X + 10, eio(t / 0.7))
        hp = mix(mix(pose_with(STAND, lean=0.04), SLUMP_SIT, sit), REST_SIT, relax)
        fig(ctx, hx, G, S, pose_with(hp, lean=hp["lean"] + 0.02 * math.sin(t * 1.6) * relax))  # slow breathing
        ctx.restore()
        cap(ctx, t, "He finally gave himself a break.", "", 9, a=1 - ease((t - 2.6) / 0.4))
        if t > 3.0:
            words(ctx, "YOU'RE ALLOWED", TEXT_Y1 - 10, 3.05, t, size=52, step=0.14)
            words(ctx, "TO HAVE LIMITS.", TEXT_Y2 + 6, 3.5, t, size=52, step=0.16, accent_words={"LIMITS."})
    return Scene(draw, duration, "custom:bench_rest", "He finally gave himself a break. / YOU'RE ALLOWED TO HAVE LIMITS.")


EPISODE = dict(
    title="One More Favor",
    accent=GOLD,
    watermark="",
    fade_out=0.25, black=1 / 30, fade_in=0.3, end_fade=0.5,
    scenes=[s1_hook(), s2_bench(), s3_another(), s4_notice(), s5_let_down(), s6_rest()],
)
