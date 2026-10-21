"""YOU START TO BECOME STRONG — one continuous story told across 7 scenes.

A skinny stickman fails at the heavy bar, almost leaves, finds a tiny dumbbell, comes back
day after day, and finally lifts the same bar. Nobody cheers. He smiles.

All scenes are custom: a front-view lifting rig (2-bone IK, `build` 0 = skinny .. 1 = muscular),
a skinny side-view rig for walking / picking things up, barbells and dumbbells.

  python3 <skill>/scripts/engine.py episode.py --preview sheet.png
  python3 <skill>/scripts/engine.py episode.py --out short.mp4
"""
import math

import cairo
from engine import (GOLD, STAND, Scene, accent, caption, clamp, ease, eio, halo, label, lerp,
                    mix, polyline, rounded_rect, vgrad, walk, words)
from props import star

G, GB = 1420, 1220            # front floor (hero + his bar) / back floor (the strong lifters)
HERO_S, LIFT_S = 56, 60
LIFTER_COL = (0.5, 0.5, 0.5)
LEG, UA, FA = 0.62, 0.45, 0.43  # limb lengths (x torso); shorter arms than engine.figure so lifts travel
HERO_BAR = dict(half=165, R=44, n=4)


# ---------- rigs ----------
def ik(p0, target, a, b, pref):
    """Two-bone IK: returns (middle joint, end point). The middle joint bends toward `pref`."""
    dx, dy = target[0] - p0[0], target[1] - p0[1]
    d0 = math.hypot(dx, dy) or 1e-6
    d = clamp(d0, abs(a - b) + 1e-3, a + b - 1e-3)
    ux, uy = dx / d0, dy / d0
    ang = math.atan2(uy, ux)
    A = math.acos(clamp((a * a + d * d - b * b) / (2 * a * d), -1, 1))
    cands = [(p0[0] + a * math.cos(ang + sg * A), p0[1] + a * math.sin(ang + sg * A)) for sg in (1, -1)]
    mid = max(cands, key=lambda e: (e[0] - p0[0]) * pref[0] + (e[1] - p0[1]) * pref[1])
    return mid, (p0[0] + ux * d, p0[1] + uy * d)


def stand_h(s, feet=0.26):
    return math.sqrt((2 * LEG * s) ** 2 - (feet * s) ** 2) * 0.995


def shoulder_w(s, build):
    return lerp(0.07, 0.30, build) * s


def rig(x, ground, s, hip_h=None, feet=0.26, hands=None, build=0.0, nod=0.0, breath=0.0,
        elbow=(1, 0.4)):
    """Front-view figure joints. hands = [(lx, ly), (rx, ry)] targets, None = hanging."""
    hip_h = stand_h(s, feet) if hip_h is None else hip_h
    hip = (x, ground - hip_h)
    neck = (x, hip[1] - s - 0.05 * breath * s)
    sw = shoulder_w(s, build) + 0.03 * breath * s
    shy = neck[1] + 0.08 * s
    sh = [(x - sw, shy), (x + sw, shy)]
    r = lerp(0.29, 0.25, build) * s
    head = (x, neck[1] - 0.12 * s - r + nod * 0.18 * s)
    reach = (UA + FA) * s
    if hands is None:
        hands = [(sh[0][0] - 0.07 * s, shy + reach), (sh[1][0] + 0.07 * s, shy + reach)]
    arms = []
    for i, sd in enumerate((-1, 1)):
        el, hd = ik(sh[i], hands[i], UA * s, FA * s, (sd * elbow[0], elbow[1]))
        arms.append((sh[i], el, hd))
    hw = lerp(0.04, 0.10, build) * s
    legs = []
    for sd in (-1, 1):
        h0 = (x + sd * hw, hip[1])
        kn, ft = ik(h0, (x + sd * feet * s, ground), LEG * s, LEG * s, (sd, -0.2))
        legs.append((h0, kn, ft))
    return dict(s=s, hip=hip, neck=neck, sh=sh, head=head, r=r, arms=arms, legs=legs, build=build,
                hands=[a[2] for a in arms])


def draw_body(ctx, j, col=(1, 1, 1), a=1.0, smile=0.0):
    s, b = j["s"], j["build"]
    ctx.new_path()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgba(*col, a); ctx.set_line_width(lerp(0.13, 0.30, b) * s)
    for h0, kn, ft in j["legs"]:
        ctx.move_to(*h0); ctx.line_to(*kn); ctx.line_to(*ft)
    ctx.stroke()
    hip, neck, (shl, shr) = j["hip"], j["neck"], j["sh"]
    if b > 0.02:  # V-shaped torso
        hw = lerp(0.04, 0.10, b) * s
        polyline(ctx, [(shl[0] - 0.06 * s * b, shl[1] - 0.05 * s), (shr[0] + 0.06 * s * b, shr[1] - 0.05 * s),
                       (hip[0] + hw, hip[1]), (hip[0] - hw, hip[1])], close=True)
        ctx.fill()
    ctx.move_to(*hip); ctx.line_to(*neck); ctx.move_to(*shl); ctx.line_to(*shr); ctx.stroke()
    for sh, el, hd in j["arms"]:
        ctx.move_to(*sh); ctx.line_to(*el); ctx.line_to(*hd); ctx.stroke()
        if b > 0.02:  # delts + biceps
            ctx.arc(*sh, 0.14 * s * b, 0, 2 * math.pi); ctx.fill()
            ctx.arc(lerp(sh[0], el[0], 0.5), lerp(sh[1], el[1], 0.5), 0.12 * s * b, 0, 2 * math.pi); ctx.fill()
    hx, hy = j["head"]; r = j["r"]
    ctx.arc(hx, hy, r, 0, 2 * math.pi); ctx.fill()
    if smile > 0:  # happy closed eyes + smile, only ever seen in the final close-up
        ctx.set_source_rgba(0, 0, 0, a * ease(smile * 2)); ctx.set_line_width(0.11 * r)
        for sd in (-1, 1):
            ctx.new_path(); ctx.arc(hx + sd * 0.36 * r, hy - 0.08 * r, 0.17 * r, math.pi * 1.1, math.pi * 1.9)
            ctx.stroke()
        sp = 0.34 * ease(smile)
        ctx.new_path(); ctx.arc(hx, hy - 0.05 * r, 0.52 * r, math.pi * (0.5 - sp), math.pi * (0.5 + sp))
        ctx.stroke()


def side(ctx, x, ground, s, pose, col=(1, 1, 1), alpha=1.0, d=1):
    """Skinny side-view figure (engine.figure with this episode's proportions and thin limbs)."""
    T, L1, L2, A1, A2 = s, LEG * s, LEG * s, UA * s, FA * s
    r = 0.29 * s
    hy = ground - lerp(L1 + L2, 0.20 * s, pose["hip"])

    def seg(p, ang, L):
        return (p[0] + d * L * math.sin(ang), p[1] + L * math.cos(ang))

    ln = pose["lean"]
    ux, uy = d * math.sin(ln), -math.cos(ln)
    hip = (x, hy)
    neck = (x + ux * T, hy + uy * T)
    sh = (x + ux * T * 0.88, hy + uy * T * 0.88)
    head = (x + ux * (T + 0.12 * s + r), hy + uy * (T + 0.12 * s + r))
    ctx.new_path()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(0.13 * s)

    def limb(p0, a1, l1, a2, l2, shade):
        p1 = seg(p0, a1, l1); p2 = seg(p1, a2, l2)
        ctx.set_source_rgba(*(c * shade for c in col), alpha)
        ctx.move_to(*p0); ctx.line_to(*p1); ctx.line_to(*p2); ctx.stroke()
        return p2

    limb(sh, pose["ua_b"], A1, pose["fa_b"], A2, 0.5)
    limb(hip, pose["th_b"], L1, pose["sh_b"], L2, 0.5)
    ctx.set_source_rgba(*col, alpha); ctx.move_to(*hip); ctx.line_to(*neck); ctx.stroke()
    limb(hip, pose["th_f"], L1, pose["sh_f"], L2, 1.0)
    hand = limb(sh, pose["ua_f"], A1, pose["fa_f"], A2, 1.0)
    ctx.set_source_rgba(*col, alpha); ctx.arc(*head, r, 0, 2 * math.pi); ctx.fill()
    return dict(head=head, hand=hand, r=r)


REACH = dict(lean=1.1, th_f=1.45, sh_f=-0.35, th_b=1.35, sh_b=-0.5, ua_f=0.25, fa_f=0.1,
             ua_b=0.15, fa_b=0.05, hip=0.56)  # squatting, hand at the floor in front of the feet


def hold(curl, lean=0.05):
    p = dict(STAND); p.update(lean=lean, ua_f=0.12, fa_f=lerp(0.2, 2.75, curl))
    return p


def slump_walk(ph):
    p = walk(ph, stride=0.32); p["lean"] = 0.32
    return p


# ---------- equipment & set ----------
def barbell(ctx, cx, y, half, R, n, a=1.0, bend=0.0, rim=(0.78, 0.78, 0.78)):
    """Front view: bar with n plates per side (edge-on). y = bar height; rests on the floor at G - R."""
    pw, gap = max(8.0, R * 0.30), 3
    ctx.new_path(); ctx.move_to(cx - half, y)
    ctx.curve_to(cx - half * 0.3, y - bend * 1.33, cx + half * 0.3, y - bend * 1.33, cx + half, y)
    ctx.set_source_rgba(*rim, a); ctx.set_line_width(max(4, R * 0.10)); ctx.stroke()
    inner = half - 10 - n * (pw + gap)
    for sd in (-1, 1):
        ctx.rectangle(cx + sd * inner - 4, y - R * 0.18, 8, R * 0.36)
        ctx.set_source_rgba(*rim, a); ctx.fill()
        for k in range(n):
            rr = R * (1 - 0.07 * k)
            px = cx + sd * (inner + gap + k * (pw + gap) + pw / 2)
            rounded_rect(ctx, px - pw / 2, y - rr, pw, 2 * rr, pw * 0.3)
            ctx.set_source_rgba(0.14, 0.14, 0.14, a); ctx.fill_preserve()
            ctx.set_source_rgba(*rim, a); ctx.set_line_width(2.5); ctx.stroke()


def dumbbell(ctx, x, y, s=1.0, a=1.0, rim=(0.82, 0.82, 0.82)):
    ctx.new_path(); ctx.set_source_rgba(*rim, a); ctx.set_line_width(4 * s)
    ctx.move_to(x - 16 * s, y); ctx.line_to(x + 16 * s, y); ctx.stroke()
    for sd in (-1, 1):
        for k, h in enumerate((24, 17)):
            px = x + sd * (16 * s + k * 7 * s + 3 * s)
            rounded_rect(ctx, px - 3 * s, y - h * s / 2, 6 * s, h * s, 2 * s)
            ctx.set_source_rgba(0.2, 0.2, 0.2, a); ctx.fill_preserve()
            ctx.set_source_rgba(*rim, a); ctx.set_line_width(2); ctx.stroke()


def lamp(ctx, x, floor, a=1.0, col=(1, 0.95, 0.85), cone=0.10, y=790):
    ctx.new_path(); ctx.set_source_rgba(0.3, 0.3, 0.3, a); ctx.set_line_width(2)
    ctx.move_to(x, 705); ctx.line_to(x, y); ctx.stroke()
    polyline(ctx, [(x - 16, y), (x + 16, y), (x + 40, y + 30), (x - 40, y + 30)], close=True)
    ctx.set_source_rgba(0.32, 0.32, 0.32, a); ctx.fill()
    polyline(ctx, [(x - 34, y + 30), (x + 34, y + 30), (x + 200, floor), (x - 200, floor)], close=True)
    ctx.set_source(vgrad(y + 30, floor, (*col, cone * a), (*col, 0.02 * a))); ctx.fill()
    halo(ctx, x, y + 32, 60, col=col, a=0.35 * a)
    ctx.new_path(); ctx.save(); ctx.translate(x, floor); ctx.scale(1, 0.12); ctx.arc(0, 0, 210, 0, 2 * math.pi)
    ctx.restore(); ctx.set_source_rgba(*col, 0.08 * a); ctx.fill()


def gym(ctx, t, lift_a=1.0, lift_col=LIFTER_COL, centre_col=(1, 0.95, 0.85), centre_cone=0.10):
    lamp(ctx, 215, GB, cone=0.07)
    lamp(ctx, 865, GB, cone=0.07)
    lamp(ctx, 540, G, col=centre_col, cone=centre_cone)
    ctx.new_path(); ctx.set_line_width(2); ctx.set_source_rgba(0.22, 0.22, 0.22, 1)
    ctx.move_to(20, GB + 2); ctx.line_to(1060, GB + 2); ctx.stroke()
    rounded_rect(ctx, 24, 1262, 92, 38, 6); ctx.set_source_rgba(0.45, 0.45, 0.45, 1)
    ctx.set_line_width(2); ctx.stroke()
    label(ctx, "EXIT", 70, 1289, 0.7, size=20, col=(0.75, 0.75, 0.75), bold=True)
    if lift_a > 0:
        presser(ctx, 215, t, lift_a, lift_col)
        squatter(ctx, 865, t, lift_a, lift_col)
    ctx.new_path(); ctx.set_line_width(3); ctx.set_source_rgba(0.4, 0.4, 0.4, 1)
    ctx.move_to(0, G + 2); ctx.line_to(1080, G + 2); ctx.stroke()


def presser(ctx, x, t, a, col, period=2.3):
    """Muscular lifter, overhead press with a big bar — smooth, effortless reps."""
    s = LIFT_S
    k = eio(0.5 - 0.5 * math.cos(2 * math.pi * t / period))
    sw = shoulder_w(s, 1)
    shy = GB - stand_h(s) - s + 0.08 * s
    y = lerp(shy - 0.04 * s, shy - 0.78 * s, k)
    j = rig(x, GB, s, build=1, hands=[(x - sw - 0.3 * s, y), (x + sw + 0.3 * s, y)], elbow=(1, 0.6))
    by = (j["hands"][0][1] + j["hands"][1][1]) / 2
    barbell(ctx, x, by, 175, 46, 4, a=a, rim=tuple(c * 1.4 for c in col))
    draw_body(ctx, j, col, a)


def squatter(ctx, x, t, a, col, period=2.7):
    """Muscular lifter squatting a bigger bar on his shoulders."""
    s, feet = LIFT_S, 0.40
    k = eio(0.5 - 0.5 * math.cos(2 * math.pi * (t / period + 0.35)))
    hip_h = lerp(stand_h(s, feet), 0.62 * stand_h(s, feet), k)
    sw = shoulder_w(s, 1)
    shy = GB - hip_h - s + 0.08 * s
    j = rig(x, GB, s, hip_h=hip_h, feet=feet, build=1,
            hands=[(x - sw - 0.36 * s, shy + 0.02 * s), (x + sw + 0.36 * s, shy + 0.02 * s)], elbow=(0.5, 1))
    barbell(ctx, x, shy - 0.05 * s, 180, 50, 5, a=a, rim=tuple(c * 1.4 for c in col))
    draw_body(ctx, j, col, a)


def dl_hip(s, bar_y, grip, build, feet=0.30):
    """Hip height that lets hands at +-grip reach bar_y (deadlift), capped at standing."""
    hx = grip - shoulder_w(s, build)
    dv = math.sqrt(max((0.96 * (UA + FA) * s) ** 2 - hx ** 2, 1))
    return min(G - (bar_y - dv + s - 0.08 * s), stand_h(s, feet))


def dl_top(s, grip, build, feet=0.30):
    hx = grip - shoulder_w(s, build)
    dv = math.sqrt(max((0.96 * (UA + FA) * s) ** 2 - hx ** 2, 1))
    return G - stand_h(s, feet) - s + 0.08 * s + dv


def hero_lift(ctx, x, s, bar_y, bend, k_grip, build, nod=0.0, breath=0.0, col=(1, 1, 1),
              bar=HERO_BAR, rim=(0.78, 0.78, 0.78), smile=0.0, shake=0.0):
    """Hero in front view at the bar: k_grip 0 = standing, hands hanging; 1 = gripping at bar_y."""
    feet = 0.30
    grip = shoulder_w(s, build) + 0.30 * s
    hip_g = dl_hip(s, bar_y, grip, build, feet)
    j0 = rig(x, G, s, feet=feet, build=build)
    hip_h = lerp(stand_h(s, feet), hip_g, k_grip)
    hands = [(lerp(j0["hands"][i][0], x + sd * grip, k_grip), lerp(j0["hands"][i][1], bar_y - bend, k_grip))
             for i, sd in enumerate((-1, 1))]
    j = rig(x + shake, G, s, hip_h=hip_h, feet=feet, hands=hands, build=build, nod=nod, breath=breath)
    draw_body(ctx, j, col, smile=smile)
    barbell(ctx, x, bar_y, bar["half"], bar["R"], bar["n"], bend=bend, rim=rim)
    return j


# ---------- small effects ----------
def cam(ctx, z, wx, wy, sx=540, sy=1250):
    """World point (wx, wy) appears at screen (sx, sy), zoomed by z. Clips to below the captions."""
    ctx.rectangle(0, 705, 1080, 1215); ctx.clip()
    ctx.translate(sx, sy); ctx.scale(z, z); ctx.translate(-wx, -wy)


def cap(ctx, t, l1, l2, t2, a=1.0, accent_words=()):
    if a <= 0 or t < 0:
        return
    ctx.push_group(); caption(ctx, t, l1, l2, t2=t2, accent_words=accent_words)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)


def strain(ctx, head, r, a, t):
    if a <= 0:
        return
    ctx.new_path(); ctx.set_line_width(3)
    for sd in (-1, 1):
        for k, ang in enumerate((-0.25, 0.25, 0.75)):
            fl = 0.5 + 0.5 * math.sin(t * 14 + k * 2.1 + sd)
            dx, dy = sd * math.cos(ang), -math.sin(ang)
            ctx.set_source_rgba(0.85, 0.85, 0.85, a * (0.3 + 0.7 * fl))
            ctx.move_to(head[0] + dx * (r + 7), head[1] + dy * (r + 7))
            ctx.line_to(head[0] + dx * (r + 19 + 5 * fl), head[1] + dy * (r + 19 + 5 * fl)); ctx.stroke()


def sweat(ctx, head, r, t, t0, sd):
    u = t - t0
    if not 0 <= u <= 0.7:
        return
    x = head[0] + sd * (r + 4 + 70 * u)
    y = head[1] - 0.3 * r - 90 * u + 380 * u * u
    a = 1 - ease((u - 0.45) / 0.25)
    ctx.new_path(); ctx.move_to(x, y - 9)
    ctx.curve_to(x + 6, y - 1, x + 5, y + 5, x, y + 5); ctx.curve_to(x - 5, y + 5, x - 6, y - 1, x, y - 9)
    ctx.set_source_rgba(0.75, 0.85, 0.95, 0.85 * a); ctx.fill()


def dust(ctx, x, y, k):
    if not 0 < k < 1:
        return
    for sd in (-1, 1):
        for i in range(3):
            ctx.new_path()
            ctx.arc(x + sd * (10 + 28 * k + 12 * i), y - 4 - 10 * k * i, 4 + 10 * k, 0, 2 * math.pi)
            ctx.set_source_rgba(0.6, 0.6, 0.6, 0.35 * (1 - k)); ctx.fill()


def _probe_reach():
    """Where the hand lands (relative to x, ground) in the REACH pose facing left."""
    ctx = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4))
    j = side(ctx, 0, 0, HERO_S, REACH, d=-1)
    return j["hand"]


REACH_HAND = _probe_reach()


# ---------- scenes ----------
def s1_enter(duration=6.5):
    x0, x1 = -40, 540

    def draw(ctx, t):
        lit = ease((t - 3.0) / 0.8)
        gym(ctx, t, lift_col=tuple(c + 0.2 * lit for c in LIFTER_COL))
        if lit > 0:
            halo(ctx, 215, GB - 120, 230, a=0.10 * lit); halo(ctx, 865, GB - 110, 230, a=0.10 * lit)
        p = clamp(t / 3.6)
        x = lerp(x0, x1, p)
        turn = ease((t - 3.6) / 0.35)
        if turn < 1:
            side(ctx, x, G, HERO_S, walk((x - x0) / 30, stride=0.40) if p < 1 else STAND, alpha=1 - turn)
        if turn > 0:
            j = rig(x1, G, HERO_S, feet=0.30, nod=0.5 * ease((t - 4.3) / 0.6))
            draw_body(ctx, j, a=turn)
        barbell(ctx, 540, G - HERO_BAR["R"], HERO_BAR["half"], HERO_BAR["R"], HERO_BAR["n"])
        caption(ctx, t, "A skinny guy walked into the gym.", "Everyone was stronger.", t2=3.0)
    return Scene(draw, duration, "custom:gym_enter", "A skinny guy walked into the gym. / Everyone was stronger.")


def s2_attempt(duration=6.5):
    R = HERO_BAR["R"]

    def draw(ctx, t):
        ctx.save()
        cam(ctx, lerp(1.30, 1.45, eio(t / duration)), 540, G - 80)
        gym(ctx, t)
        k = eio((t - 0.9) / 0.8) * (1 - eio((t - 4.4) / 0.8))
        st = ease((t - 1.7) / 0.3) * (1 - ease((t - 4.2) / 0.25))
        bend = st * (3.5 + 1.5 * math.sin(t * 9))
        j = hero_lift(ctx, 540, HERO_S, G - R, bend, k, 0.0, nod=ease((t - 5.1) / 0.6),
                      shake=1.6 * st * math.sin(t * 55))
        strain(ctx, j["head"], j["r"], st, t)
        sweat(ctx, j["head"], j["r"], t, 2.5, 1); sweat(ctx, j["head"], j["r"], t, 3.3, -1)
        ctx.restore()
        caption(ctx, t, "He tried the heavy bar.", "It didn't move.", t2=3.3)
    return Scene(draw, duration, "custom:bar_wont_move", "He tried the heavy bar. / It didn't move.")


def s3_others(duration=6.5):
    x0, x1 = 540, 300

    def draw(ctx, t):
        lit = ease(t / 0.6) * (1 - ease((t - 3.4) / 0.8))
        gym(ctx, t, lift_col=tuple(c + 0.32 * lit for c in LIFTER_COL))
        if lit > 0:
            halo(ctx, 215, GB - 130, 260, a=0.16 * lit); halo(ctx, 865, GB - 120, 260, a=0.16 * lit)
        turn = ease((t - 2.8) / 0.35)
        p = clamp((t - 3.0) / 3.2)
        x = lerp(x0, x1, p)
        if turn < 1:
            draw_body(ctx, rig(x0, G, HERO_S, feet=0.30, nod=1.0), col=(0.9, 0.9, 0.9), a=1 - turn)
        if turn > 0:
            side(ctx, x, G, HERO_S, slump_walk((x0 - x) / 26), col=(0.9, 0.9, 0.9), alpha=turn, d=-1)
        barbell(ctx, 540, G - HERO_BAR["R"], HERO_BAR["half"], HERO_BAR["R"], HERO_BAR["n"])
        caption(ctx, t, "They made it look effortless.", "He headed for the exit.", t2=3.0)
    return Scene(draw, duration, "custom:effortless_others", "They made it look effortless. / He headed for the exit.")


def s4_tiny(duration=7.0):
    db_x, db_s = 175, 0.7
    x_stop = db_x - REACH_HAND[0]
    rest_y = G - 12 * db_s

    def draw(ctx, t):
        ctx.save()
        cam(ctx, 1.75, 235, G - 85, 540, 1190)
        gym(ctx, t, lift_a=0.6)
        p = eio(t / 1.4)
        x = lerp(330, x_stop, p)
        if t < 1.4:
            pose = slump_walk((330 - x) / 26)
        else:
            look = dict(STAND); look["lean"] = lerp(0.32, 0.5, ease((t - 1.4) / 0.4))
            crouch = eio((t - 2.0) / 0.7)
            rise = eio((t - 2.85) / 0.6)
            pose = mix(mix(look, REACH, crouch), hold(0.0, lean=0.1), rise)
            reps = clamp((t - 3.6) / 2.6) * 3
            if t > 3.6 and reps < 3:
                pose = hold(math.sin(math.pi * (reps % 1)) ** 2, lean=0.1)
        j = side(ctx, x, G, HERO_S, pose, d=-1)
        glint = ease((t - 0.4) / 0.4) * (1 - ease((t - 2.4) / 0.4))
        if t < 2.7:
            halo(ctx, db_x, rest_y, 70, a=0.25 * glint)
            star(ctx, db_x + 18, rest_y - 14, 8 * (0.6 + 0.4 * math.sin(t * 6)), a=0.9 * glint, rot=t)
            dumbbell(ctx, db_x, rest_y, db_s)
        else:
            dumbbell(ctx, j["hand"][0], j["hand"][1], db_s)
        ctx.restore()
        caption(ctx, t, "Then he noticed a tiny dumbbell.", "Almost embarrassingly easy.", t2=3.9)
    return Scene(draw, duration, "custom:tiny_dumbbell", "Then he noticed a tiny dumbbell. / Almost embarrassingly easy.")


MONTAGE = [  # (day, lift, build, weight)
    ("DAY 1", "curl1", 0.00, 0.7),
    ("DAY 8", "curl2", 0.06, 1.2),
    ("DAY 19", "press", 0.12, dict(half=120, R=22, n=1)),
    ("DAY 34", "dead", 0.19, dict(half=140, R=30, n=2)),
    ("DAY 52", "dead", 0.26, dict(half=155, R=38, n=3)),
]
STAGE = 2.0


def montage_frame(ctx, lift, build, wt, u):
    s, x = HERO_S, 540
    j0 = rig(x, G, s, feet=0.30, build=build)
    (shl, shr), hang = j0["sh"], j0["hands"]
    shy = shl[1]
    if lift in ("curl1", "curl2"):
        hands = []
        for i, sd in enumerate((-1, 1)):
            ph = (u - 0.25) / 0.65 + (0.5 if (lift == "curl2" and i == 0) else 0)
            k = math.sin(math.pi * ph) ** 2 if (u > 0.25 and (lift == "curl2" or i == 1)) else 0.0
            hands.append((lerp(hang[i][0], j0["sh"][i][0] + sd * 0.12 * s, k), lerp(hang[i][1], shy + 0.06 * s, k)))
        j = rig(x, G, s, feet=0.30, hands=hands, build=build, elbow=(0.3, 1))
        draw_body(ctx, j)
        for i in ((0, 1) if lift == "curl2" else (1,)):
            dumbbell(ctx, *j["hands"][i], wt)
    elif lift == "press":
        k = math.sin(math.pi * clamp((u - 0.25) / 1.4)) ** 2
        g = shoulder_w(s, build) + 0.30 * s
        y = lerp(shy - 0.02 * s, shy - 0.80 * s, k)
        j = rig(x, G, s, feet=0.30, hands=[(x - g, y), (x + g, y)], build=build, elbow=(1, 0.6))
        barbell(ctx, x, j["hands"][0][1], wt["half"], wt["R"], wt["n"])
        draw_body(ctx, j)
    else:
        g = shoulder_w(s, build) + 0.30 * s
        k = math.sin(math.pi * clamp((u - 0.25) / 1.45)) ** 2
        bar_y = lerp(G - wt["R"], dl_top(s, g, build), k)
        hero_lift(ctx, x, s, bar_y, 0, ease((u - 0.05) / 0.2), build, bar=wt)


def s5_montage():
    duration = STAGE * len(MONTAGE) + 0.4

    def draw(ctx, t):
        i = min(int(t / STAGE), len(MONTAGE) - 1)
        u = t - i * STAGE
        day, lift, build, wt = MONTAGE[i]
        blink = (1 if i == 0 else ease(u / 0.22)) * (1 if i == len(MONTAGE) - 1 else ease((STAGE - u) / 0.22))
        ctx.push_group()
        ctx.save()
        cam(ctx, 1.3, 540, G - 90, 540, 1270)
        gym(ctx, t, lift_a=0.35)
        montage_frame(ctx, lift, build, wt, u)
        ctx.restore()
        label(ctx, day, 540, 830, 0.9, size=44, col=(0.92, 0.92, 0.92), bold=True)
        for k in range(len(MONTAGE)):  # progress dots
            ctx.new_path(); ctx.arc(540 + (k - 2) * 26, 868, 5, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, 0.85 if k <= i else 0.2); ctx.fill()
        ctx.pop_group_to_source(); ctx.paint_with_alpha(blink)
        caption(ctx, t, "So he came back.", "A little heavier every time.", t2=2.0)
    return Scene(draw, duration, "custom:days_montage", "So he came back. / A little heavier every time.")


def s6_lift(duration=12.5):
    R, s, build = HERO_BAR["R"], HERO_S, 0.32
    grip = shoulder_w(s, build) + 0.30 * s
    top = dl_top(s, grip, build)
    head_rest = rig(540, G, s, feet=0.30, build=build)["head"]

    def draw(ctx, t):
        gold = ease((t - 6.4) / 0.9)
        push = eio((t - 8.4) / 2.0)
        ctx.save()
        cam(ctx, lerp(1.35, 2.6, push), 540, lerp(G - 80, head_rest[1] + 20, push), 540, lerp(1250, 1120, push))
        gym(ctx, t, centre_col=tuple(lerp(c, a, gold) for c, a in zip((1, 0.95, 0.85), accent())),
            centre_cone=lerp(0.10, 0.16, gold))
        halo(ctx, 540, G - 130, 300, col=accent(), a=0.22 * gold)
        k = eio((t - 0.9) / 0.8)
        breath = math.sin(math.pi * clamp((t - 1.8) / 1.3))
        q = eio((t - 3.3) / 3.3)
        bar_y = lerp(G - R, top, q)
        lifting = 3.3 < t < 6.6
        shake = 1.2 * (1 - q) * math.sin(t * 50) if lifting else 0.0
        bend = 2.5 * (1 - q) if lifting else 0.0
        rim = tuple(lerp(c, a, gold) for c, a in zip((0.78, 0.78, 0.78), accent()))
        j = hero_lift(ctx, 540, s, bar_y, bend, k, build, nod=0.25 * (1 - k), breath=breath,
                      rim=rim, smile=ease((t - 9.6) / 0.9), shake=shake)
        strain(ctx, j["head"], j["r"], 0.6 * (1 - q) * ease((t - 3.4) / 0.3) if lifting else 0, t)
        for sd in (-1, 1):
            dust(ctx, 540 + sd * (HERO_BAR["half"] - 30), G, (t - 3.6) / 1.1)
        ctx.restore()
        cap(ctx, t, "The same bar.", "One deep breath.", 1.9, a=1 - ease((t - 3.4) / 0.5))
        cap(ctx, t - 7.4, "Nobody cheered.", "He simply smiled.", 2.6)
    return Scene(draw, duration, "custom:same_bar_lift", "The same bar. One deep breath. / Nobody cheered. He simply smiled.")


def s7_message(duration=7.5):
    def draw(ctx, t):
        words(ctx, "YOU DON'T HAVE TO", 880, 0.2, t, size=52, step=0.14)
        words(ctx, "BE STRONG TO START.", 950, 0.75, t, size=52, step=0.14)
        words(ctx, "YOU START TO", 1090, 2.4, t, size=52, step=0.14)
        words(ctx, "BECOME STRONG.", 1160, 2.85, t, size=52, step=0.18, accent_words={"BECOME", "STRONG."})
        a = ease((t - 3.8) / 0.8)
        if a > 0:
            halo(ctx, 540, 1330, 120, col=accent(), a=0.3 * a)
            dumbbell(ctx, 540, 1330, 1.1, a=a, rim=accent())
    return Scene(draw, duration, "custom:final_message",
                 "YOU DON'T HAVE TO BE STRONG TO START. / YOU START TO BECOME STRONG.")


EPISODE = dict(
    title="You Start To Become Strong",
    accent=GOLD,
    watermark="",
    scenes=[s1_enter(), s2_attempt(), s3_others(), s4_tiny(), s5_montage(), s6_lift(), s7_message()],
)
