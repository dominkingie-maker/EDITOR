"""DISCIPLINE MAKES NO NOISE. RESULTS DO. — 37 s, music only, story told in captions.

Hook (flash-forward): frame 0 is the ending — the skinny stickman blazing past the two runners with
speed lines and a gold trail; it slams at 0.35 s, then a tape-rewind tears back to the start (1.3 s).

  python3 <skill>/scripts/score.py music_score.py --out music.wav
  python3 <skill>/scripts/hookcheck.py episode.py
  python3 <skill>/scripts/engine.py episode.py --out discipline-makes-no-noise.mp4 --music music.wav
"""
import math

from engine import GOLD, Scene
from props import cloud, moon, rain, speech_bubble, sun
from storykit import (FALL, HANDS_DOWN, STAND, cam, cap, clamp, dust, ease, eio, faded, fig, flash, halo,
                      impact, lerp, mix, park, pose_with, punch_zoom, rewind_glitch, rounded_rect, run,
                      speed_lines, stars, struggle_run, title_lines, tremble, walk)

G = 1400
HS, RS = 58, 60                       # skinny hero / the two runners
GREY = (0.55, 0.55, 0.55)
RUN_SPEED = 230                       # px/s the world scrolls while they run


# ---------- characters ----------
def shoes(ctx, j, s, wear=0.0, a=1.0):
    """Running shoes on both feet; wear 0..1 adds holes and a flapping sole."""
    for k, (fx, fy) in enumerate(j["feet"]):
        shade = 0.85 if k == 0 else 0.42
        L, h = 0.36 * s, 0.13 * s
        rounded_rect(ctx, fx - 0.08 * s, fy - h * 0.7, L, h, h * 0.45)
        ctx.set_source_rgba(0.62 * shade, 0.62 * shade, 0.62 * shade, a); ctx.fill_preserve()
        ctx.set_source_rgba(shade, shade, shade, a); ctx.set_line_width(2.5); ctx.stroke()
        for i in range(int(wear * 3.5)):
            ctx.new_path(); ctx.arc(fx + (0.05 + 0.08 * i) * s, fy - h * 0.2, 0.025 * s + 1, 0, 2 * math.pi)
            ctx.set_source_rgba(0, 0, 0, a); ctx.fill()
        if wear > 0.6 and k == 0:
            ctx.new_path(); ctx.move_to(fx + 0.26 * s, fy + h * 0.3); ctx.line_to(fx + 0.36 * s, fy + h * 0.65)
            ctx.set_source_rgba(shade, shade, shade, a); ctx.set_line_width(2.5); ctx.stroke()


def hero(ctx, x, t, ph, strong=0.0, wear=0.0, shake=1.5, pose=None, face=None, ground=G):
    """The skinny stickman (thin limbs). strong 0 = struggling run .. 1 = powerful upright run."""
    p = pose or mix(struggle_run(ph, 0.32), pose_with(run(ph), lean=0.22), strong)
    j = fig(ctx, x, ground, HS, p, lw=0.13, knee_shake=tremble(t, shake), face=face)
    shoes(ctx, j, HS, wear)
    return j


def runner(ctx, x, t, ph, look_back=0.0, laugh=0.0, pose=None, a=1.0):
    """One of the two runners (grey, normal build). look_back turns the head back; laugh shakes it."""
    p = pose or pose_with(run(ph), lean=lerp(0.22, -0.10, look_back))
    hd = -16 * look_back + 3 * laugh * math.sin(t * 34)
    j = fig(ctx, x, G, RS, p, col=GREY, a=a, head_dx=hd)
    shoes(ctx, j, RS, 0.0, a)
    return j


# ---------- skies ----------
def dawn(ctx, t, sun_y, a=1.0):
    halo(ctx, 860, G - 20, 620, col=(1.0, 0.72, 0.42), a=0.16 * a)
    sun(ctx, 860, sun_y, r=46, a=0.9 * a, col=(1.0, 0.82, 0.55), t=t)


def night(ctx, t):
    stars(ctx, t, 0.8)
    moon(ctx, 840, 820, r=34)


def storm(ctx, t):
    for x, y in ((180, 760), (520, 735), (860, 770)):
        cloud(ctx, x, y, s=1.3, shade=0.22)
    rain(ctx, 0, 790, 1080, 640, t, a=1.0, density=46, speed=2.4)


# ---------- scenes ----------
def s1_hook(duration=4.5):
    def draw(ctx, t):
        if t < 1.3:   # flash-forward: the ending first
            imp = t - 0.35
            ctx.save(); impact(ctx, imp, 7)
            cam(ctx, punch_zoom(t, 0.35, base=1.5), 540, G - 110, 540, 1170)
            dawn(ctx, t, G - 260); park(ctx, 600 * t)
            for x, ph0 in ((470, 0.0), (600, 1.7)):
                runner(ctx, x, t, t * 11 + ph0, look_back=-0.6 * ease(imp / 0.2))
            hx = 300 + 600 * t                 # already in frame at t=0, level with them at the hit
            halo(ctx, hx - 90, G - 95, 190, col=GOLD, a=0.35)
            speed_lines(ctx, hx - 20, G - 100, t, a=1.0)
            hero(ctx, hx, t, t * 17, strong=1.0, wear=1.0, shake=0, face="open")
            dust(ctx, hx - 60, G, (t % 0.4) / 0.4, spread=0.8)
            ctx.restore(); flash(ctx, imp, 0.22)
            rewind_glitch(ctx, t, 0.8, 0.5)
            return
        u = t - 1.3                              # the real start
        scroll = RUN_SPEED * u
        park(ctx, scroll)
        for k, (x, ph0) in enumerate(((640, 0.0), (775, 1.9))):
            j = runner(ctx, x + 25 * u, u, scroll / 30 + ph0, look_back=ease((u - 0.5) / 0.4), laugh=ease((u - 0.8) / 0.3))
            for t0, txt in ((0.9 + 0.35 * k, "HA!"), (1.6 + 0.3 * k, "HAHA")):
                a = ease((u - t0) / 0.15) * (1 - ease((u - t0 - 0.6) / 0.2))
                if a > 0:
                    speech_bubble(ctx, j["head"][0] - 10, j["head"][1] - 62, txt, a, size=24, tail=-1)
        hero(ctx, 230, u, scroll / 26, wear=0.0, shake=2.0)
        cap(ctx, u, "They looked back and laughed.", "He was way behind.", 1.7)
    return Scene(draw, duration, "hook-flashforward-the-pass", "They looked back and laughed. / He was way behind.")


def s2_trip(duration=4.5):
    def draw(ctx, t):
        moving = min(t, 2.3) + 0.15 * (1 - math.exp(-6 * max(0.0, t - 2.3)))
        scroll = RUN_SPEED * moving
        ctx.save(); impact(ctx, t - 2.3, 9)
        park(ctx, scroll)
        for x, ph0 in ((700, 0.0), (830, 1.9)):
            runner(ctx, x + 170 * t, t, (scroll + 170 * t) / 30 + ph0, look_back=0.6 * (1 - ease((t - 0.6) / 0.5)))
        hx = 230 + 70 * min(t, 2.0)
        if t < 2.0:
            pose = pose_with(struggle_run(scroll / 24, 0.40))
        else:
            pose = mix(mix(struggle_run(scroll / 24, 0.40), FALL, eio((t - 2.0) / 0.3)), HANDS_DOWN, ease((t - 2.3) / 0.12))
            pose = pose_with(pose, lean=pose["lean"] + 0.05 * math.sin(t * 9) * ease((t - 2.8) / 0.4))
        hero(ctx, hx, t, scroll / 24, pose=pose, shake=2.4, face="strain")
        dust(ctx, hx + 15, G, (t - 2.3) / 0.6, spread=1.3)
        ctx.restore(); flash(ctx, t - 2.3, 0.12)
        cap(ctx, t, "He tried to catch up.", "He tripped and fell.", 2.3)
    return Scene(draw, duration, "custom:trip_and_fall", "He tried to catch up. / He tripped and fell.")


def s3_next_morning(duration=4.0):
    def draw(ctx, t):
        run_t = clamp((t - 0.8) / 1.8) * 1.8
        scroll = RUN_SPEED * 0.8 * run_t
        ctx.save(); impact(ctx, t - 2.6, 6)
        dawn(ctx, t, lerp(G + 30, G - 190, eio(t / 2.6)))
        park(ctx, scroll)
        hx = lerp(100, 330, eio(t / 0.8)) + 20 * ease((t - 2.4) / 0.2)
        if t < 0.8:
            pose = walk(hx / 30, 0.42)
        elif t < 2.4:
            pose = struggle_run(scroll / 24, 0.33)
        else:
            pose = mix(mix(struggle_run(scroll / 24, 0.33), FALL, eio((t - 2.4) / 0.2)), HANDS_DOWN, ease((t - 2.6) / 0.12))
        hero(ctx, hx, t, scroll / 24, pose=pose, wear=0.15, shake=2.0)
        dust(ctx, hx + 15, G, (t - 2.6) / 0.6)
        ctx.restore()
        cap(ctx, t, "The next morning, he came back.", "He ran. And fell again.", 2.2)
    return Scene(draw, duration, "custom:next_morning", "The next morning, he came back. / He ran. And fell again.")


STAGES = [("DAY 3", "storm", 0.30), ("DAY 12", "shoes", 0.65), ("DAY 27", "night", 0.85), ("DAY 46", "dawn", 1.0)]
STAGE = 1.5


def s4_days(duration=6.0):
    def draw(ctx, t):
        i = min(int(t / STAGE), len(STAGES) - 1)
        u = t - i * STAGE
        day, kind, wear = STAGES[i]
        blink = (1 if i == 0 else ease(u / 0.18)) * (1 if i == len(STAGES) - 1 else ease((STAGE - u) / 0.18))
        scroll = RUN_SPEED * t
        strong = {"storm": 0.0, "shoes": 0.2, "night": 0.35, "dawn": 0.75}[kind]

        def world():
            ctx.save()
            if kind == "shoes":
                cam(ctx, 6.0, 552, G - 12, 540, 1240)
            if kind == "storm":
                storm(ctx, t)
            elif kind == "night":
                night(ctx, t)
            elif kind == "dawn":
                dawn(ctx, t, G - 230)
            park(ctx, scroll)
            hero(ctx, 540, t, scroll / 26, strong=strong, wear=wear, shake=2.6 if kind in ("shoes", "night") else 1.4,
                 face="strain" if kind == "shoes" else None)
            ctx.restore()
            if kind == "night":
                ctx.rectangle(0, 705, 1080, 1215); ctx.set_source_rgba(0, 0, 0.04, 0.35); ctx.fill()

        faded(ctx, blink, world)
        faded(ctx, blink, lambda: _day_label(ctx, day, i))
        cap(ctx, t, "Days passed.", "But every morning, he returned.", 1.6)
    return Scene(draw, duration, "custom:days_pass", "Days passed. / But every morning, he returned.")


def _day_label(ctx, day, i):
    from storykit import label
    rounded_rect(ctx, 430, 784, 220, 100, 20); ctx.set_source_rgba(0, 0, 0, 0.78); ctx.fill()  # stays readable over close-ups
    label(ctx, day, 540, 830, 0.9, size=42, col=(0.92, 0.92, 0.92), bold=True)
    for k in range(len(STAGES)):
        ctx.new_path(); ctx.arc(540 + (k - 1.5) * 24, 866, 5, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.85 if k <= i else 0.2); ctx.fill()


def s5_they_return(duration=5.0):
    def draw(ctx, t):
        go = ease((t - 2.0) / 0.4)
        scroll = RUN_SPEED * max(0.0, t - 2.0)
        dawn(ctx, t, G - 240)
        park(ctx, scroll)
        for x0, x1, ph0 in ((-120, 420, 0.0), (-250, 550, 1.9)):
            x = lerp(x0, x1, eio(t / 1.9))
            p = mix(walk(x / 30, 0.42), STAND, ease((t - 1.8) / 0.2))
            p = mix(p, pose_with(run(scroll / 30 + ph0), lean=0.2), go)
            runner(ctx, x, t, scroll / 30 + ph0, pose=p)
        cap(ctx, t, "One day, the two came back.", "They started running.", 2.1)
    return Scene(draw, duration, "custom:they_return", "One day, the two came back. / They started running.")


def s6_pass(duration=4.5):
    def draw(ctx, t):
        scroll = RUN_SPEED * t
        stunned = ease((t - 1.6) / 0.6)
        ctx.save(); impact(ctx, t - 1.0, 6)
        dawn(ctx, t, G - 250); park(ctx, scroll)
        for x, ph0 in ((420, 0.0), (550, 1.9)):
            p = mix(pose_with(run(scroll / 30 + ph0), lean=0.2), pose_with(STAND, lean=-0.10), stunned)
            jolt = -0.25 * math.exp(-6 * max(0.0, t - 1.0)) if t > 1.0 else 0.0
            runner(ctx, x, t, scroll / 30 + ph0, pose=pose_with(p, lean=p["lean"] + jolt),
                   look_back=-0.8 * ease((t - 1.0) / 0.3))
        hx = 480 + 800 * (t - 1.0)            # level with them on the music drop (t = 1.0)
        if -200 < hx < 1300:
            halo(ctx, hx - 90, G - 95, 200, col=GOLD, a=0.4)
            speed_lines(ctx, hx - 20, G - 100, t, a=1.0)
            hero(ctx, hx, t, t * 17, strong=1.0, wear=1.0, shake=0, face="open")
        ctx.restore(); flash(ctx, t - 1.0, 0.12)
        cap(ctx, t, "Suddenly, someone passed them.", "The same skinny stickman.", 1.8)
    return Scene(draw, duration, "custom:the_pass", "Suddenly, someone passed them. / The same skinny stickman.")


def s7_no_look_back(duration=4.0):
    def draw(ctx, t):
        scroll = 420 * t
        ctx.save()
        cam(ctx, lerp(1.75, 1.6, t / duration), 600, G - 95, 540, 1180)
        dawn(ctx, t, G - 260); park(ctx, scroll)
        for x, ph0 in ((300 - 120 * t, 0.0), (190 - 120 * t, 1.9)):
            runner(ctx, x, t, t * 8 + ph0, pose=pose_with(walk(t * 6 + ph0, 0.3), lean=0.05), a=0.6)
        halo(ctx, 600, G - 95, 240, col=GOLD, a=0.22)
        hero(ctx, 600, t, scroll / 30, strong=1.0, wear=1.0, shake=0, face="open")
        ctx.restore()
        cap(ctx, t, "Only now,", "he didn't even look back.", 1.1)
    return Scene(draw, duration, "custom:no_look_back", "Only now, / he didn't even look back.")


def s8_message(duration=4.5):
    def draw(ctx, t):
        title_lines(ctx, t, [(0.15, "DISCIPLINE"), (0.6, "MAKES NO NOISE.")], size=56, y0=860, gap=74)
        title_lines(ctx, t, [(1.9, "RESULTS DO.")], size=70, y0=1075, accent_words={"RESULTS", "DO."})
        halo(ctx, 540, 1055, 280, col=GOLD, a=0.12 * ease((t - 1.9) / 0.6))
    return Scene(draw, duration, "custom:message_card", "DISCIPLINE MAKES NO NOISE. / RESULTS DO.")


EPISODE = dict(
    title="Discipline Makes No Noise",
    accent=GOLD,
    watermark="",
    fade_out=0.3, black=1 / 30, fade_in=0.35, end_fade=0.6,
    scenes=[s1_hook(), s2_trip(), s3_next_morning(), s4_days(), s5_they_return(), s6_pass(),
            s7_no_look_back(), s8_message()],
)
