"""YOU CAN CARE WITHOUT CARRYING EVERYTHING — 30 s, music only, story told in captions.

One continuous story in 7 beats (timings match the brief). Hook: frame 0 already has a box
in mid-air; it slams onto the swaying stack with a zoom punch, screen shake, flash and dust,
and his knees buckle.

  python3 <skill>/scripts/engine.py episode.py --preview sheet.png
  python3 <skill>/scripts/engine.py episode.py --out short.mp4 --music music.wav
"""
import math

import cairo
from engine import (CARRY, GOLD, STAND, TEXT_Y1, TEXT_Y2, Scene, accent, camera, caption, clamp, ease,
                    eio, halo, lerp, mix, rounded_rect, walk, words)

G = 1400
HERO_X, S, OS = 400, 62, 58      # hero position / hero size / others' size
OTHER = (0.55, 0.55, 0.55)
GREY_RIM = (0.72, 0.72, 0.72)

BUCKLE = dict(lean=0.30, th_f=0.60, sh_f=-0.50, th_b=0.30, sh_b=-0.65,
              ua_f=0.90, fa_f=1.60, ua_b=0.80, fa_b=1.50, hip=0.18)
SQUAT_CARRY = dict(lean=0.45, th_f=1.10, sh_f=-0.30, th_b=0.90, sh_b=-0.40,
                   ua_f=1.20, fa_f=1.30, ua_b=1.10, fa_b=1.20, hip=0.35)
CARRY_ARMS = dict(ua_f=0.90, fa_f=1.60, ua_b=0.80, fa_b=1.50)
PALM = dict(ua_f=1.35, fa_f=2.70)           # forearm up, palm out: "no"
THROWN = dict(ua_f=2.30, fa_f=2.60, ua_b=2.10, fa_b=2.40)

# the burden stack: (width, height, x offset) bottom to top
STACK = [(124, 82, 0), (112, 74, 7), (118, 78, -6), (106, 70, 9), (114, 76, -4), (100, 66, 6)]
LANDED = (96, 62, -2)


def pose_with(p, **kw):
    q = dict(p); q.update(kw)
    return q


def carry_walk(ph, lean=0.12):
    return pose_with(walk(ph, stride=0.38), lean=lean, **CARRY_ARMS)


# ---------- drawing ----------
def fig(ctx, x, ground, s, pose, col=(1, 1, 1), a=1.0, d=1, head_dx=0.0):
    """engine.figure with a movable head (for the head shake). Returns joints."""
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

    def limb(p0, a1, l1, a2, l2, shade):
        p1 = seg(p0, a1, l1); p2 = seg(p1, a2, l2)
        ctx.set_source_rgba(*(c * shade for c in col), a)
        ctx.move_to(*p0); ctx.line_to(*p1); ctx.line_to(*p2); ctx.stroke()
        return p2

    hand_b = limb(sh, pose["ua_b"], A1, pose["fa_b"], A2, 0.5)
    limb(hip, pose["th_b"], L1, pose["sh_b"], L2, 0.5)
    ctx.set_source_rgba(*col, a); ctx.move_to(*hip); ctx.line_to(*neck); ctx.stroke()
    limb(hip, pose["th_f"], L1, pose["sh_f"], L2, 1.0)
    hand_f = limb(sh, pose["ua_f"], A1, pose["fa_f"], A2, 1.0)
    ctx.set_source_rgba(*col, a); ctx.arc(*head, r, 0, 2 * math.pi); ctx.fill()
    return dict(head=head, hand_f=hand_f, hand_b=hand_b, r=r, hip=hip)


def box(ctx, cx, bottom, w, h, a=1.0, rim=GREY_RIM, glow=0.0):
    if glow > 0:
        halo(ctx, cx, bottom - h / 2, w * 1.6, col=accent(), a=0.35 * glow * a)
    rounded_rect(ctx, cx - w / 2, bottom - h, w, h, 5)
    ctx.set_source_rgba(0.13, 0.13, 0.13, a); ctx.fill_preserve()
    ctx.set_source_rgba(*rim, a); ctx.set_line_width(3); ctx.stroke()
    ctx.set_source_rgba(*(c * 0.6 for c in rim), a); ctx.set_line_width(3)
    ctx.move_to(cx, bottom - h + 3); ctx.line_to(cx, bottom - h + h * 0.38); ctx.stroke()
    ctx.move_to(cx - w * 0.3, bottom - h * 0.22); ctx.line_to(cx - w * 0.1, bottom - h * 0.22); ctx.stroke()


def stack(ctx, bx, by, boxes, tilt=0.0, sway=0.0, squash=1.0, a=1.0):
    """Boxes bottom-up from (bx, by), rotated by tilt around the base. sway bends the top sideways.
    Returns the world position of the top centre (where the next box lands)."""
    ctx.save(); ctx.translate(bx, by); ctx.rotate(tilt)
    y, total = 0.0, sum(h for _, h, _ in boxes)
    lx = 0.0
    for w, h, off in boxes:
        hh = h * squash
        lx = off + sway * ((-y) / max(total, 1)) ** 2
        box(ctx, lx, y, w, hh, a)
        y -= hh
    ctx.restore()
    c, s_ = math.cos(tilt), math.sin(tilt)
    return (bx + c * lx - s_ * y, by + s_ * lx + c * y)


def carried(ctx, j, boxes, d=1, **kw):
    """Stack resting on the hands in front of a carrying figure."""
    bx = j["hand_f"][0] + d * boxes[0][0] * 0.32
    by = min(j["hand_f"][1], j["hand_b"][1]) + 6
    return stack(ctx, bx, by, boxes, **kw)


def floor(ctx, scroll=0.0):
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
            ctx.arc(x + sd * spread * (12 + 40 * k + 14 * i), y - 4 - 12 * k * i, 5 + 12 * k, 0, 2 * math.pi)
            ctx.set_source_rgba(0.6, 0.6, 0.6, 0.4 * (1 - k)); ctx.fill()


def tremble(t, amt):
    return amt * (math.sin(t * 61) * 0.6 + math.sin(t * 37 + 1) * 0.4)


def cap(ctx, t, l1, l2, t2):
    caption(ctx, t, l1, l2, t2=t2)


# ---------- scenes ----------
def s1_hook(duration=3.0):
    """Frame 0: a box is already flying in. It slams onto the swaying stack; knees buckle."""
    t_hit = 0.55

    def draw(ctx, t):
        imp = t - t_hit
        hit = imp > 0
        z = 1.0 + 0.10 * math.exp(-5 * imp) if hit else 1.0 + 0.05 * eio(t / t_hit)
        ctx.save()
        if hit:
            ctx.translate(9 * math.exp(-7 * imp) * math.sin(55 * imp), 7 * math.exp(-8 * imp) * math.sin(63 * imp))
        camera(ctx, z, HERO_X + 60, 1150)
        floor(ctx)
        b = 1 - math.exp(-7 * imp) * math.cos(9 * imp) if hit else 0.0
        pose = mix(CARRY, BUCKLE, b * 0.85 + 0.15)
        x = HERO_X + tremble(t, 1.2 if not hit else 2.0 * (1 - 0.5 * clamp(imp)))
        # the giver who just tossed it
        throw = ease(t / 1.2)
        fig(ctx, 830, G, OS, mix(pose_with(STAND, **THROWN), STAND, throw), col=OTHER, d=-1)
        ctx.push_group()
        j = fig(ctx, x, G, S, pose)
        hero = ctx.pop_group()
        squash = 1 - (0.06 * math.exp(-6 * imp) * abs(math.cos(8 * imp)) if hit else 0)
        sway = 18 * math.sin(t * 3.1) + (26 * math.exp(-4 * imp) * math.sin(11 * imp) if hit else 0)
        boxes = STACK + ([LANDED] if hit else [])
        top = carried(ctx, j, boxes, sway=sway, squash=squash)
        ctx.set_source(hero); ctx.paint()
        if not hit:  # the incoming box, already mid-air at frame 0
            u = (t + 0.45) / (t_hit + 0.45)
            x0, y0 = 810, 1260
            tx, ty = top
            bx = lerp(x0, tx, u); by = lerp(y0, ty, u) - 4 * 300 * u * (1 - u)
            ctx.save(); ctx.translate(bx, by); ctx.rotate(-1.4 * (1 - u))
            box(ctx, 0, 0, LANDED[0], LANDED[1]); ctx.restore()
        else:
            dust(ctx, top[0], top[1] + LANDED[1] + 4, imp / 0.7)
            dust(ctx, x, G, imp / 0.8, spread=1.4)
        ctx.restore()
        if hit:
            ctx.set_source_rgba(1, 1, 1, 0.22 * math.exp(-9 * imp)); ctx.paint()
        cap(ctx, t, "He was already struggling.", "They handed him more.", 1.35)
    return Scene(draw, duration, "custom:box_slam_hook", "He was already struggling. / They handed him more.")


def s2_carry(duration=5.0):
    def draw(ctx, t):
        go = eio((t - 0.6) / 0.9)
        dist = 95 * max(0.0, t - 0.6 - 0.45)        # px walked (ground scrolls)
        floor(ctx, dist)
        up = eio(t / 1.0)
        ph = dist / 34
        pose = mix(mix(BUCKLE, CARRY, up), carry_walk(ph), go)
        for k, (ox, phase) in enumerate(((170, 1.3), (830, 2.6))):   # empty-handed companions
            p = mix(STAND, walk(ph + phase, stride=0.42), go)
            fig(ctx, ox, G, OS, pose_with(p, lean=0.04), col=OTHER)
        ctx.push_group()
        j = fig(ctx, HERO_X + tremble(t, 1.0), G, S, pose)
        hero = ctx.pop_group()
        carried(ctx, j, STACK + [LANDED], sway=14 * math.sin(t * 2.6))
        ctx.set_source(hero); ctx.paint()
        cap(ctx, t, "He carried everyone's burdens.", "He didn't want to disappoint them.", 2.3)
    return Scene(draw, duration, "custom:carry_for_all", "He carried everyone's burdens. / He didn't want to disappoint them.")


def s3_tip(duration=5.0):
    offer = (70, 56, 0)

    def draw(ctx, t):
        stop = eio(t / 0.9)
        dist = 95 * 0.9 * (1 - (1 - clamp(t / 0.9)) ** 2) * 0.5
        floor(ctx, dist)
        ph = dist / 34
        fig(ctx, 170, G, OS, mix(walk(ph + 1.3, 0.42), STAND, stop), col=OTHER)
        # a third stickman steps in holding out a box
        gx = lerp(980, 790, eio((t - 0.3) / 1.0))
        gp = mix(walk((980 - gx) / 34, 0.4), STAND, eio((t - 1.1) / 0.3))
        gp = pose_with(gp, ua_f=1.45, fa_f=1.55, ua_b=1.35, fa_b=1.5)
        gj = fig(ctx, gx, G, OS, gp, col=OTHER, d=-1)
        box(ctx, gj["hand_f"][0] - 22, gj["hand_f"][1] + 8, *offer[:2])
        reach = eio((t - 1.6) / 0.7)
        hp = mix(carry_walk(ph), CARRY, stop)
        hp = pose_with(hp, ua_f=lerp(0.90, 1.45, reach), fa_f=lerp(1.60, 1.45, reach), lean=lerp(0.1, -0.05, reach))
        tilt = 0.17 * eio((t - 2.0) / 2.2) + 0.035 * math.sin(t * 5.2) * ease((t - 2.0) / 0.5)
        ctx.push_group()
        j = fig(ctx, HERO_X + tremble(t, 1.0 + 1.5 * reach), G, S, hp)
        hero = ctx.pop_group()
        stack(ctx, j["hand_b"][0] + 70, j["hand_b"][1] + 6, STACK + [LANDED], tilt=tilt,
              sway=12 * math.sin(t * 2.4) + 60 * eio((t - 2.2) / 2.0))
        ctx.set_source(hero); ctx.paint()
        cap(ctx, t, "Every time someone asked,", "he said yes.", 2.2)
    return Scene(draw, duration, "custom:stack_tips", "Every time someone asked, / he said yes.")


def s4_wearing(duration=5.0):
    def draw(ctx, t):
        floor(ctx)
        u = t
        tilt = 0.17 * math.exp(-2.6 * u) * math.cos(6 * u)
        sway = 60 * math.exp(-2.4 * u) * math.cos(5 * u)
        look_hands = ease((t - 1.5) / 0.4) * (1 - ease((t - 2.9) / 0.4))
        look_self = ease((t - 3.1) / 0.4)
        comp = []
        for ox, d in ((170, 1), (810, -1)):
            comp.append(fig(ctx, ox, G, OS, pose_with(STAND, ua_f=0.55, fa_f=1.1, ua_b=0.45, fa_b=1.0),
                            col=OTHER, d=d))
        for cj in comp:  # their empty hands
            halo(ctx, cj["hand_f"][0], cj["hand_f"][1], 70, a=0.35 * look_hands)
        hp = pose_with(CARRY, lean=lerp(0.05, 0.30, look_self))
        ctx.push_group()
        j = fig(ctx, HERO_X + tremble(t, 2.0), G, S, hp)
        hero = ctx.pop_group()
        bx = j["hand_f"][0] + STACK[0][0] * 0.32
        if look_self > 0:
            halo(ctx, bx, G - 360, 330, a=0.16 * look_self)
        carried(ctx, j, STACK + [LANDED], tilt=tilt, sway=sway + 4 * math.sin(t * 13))
        ctx.set_source(hero); ctx.paint()
        cap(ctx, t, "But helping everyone", "was wearing him down.", 2.0)
    return Scene(draw, duration, "custom:empty_hands", "But helping everyone / was wearing him down.")


def s5_no(duration=6.0):
    offer = (70, 56, 0)

    def draw(ctx, t):
        floor(ctx)
        down = eio(t / 1.3)
        up = eio((t - 1.4) / 0.6)
        palm = eio((t - 2.7) / 0.4) * (1 - eio((t - 4.8) / 0.5))
        shake = 6 * math.sin(2 * math.pi * 2.6 * (t - 3.1)) * ease((t - 3.1) / 0.15) * (1 - ease((t - 4.0) / 0.2))
        hx = lerp(HERO_X, HERO_X - 10, up)
        hp = mix(mix(CARRY, SQUAT_CARRY, down), pose_with(STAND, lean=0.02), up)
        if palm > 0:
            hp = pose_with(hp, ua_f=lerp(hp["ua_f"], PALM["ua_f"], palm), fa_f=lerp(hp["fa_f"], PALM["fa_f"], palm))
        # giver comes from behind him, offers, then keeps it
        gx = lerp(-90, 170, eio((t - 1.6) / 1.0)) - 90 * eio((t - 4.3) / 0.9)
        walking = 1.6 < t < 2.6 or 4.3 < t < 5.2
        gp = walk(gx / 34, 0.4) if walking else STAND
        gp = pose_with(gp, ua_f=1.45, fa_f=1.55, ua_b=1.35, fa_b=1.5)
        gp = mix(gp, pose_with(CARRY), eio((t - 4.2) / 0.4))
        gj = fig(ctx, gx, G, OS, gp, col=OTHER)
        box(ctx, gj["hand_f"][0] + 22, gj["hand_f"][1] + 8, *offer[:2])
        d = 1 if t < 1.9 else -1     # he turns round to face them
        # the stack goes down to the floor and stays there
        ctx.push_group()
        j = fig(ctx, hx, G, S, hp, d=d, head_dx=shake)
        hero = ctx.pop_group()
        if up <= 0:
            jc = j
            bx = jc["hand_f"][0] + STACK[0][0] * 0.32
            by = lerp(min(jc["hand_f"][1], jc["hand_b"][1]) + 6, G, eio((t - 0.3) / 1.0))
        else:
            bx, by = S5_REST
        stack(ctx, bx, by, STACK + [LANDED])
        ctx.set_source(hero); ctx.paint()
        if palm > 0:
            halo(ctx, j["hand_f"][0], j["hand_f"][1], 60, a=0.3 * palm)
        cap(ctx, t, "This time, he said no.", "They could carry their own.", 3.3)
    return Scene(draw, duration, "custom:palm_no", "This time, he said no. / They could carry their own.")


def _rest_pos():
    ctx = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4))
    j = fig(ctx, HERO_X, G, S, SQUAT_CARRY)
    return (j["hand_f"][0] + STACK[0][0] * 0.32, G)


S5_REST = _rest_pos()
MINE = (52, 42, 0)


def s6_limit(duration=3.0):
    def draw(ctx, t):
        rise = eio(t / 0.7)
        go = eio((t - 0.7) / 0.5)
        dist = 110 * max(0.0, t - 0.9)
        floor(ctx, dist)
        ph = dist / 34
        for ox, boxes, phase in ((150, [(96, 64, 0), (88, 58, 5)], 1.0), (790, [(100, 66, 0), (92, 60, -4), (84, 56, 5)], 2.2)):
            p = mix(mix(SQUAT_CARRY, CARRY, rise), carry_walk(ph + phase, lean=0.08), go)
            ctx.push_group(); oj = fig(ctx, ox, G, OS, p, col=OTHER); other = ctx.pop_group()
            carried(ctx, oj, boxes, a=0.85)
            ctx.set_source(other); ctx.paint()
        hp = mix(mix(SQUAT_CARRY, pose_with(STAND, lean=0.0, **CARRY_ARMS), rise),
                 pose_with(walk(ph, 0.4), lean=0.02, **CARRY_ARMS), go)
        ctx.push_group(); j = fig(ctx, 470, G, S, hp); hero = ctx.pop_group()
        bx = j["hand_f"][0] + 8
        box(ctx, bx, min(j["hand_f"][1], j["hand_b"][1]) + 6, MINE[0], MINE[1], rim=accent(), glow=0.6 + 0.4 * rise)
        ctx.set_source(hero); ctx.paint()
        cap(ctx, t, "He still cared.", "He just needed a limit.", 1.2)
    return Scene(draw, duration, "custom:own_box", "He still cared. / He just needed a limit.")


def s7_message(duration=3.0):
    def draw(ctx, t):
        ctx.save()
        ctx.rectangle(0, 705, 1080, 1215); ctx.clip()
        camera(ctx, lerp(1.45, 1.8, eio(t / duration)), HERO_X + 30, G - 120)
        dist = 110 * (t + 2.1)
        floor(ctx, dist)
        ph = dist / 34
        hp = walk(ph, 0.42)
        hp = pose_with(hp, lean=0.0, ua_f=hp["ua_f"] * 0.6, fa_f=hp["fa_f"] * 0.5 + 0.1)
        halo(ctx, HERO_X, G - 110, 260, col=accent(), a=0.18)
        j = fig(ctx, HERO_X, G, S, hp)
        box(ctx, j["hand_f"][0] + 6, j["hand_f"][1] + 26, MINE[0] * 0.8, MINE[1] * 0.8, rim=accent(), glow=0.8)
        ctx.restore()
        words(ctx, "YOU CAN CARE", TEXT_Y1 - 10, 0.1, t, size=50, step=0.13, accent_words={"CARE"})
        words(ctx, "WITHOUT CARRYING EVERYTHING.", TEXT_Y2 + 6, 0.65, t, size=50, step=0.13)
    return Scene(draw, duration, "custom:relaxed_close", "YOU CAN CARE / WITHOUT CARRYING EVERYTHING.")


EPISODE = dict(
    title="You Can Care Without Carrying Everything",
    accent=GOLD,
    watermark="",
    fade_out=0.25, black=1 / 30, fade_in=0.3, end_fade=0.5,   # 3–6 s beats need quicker fades
    scenes=[s1_hook(), s2_carry(), s3_tip(), s4_wearing(), s5_no(), s6_limit(), s7_message()],
)
