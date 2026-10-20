"""storykit — building blocks for story-driven stick-figure Shorts (one character, one arc).

Import in an episode file:  from storykit import *
Everything here draws in WORLD coordinates; wrap world drawing in ctx.save() / cam(...) / ctx.restore()
and draw captions afterwards in screen space.

Sections: poses · side-view figure · front-view lifting rig · objects · environments · effects ·
camera & darkness · captions.  See references/api.md for a one-page summary.
"""
import math
import random

import cairo
from engine import (CARRY, CROUCH, GOLD, SIT, SIT_CHAIR, STAND, TEXT_Y1, TEXT_Y2, accent, caption, clamp,  # noqa: F401
                    ease, eio, halo, label, lerp, mix, polyline, rounded_rect, run, vgrad, walk, words)

G = 1400                     # default ground line
GREY = (0.55, 0.55, 0.55)    # secondary characters
RIM = (0.72, 0.72, 0.72)     # outlines of objects

# ---------------------------------------------------------------- poses (side view, engine format)
# Angles: radians from straight down, + = toward facing direction. hip: 0 standing .. 1 on the floor.
# Leg angles and hip are kept consistent so feet stay on the ground.
TIRED = dict(STAND, lean=0.14)
BUCKLE = dict(lean=0.30, th_f=0.60, sh_f=-0.50, th_b=0.30, sh_b=-0.65,
              ua_f=0.90, fa_f=1.60, ua_b=0.80, fa_b=1.50, hip=0.18)          # knees giving way under load
SQUAT_CARRY = dict(lean=0.45, th_f=1.10, sh_f=-0.30, th_b=0.90, sh_b=-0.40,
                   ua_f=1.20, fa_f=1.30, ua_b=1.10, fa_b=1.20, hip=0.35)     # setting a load down
REACH_FLOOR = dict(lean=1.10, th_f=1.45, sh_f=-0.35, th_b=1.35, sh_b=-0.50,
                   ua_f=0.25, fa_f=0.10, ua_b=0.15, fa_b=0.05, hip=0.56)     # hand at the floor in front
FALL = dict(lean=0.95, th_f=0.85, sh_f=-0.25, th_b=-0.35, sh_b=-0.95,
            ua_f=1.55, fa_f=1.25, ua_b=1.25, fa_b=1.0, hip=0.33)             # mid-stumble
HANDS_DOWN = dict(lean=0.95, th_f=0.15, sh_f=-1.45, th_b=0.05, sh_b=-1.50,
                  ua_f=0.25, fa_f=-0.05, ua_b=0.20, fa_b=-0.10, hip=0.61)    # knees + palms on the ground
KNEEL_UP = dict(lean=0.12, th_f=0.05, sh_f=-1.50, th_b=-0.02, sh_b=-1.55,
                ua_f=0.15, fa_f=0.25, ua_b=0.05, fa_b=0.15, hip=0.61)        # upright on both knees
ONE_KNEE = dict(lean=0.55, th_f=1.35, sh_f=-0.10, th_b=0.05, sh_b=-1.50,
                ua_f=0.70, fa_f=0.40, ua_b=0.50, fa_b=0.30, hip=0.61)
HALF_UP = dict(lean=0.42, th_f=0.75, sh_f=-0.35, th_b=0.45, sh_b=-0.55,
               ua_f=0.70, fa_f=0.90, ua_b=0.60, fa_b=0.80, hip=0.20)         # bent over, hands near knees
SIT_UP = dict(SIT, lean=0.12)
SIT_DOWN = dict(SIT, lean=0.85, ua_f=0.75, fa_f=0.45, ua_b=0.65, fa_b=0.35)  # head down, defeated
LOOK_HANDS = dict(SIT, lean=0.40, ua_f=1.00, fa_f=2.30, ua_b=0.90, fa_b=2.20)
SLUMP_SIT = dict(SIT_CHAIR, lean=0.48, ua_f=0.55, fa_f=0.95, ua_b=0.45, fa_b=0.85)  # on a bench, hunched
REST_SIT = dict(SIT_CHAIR, lean=-0.06, ua_f=0.25, fa_f=1.25, ua_b=0.15, fa_b=1.15)  # on a bench, relaxed
# arm sets — merge with pose_with(p, **ARMS)
CARRY_ARMS = dict(ua_f=0.90, fa_f=1.60, ua_b=0.80, fa_b=1.50)   # stack resting on forearms
HUG_ARMS = dict(ua_f=0.55, fa_f=1.20, ua_b=0.45, fa_b=1.10)     # parcels hugged to the chest
HOLD_OUT = dict(ua_f=1.45, fa_f=1.55, ua_b=1.35, fa_b=1.50)     # offering something
POINT = dict(ua_f=1.60, fa_f=1.62)
PALM_UP = dict(ua_f=1.35, fa_f=2.70)                            # "no" / stop
THROWN = dict(ua_f=2.30, fa_f=2.60, ua_b=2.10, fa_b=2.40)


def pose_with(p, **kw):
    q = dict(p); q.update(kw)
    return q


def struggle_run(ph, lean=0.30):
    return pose_with(mix(walk(ph, 0.5), run(ph), 0.55), lean=lean)


def carry_walk(ph, lean=0.12, arms=CARRY_ARMS):
    return pose_with(walk(ph, stride=0.38), lean=lean, **arms)


def slump_walk(ph):
    return pose_with(walk(ph, stride=0.32), lean=0.32)


def hold_curl(curl, lean=0.05):
    """Standing, front forearm curling 0..1 (dumbbell curl in side view)."""
    return pose_with(STAND, lean=lean, ua_f=0.12, fa_f=lerp(0.2, 2.75, curl))


def steps(t, starts, dur=0.6, stride=60.0):
    """Discrete footsteps: returns (distance walked, walk phase). Each step k runs starts[k]..+dur and
    moves `stride` px; footfalls land at starts[k] + dur (put a kick there in the score)."""
    dist, ph = 0.0, 0.0
    for k, st in enumerate(starts):
        u = eio((t - st) / dur)
        dist += stride * u
        ph = math.pi * (k + u) if t >= st else ph
    return dist, ph


# ---------------------------------------------------------------- side-view figure
def fig(ctx, x, ground, s, pose, col=(1, 1, 1), a=1.0, d=1, lw=0.22, head_dx=0.0, knee_shake=0.0,
        hand_shake=0.0, face=None):
    """Side-view pictogram (engine.figure proportions) with extras:
    lw         limb thickness × s (0.13 skinny, 0.22 normal)
    head_dx    move the head sideways (head shake, peeking out from behind something)
    knee_shake / hand_shake  px of tremble at knees / hands
    face       None | 'strain' | 'closed' | 'open' | 'wide' | 'smile'  (only reads at zoom ≥ ~1.6)
    Returns joints: head, hand_f, hand_b, knees, hip, r."""
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
    ctx.set_line_width(lw * s)

    def limb(p0, a1, l1, a2, l2, shade, jx=0.0, jy=0.0):
        p1 = seg(p0, a1, l1); p1 = (p1[0] + jx, p1[1])
        p2 = seg(p1, a2, l2); p2 = (p2[0] + jx * 0.5, p2[1] + jy)
        ctx.set_source_rgba(*(c * shade for c in col), a)
        ctx.move_to(*p0); ctx.line_to(*p1); ctx.line_to(*p2); ctx.stroke()
        return p1, p2

    _, hand_b = limb(sh, pose["ua_b"], A1, pose["fa_b"], A2, 0.5, hand_shake * 0.7, -hand_shake)
    knee_b, _ = limb(hip, pose["th_b"], L1, pose["sh_b"], L2, 0.5, -knee_shake)
    ctx.set_source_rgba(*col, a); ctx.move_to(*hip); ctx.line_to(*neck); ctx.stroke()
    knee_f, _ = limb(hip, pose["th_f"], L1, pose["sh_f"], L2, 1.0, knee_shake)
    _, hand_f = limb(sh, pose["ua_f"], A1, pose["fa_f"], A2, 1.0, -hand_shake, hand_shake * 0.8)
    ctx.set_source_rgba(*col, a); ctx.arc(*head, r, 0, 2 * math.pi); ctx.fill()
    if face:
        side_face(ctx, head, r, d, face, a)
    return dict(head=head, hand_f=hand_f, hand_b=hand_b, knees=(knee_f, knee_b), hip=hip, r=r)


def side_face(ctx, head, r, d, face, a=1.0):
    ex, ey = head[0] + d * 0.42 * r, head[1] - 0.12 * r
    mx, my = head[0] + d * 0.50 * r, head[1] + 0.40 * r
    ctx.set_source_rgba(0, 0, 0, a); ctx.set_line_width(0.12 * r); ctx.new_path()
    if face == "strain":
        ctx.move_to(ex - d * 0.16 * r, ey - 0.14 * r); ctx.line_to(ex + d * 0.06 * r, ey)
        ctx.line_to(ex - d * 0.16 * r, ey + 0.14 * r); ctx.stroke()
        ctx.arc(mx + d * 0.05 * r, my, 0.12 * r, 0, 2 * math.pi); ctx.fill()
    elif face == "closed":
        ctx.arc(ex, ey - 0.05 * r, 0.15 * r, 0.15 * math.pi, 0.85 * math.pi); ctx.stroke()
    elif face in ("open", "wide", "smile"):
        ctx.arc(ex, ey, (0.14 if face == "wide" else 0.09) * r, 0, 2 * math.pi); ctx.fill()
        if face == "wide":
            ctx.arc(mx + d * 0.05 * r, my + 0.05 * r, 0.10 * r, 0, 2 * math.pi); ctx.stroke()
        elif face == "smile":
            ctx.new_path(); ctx.arc(mx - d * 0.05 * r, my - 0.12 * r, 0.22 * r, 0.15 * math.pi, 0.85 * math.pi)
            ctx.stroke()


def front_face(ctx, head, r, smile=1.0, a=1.0):
    """Happy closed eyes + smile on a FRONT-view head; smile 0..1 draws it in."""
    if smile <= 0:
        return
    hx, hy = head
    ctx.set_source_rgba(0, 0, 0, a * ease(smile * 2)); ctx.set_line_width(0.11 * r)
    for sd in (-1, 1):
        ctx.new_path(); ctx.arc(hx + sd * 0.36 * r, hy - 0.08 * r, 0.17 * r, math.pi * 1.1, math.pi * 1.9)
        ctx.stroke()
    sp = 0.34 * ease(smile)
    ctx.new_path(); ctx.arc(hx, hy - 0.05 * r, 0.52 * r, math.pi * (0.5 - sp), math.pi * (0.5 + sp)); ctx.stroke()


def probe(fn, *args, **kw):
    """Run a drawing function on a throwaway surface and return its result (e.g. joint positions),
    so a prop can be placed exactly where a hand will be in a given pose."""
    ctx = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4))
    return fn(ctx, *args, **kw)


def layered(ctx, draw_fig, draw_props):
    """Draw props BEHIND a figure whose joints they need: the figure goes into a group first,
    props are drawn using its joints, then the figure is painted on top. Returns (joints, props_result)."""
    ctx.push_group(); j = draw_fig(); fg = ctx.pop_group()
    out = draw_props(j)
    ctx.set_source(fg); ctx.paint()
    return j, out


# ---------------------------------------------------------------- front-view lifting rig
LEG, UA, FA = 0.62, 0.45, 0.43   # front rig proportions (shorter arms so lifts travel)


def ik(p0, target, a, b, pref):
    """Two-bone IK: (middle joint, end point); the middle joint bends toward vector `pref`."""
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


def rig(x, ground, s, hip_h=None, feet=0.26, hands=None, build=0.0, nod=0.0, breath=0.0, elbow=(1, 0.4)):
    """Front-view joints. build 0 = skinny .. 1 = muscular. hands = [(lx,ly),(rx,ry)] targets or None
    (hanging). Lower hip_h for squats / deadlift starts; feet stay planted via IK."""
    hip_h = stand_h(s, feet) if hip_h is None else hip_h
    hip = (x, ground - hip_h)
    neck = (x, hip[1] - s - 0.05 * breath * s)
    sw = shoulder_w(s, build) + 0.03 * breath * s
    shy = neck[1] + 0.08 * s
    shs = [(x - sw, shy), (x + sw, shy)]
    r = lerp(0.29, 0.25, build) * s
    head = (x, neck[1] - 0.12 * s - r + nod * 0.18 * s)
    reach = (UA + FA) * s
    if hands is None:
        hands = [(shs[0][0] - 0.07 * s, shy + reach), (shs[1][0] + 0.07 * s, shy + reach)]
    arms = []
    for i, sd in enumerate((-1, 1)):
        el, hd = ik(shs[i], hands[i], UA * s, FA * s, (sd * elbow[0], elbow[1]))
        arms.append((shs[i], el, hd))
    hw = lerp(0.04, 0.10, build) * s
    legs = []
    for sd in (-1, 1):
        h0 = (x + sd * hw, hip[1])
        kn, ft = ik(h0, (x + sd * feet * s, ground), LEG * s, LEG * s, (sd, -0.2))
        legs.append((h0, kn, ft))
    return dict(s=s, hip=hip, neck=neck, sh=shs, head=head, r=r, arms=arms, legs=legs, build=build,
                hands=[a_[2] for a_ in arms])


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
    for shp, el, hd in j["arms"]:
        ctx.move_to(*shp); ctx.line_to(*el); ctx.line_to(*hd); ctx.stroke()
        if b > 0.02:  # delts + biceps
            ctx.arc(*shp, 0.14 * s * b, 0, 2 * math.pi); ctx.fill()
            ctx.arc(lerp(shp[0], el[0], 0.5), lerp(shp[1], el[1], 0.5), 0.12 * s * b, 0, 2 * math.pi); ctx.fill()
    ctx.arc(*j["head"], j["r"], 0, 2 * math.pi); ctx.fill()
    front_face(ctx, j["head"], j["r"], smile, a)


def deadlift_hip(ground, s, bar_y, grip, build, feet=0.30):
    """Hip height that lets hands at ±grip reach bar_y (capped at standing)."""
    hx = grip - shoulder_w(s, build)
    dv = math.sqrt(max((0.96 * (UA + FA) * s) ** 2 - hx ** 2, 1))
    return min(ground - (bar_y - dv + s - 0.08 * s), stand_h(s, feet))


def deadlift_top(ground, s, grip, build, feet=0.30):
    hx = grip - shoulder_w(s, build)
    dv = math.sqrt(max((0.96 * (UA + FA) * s) ** 2 - hx ** 2, 1))
    return ground - stand_h(s, feet) - s + 0.08 * s + dv


# ---------------------------------------------------------------- objects
def box(ctx, cx, bottom, w, h, a=1.0, rim=RIM, glow=0.0):
    """Cardboard box standing on `bottom`. glow>0 adds an accent halo (the hero's own box)."""
    if glow > 0:
        halo(ctx, cx, bottom - h / 2, w * 1.6, col=accent(), a=0.35 * glow * a)
    rounded_rect(ctx, cx - w / 2, bottom - h, w, h, 5)
    ctx.set_source_rgba(0.13, 0.13, 0.13, a); ctx.fill_preserve()
    ctx.set_source_rgba(*rim, a); ctx.set_line_width(3); ctx.stroke()
    ctx.set_source_rgba(*(c * 0.6 for c in rim), a)
    ctx.move_to(cx, bottom - h + 3); ctx.line_to(cx, bottom - h + min(h * 0.4, 24)); ctx.stroke()


def stack(ctx, bx, by, boxes, tilt=0.0, sway=0.0, squash=1.0, a=1.0):
    """boxes = [(w, h, x_offset), ...] bottom-up from (bx, by). tilt rotates about the base; sway bends
    the upper boxes sideways; squash < 1 for an impact. Returns world (x, y) of the top centre."""
    ctx.save(); ctx.translate(bx, by); ctx.rotate(tilt)
    y, lx = 0.0, 0.0
    total = sum(h for _, h, _ in boxes)
    for w, h, off in boxes:
        hh = h * squash
        lx = off + sway * ((-y) / max(total, 1)) ** 2
        box(ctx, lx, y, w, hh, a)
        y -= hh
    ctx.restore()
    c, s_ = math.cos(tilt), math.sin(tilt)
    return (bx + c * lx - s_ * y, by + s_ * lx + c * y)


def barbell(ctx, cx, y, half, R, n, a=1.0, bend=0.0, rim=(0.78, 0.78, 0.78)):
    """Front view; plates edge-on. Rests on the floor when y = ground - R. bend>0 = bar flexing."""
    pw, gap = max(8.0, R * 0.30), 3
    ctx.new_path(); ctx.move_to(cx - half, y)
    ctx.curve_to(cx - half * 0.3, y - bend * 1.33, cx + half * 0.3, y - bend * 1.33, cx + half, y)
    ctx.set_source_rgba(*rim, a); ctx.set_line_width(max(4, R * 0.10)); ctx.stroke()
    inner = half - 10 - n * (pw + gap)
    for sd in (-1, 1):
        ctx.rectangle(cx + sd * inner - 4, y - R * 0.18, 8, R * 0.36); ctx.set_source_rgba(*rim, a); ctx.fill()
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


def bench(ctx, x, ground=G, a=1.0, glow=0.0, col=(0.7, 0.7, 0.7)):
    """Park bench seen from the front. Seat top ≈ ground-34: a fig at x with SIT_CHAIR sits on it."""
    if glow > 0:
        halo(ctx, x, ground - 60, 220, col=col, a=0.25 * glow)
    ctx.new_path(); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgba(*col, a); ctx.set_line_width(6)
    for sx in (-92, 92):
        ctx.move_to(x + sx, ground); ctx.line_to(x + sx, ground - 34)
        ctx.move_to(x + sx, ground - 34); ctx.line_to(x + sx - 6, ground - 104)
    ctx.stroke()
    for y0, h in ((ground - 40, 10), (ground - 106, 10), (ground - 84, 9)):
        dx = -6 if y0 < ground - 50 else 0
        rounded_rect(ctx, x - 112 + dx, y0, 224, h, 3)
        ctx.set_source_rgba(0.2, 0.2, 0.2, a); ctx.fill_preserve()
        ctx.set_source_rgba(*col, a); ctx.set_line_width(2.5); ctx.stroke()


def road_sign(ctx, x, ground, lines, a=1.0, col=(0.85, 0.85, 0.85), h=270, w=300, size=28):
    """Roadside sign on a post; lines = ["FINISH LINE", "AHEAD →"]. Readable as a frame-0 hook at zoom 2."""
    top = ground - h
    ctx.new_path(); ctx.set_source_rgba(0.45, 0.45, 0.45, a); ctx.set_line_width(8)
    ctx.move_to(x, ground); ctx.line_to(x, top + 40); ctx.stroke()
    ph = 34 + size * 1.25 * len(lines)
    rounded_rect(ctx, x - w / 2, top - ph / 2, w, ph, 10)
    ctx.set_source_rgba(0.10, 0.10, 0.10, a); ctx.fill_preserve()
    ctx.set_source_rgba(*col, a); ctx.set_line_width(4); ctx.stroke()
    for i, ln in enumerate(lines):
        label(ctx, ln, x, top - ph / 2 + 17 + size * 1.25 * (i + 0.8), a, size=size, col=col, bold=True)


def finish_arch(ctx, x, ground_fn, glow=1.0, text="FINISH"):
    """Gold finish arch with a chequered line; ground_fn(x) gives the road height."""
    yf = ground_fn(x)
    gold = accent()
    if glow > 0:
        halo(ctx, x, yf - 150, 340, col=gold, a=0.30 * glow)
    col = tuple(lerp(0.45, c, 0.4 + 0.6 * glow) for c in gold)
    ctx.new_path(); ctx.set_line_width(7); ctx.set_source_rgba(*col, 1)
    for px in (x - 95, x + 95):
        ctx.move_to(px, ground_fn(px)); ctx.line_to(px, yf - 250)
    ctx.stroke()
    ctx.rectangle(x - 112, yf - 268, 224, 48); ctx.set_source_rgba(0.12, 0.10, 0.06, 1); ctx.fill_preserve()
    ctx.set_source_rgba(*col, 1); ctx.set_line_width(3); ctx.stroke()
    label(ctx, text, x, yf - 234, 1.0, size=28, col=col, bold=True)
    for k in range(19):
        px = x - 95 + k * 10
        ctx.rectangle(px, ground_fn(px) + 2 + (k % 2) * 8, 10, 8); ctx.set_source_rgba(*col, 0.9); ctx.fill()


def hanging_lamp(ctx, x, floor, a=1.0, col=(1, 0.95, 0.85), cone=0.10, y=790):
    """Gym/stage lamp with a light cone down to `floor`. Lerp col toward accent() for a payoff."""
    ctx.new_path(); ctx.set_source_rgba(0.3, 0.3, 0.3, a); ctx.set_line_width(2)
    ctx.move_to(x, 705); ctx.line_to(x, y); ctx.stroke()
    polyline(ctx, [(x - 16, y), (x + 16, y), (x + 40, y + 30), (x - 40, y + 30)], close=True)
    ctx.set_source_rgba(0.32, 0.32, 0.32, a); ctx.fill()
    polyline(ctx, [(x - 34, y + 30), (x + 34, y + 30), (x + 200, floor), (x - 200, floor)], close=True)
    ctx.set_source(vgrad(y + 30, floor, (*col, cone * a), (*col, 0.02 * a))); ctx.fill()
    halo(ctx, x, y + 32, 60, col=col, a=0.35 * a)


# ---------------------------------------------------------------- environments
def floor(ctx, scroll=0.0, ground=G, x0=0, x1=1080):
    """Flat ground line + dashes; increase `scroll` to walk in place (the world slides left)."""
    ctx.new_path(); ctx.set_line_width(3); ctx.set_source_rgba(0.42, 0.42, 0.42, 1)
    ctx.move_to(x0, ground + 2); ctx.line_to(x1, ground + 2); ctx.stroke()
    ctx.set_line_width(2); ctx.set_source_rgba(0.24, 0.24, 0.24, 1)
    for k in range(int((x1 - x0) / 90) + 3):
        x = (k * 90 - scroll) % (x1 - x0 + 180) + x0 - 90
        ctx.move_to(x, ground + 22); ctx.line_to(x + 34, ground + 22)
    ctx.stroke()


def park(ctx, scroll=0.0, ground=G):
    """floor() plus dim trees and lamp posts drifting by at half speed (parallax)."""
    from props import lamp_post, tree
    for k in range(5):
        x = (k * 340 + 120 - scroll * 0.5) % 1700 - 300
        if k % 2:
            lamp_post(ctx, x, ground - 6, h=300, a=0.35, on=True)
        else:
            tree(ctx, x, ground - 6, s=0.95, a=0.55, shade=0.14)
    floor(ctx, scroll, ground)


class Road:
    """A world-space road with one smooth hill (crest hc, half-width hw, height hh). y(x) = surface."""

    def __init__(self, hc, hw=440, hh=110, ground=G):
        self.hc, self.hw, self.hh, self.g = hc, hw, hh, ground

    def y(self, x):
        if abs(x - self.hc) < self.hw:
            return self.g - self.hh * (0.5 + 0.5 * math.cos(math.pi * (x - self.hc) / self.hw))
        return self.g

    def draw(self, ctx, x0=-800, x1=4000):
        xs = range(int(x0), int(x1), 16)
        ctx.new_path()
        for x in xs:
            ctx.line_to(x, self.y(x))
        for x in reversed(xs):
            ctx.line_to(x, self.y(x) + 40)
        ctx.close_path(); ctx.set_source_rgba(0.075, 0.075, 0.075, 1); ctx.fill()
        ctx.new_path()
        for x in xs:
            ctx.line_to(x, self.y(x))
        ctx.set_source_rgba(0.45, 0.45, 0.45, 1); ctx.set_line_width(3); ctx.stroke()
        ctx.set_source_rgba(0.28, 0.28, 0.28, 1); ctx.set_line_width(3)
        for x in range(int(x0), int(x1), 80):
            ctx.move_to(x, self.y(x) + 20); ctx.line_to(x + 34, self.y(x + 34) + 20)
        ctx.stroke()


_rng = random.Random(4)
_STARS = [(_rng.uniform(-800, 4000), _rng.uniform(250, 1180), _rng.uniform(1.2, 3.0), _rng.uniform(0, 6))
          for _ in range(160)]
_CONFETTI = [(_rng.uniform(-150, 150), _rng.uniform(0, 1), _rng.uniform(0.6, 1.4), _rng.random() < 0.6)
             for _ in range(46)]


def stars(ctx, t, amt=0.5):
    for x, y, r, ph in _STARS:
        a = amt * (0.35 + 0.35 * math.sin(t * 1.3 + ph))
        if a > 0.02:
            ctx.new_path(); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, a); ctx.fill()


# ---------------------------------------------------------------- effects
def tremble(t, amt):
    """Organic shake value in px (use for x jitter, knee_shake, hand_shake)."""
    return amt * (math.sin(t * 61) * 0.6 + math.sin(t * 37 + 1) * 0.4)


def impact(ctx, imp, shake=9.0):
    """Call right after ctx.save() and BEFORE cam(): screen shake for imp = t - t_hit seconds."""
    if imp > 0:
        ctx.translate(shake * math.exp(-7 * imp) * math.sin(55 * imp), 0.85 * shake * math.exp(-8 * imp) * math.sin(63 * imp))


def flash(ctx, imp, a=0.2):
    """White flash after an impact (screen space, after restoring the camera)."""
    if imp > 0:
        ctx.set_source_rgba(1, 1, 1, a * math.exp(-10 * imp)); ctx.paint()


def settle(imp, freq=9.0, damp=7.0):
    """0 → 1 with a damped overshoot after an impact (knees buckling, a stack squashing)."""
    return 1 - math.exp(-damp * imp) * math.cos(freq * imp) if imp > 0 else 0.0


def dust(ctx, x, y, k, spread=1.0):
    """Puffs either side of (x, y); k runs 0..1 over the puff's life."""
    if not 0 < k < 1:
        return
    for sd in (-1, 1):
        for i in range(3):
            ctx.new_path()
            ctx.arc(x + sd * spread * (12 + 40 * k + 14 * i), y - 4 - 10 * k * i, 5 + 11 * k, 0, 2 * math.pi)
            ctx.set_source_rgba(0.6, 0.6, 0.6, 0.45 * (1 - k)); ctx.fill()


def strain_lines(ctx, head, r, a, t):
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


def sweat(ctx, head, r, t, t0, sd=1):
    u = t - t0
    if not 0 <= u <= 0.7:
        return
    x = head[0] + sd * (r + 4 + 70 * u)
    y = head[1] - 0.3 * r - 90 * u + 380 * u * u
    a = 1 - ease((u - 0.45) / 0.25)
    ctx.new_path(); ctx.move_to(x, y - 9)
    ctx.curve_to(x + 6, y - 1, x + 5, y + 5, x, y + 5); ctx.curve_to(x - 5, y + 5, x - 6, y - 1, x, y - 9)
    ctx.set_source_rgba(0.75, 0.85, 0.95, 0.85 * a); ctx.fill()


def confetti(ctx, t, x0, y0):
    """Gold/white confetti falling around (x0, y0); t = seconds since the burst."""
    if t <= 0:
        return
    for dx, ph, sp, is_gold in _CONFETTI:
        y = y0 - 260 + ((t * 140 * sp + ph * 300) % 420)
        x = x0 + dx * (1 + 0.4 * t) + 14 * math.sin(t * 3 + ph * 9)
        ctx.save(); ctx.translate(x, y); ctx.rotate(t * 4 * sp + ph * 6)
        ctx.rectangle(-5, -2.5, 10, 5)
        ctx.set_source_rgba(*(accent() if is_gold else (1, 1, 1)), min(1.0, t * 3) * 0.9); ctx.fill()
        ctx.restore()


# ---------------------------------------------------------------- camera, darkness, captions
def cam(ctx, z, wx, wy, sx=540, sy=1200, clip=True):
    """World point (wx, wy) appears at screen (sx, sy), zoomed by z. Use inside save()/restore().
    clip keeps zoomed world art out of the caption band (y < 705)."""
    if clip:
        ctx.rectangle(0, 705, 1080, 1215); ctx.clip()
    ctx.translate(sx, sy); ctx.scale(z, z); ctx.translate(-wx, -wy)


def zoom_lerp(a, b, k):
    """Perceptually even zoom interpolation (use for pull-backs / push-ins)."""
    return math.exp(lerp(math.log(a), math.log(b), k))


def darkness(ctx, amt, x0=560):
    """What the character can't see: the right side of the frame sinks to black (screen space,
    draw after restoring the camera, before captions). Pair with hiding the reveal object entirely."""
    if amt <= 0:
        return
    g = cairo.LinearGradient(x0, 0, 1080, 0)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(0.6, 0, 0, 0, 0.85 * amt)
    g.add_color_stop_rgba(1, 0, 0, 0, amt)
    ctx.rectangle(0, 705, 1080, 1215); ctx.set_source(g); ctx.fill()


def faded(ctx, a, draw):
    """Run draw() into a group and paint it at alpha a (fade an object, a caption, a whole world)."""
    if a <= 0:
        return None
    ctx.push_group(); out = draw(); ctx.pop_group_to_source(); ctx.paint_with_alpha(min(a, 1.0))
    return out


def cap(ctx, t, line1, line2="", t2=2.4, a=1.0, accent_words=()):
    """engine.caption with an alpha (swap caption sets inside one long scene) and t<0 = not yet."""
    if t < 0:
        return
    faded(ctx, a, lambda: caption(ctx, t, line1, line2, t2=t2, accent_words=accent_words))


def phrase_beats(ctx, t, phrases, y=TEXT_Y2, size=40, hold=None):
    """phrases = [(t_start, "One step."), (t_next, "Then another."), ...]: each replaces the last, timed
    to on-screen actions (footsteps, reps). The last one stays."""
    for i, (t0, text) in enumerate(phrases):
        t_end = phrases[i + 1][0] if i + 1 < len(phrases) else 1e9
        a = 1 - ease((t - t_end) / 0.2)
        if t >= t0 and a > 0:
            faded(ctx, a, lambda: words(ctx, text, y, t0, t, size=size, step=0.1))


def title_lines(ctx, t, lines, size=54, y0=900, gap=72, accent_words=()):
    """End card: lines = [(t_start, "TEXT"), ...] stacked from y0; a gap of None leaves a blank line."""
    y = y0
    for t0, text in lines:
        if text:
            words(ctx, text, y, t0, t, size=size, step=0.14, accent_words=accent_words)
        y += gap
