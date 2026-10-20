"""KEEP GOING — "You can't always see how close you are." 41.8 s, music only, story told in captions.

Hook: frame 0 is a close-up of a roadside sign, FINISH LINE AHEAD →, as he stumbles into frame and
nearly goes down (jolt + thud). The camera pulls back: only road, and a distant hill.
The finish line is not drawn at all until the crane shot and the crest (darkness hides the rest).

  python3 <skill>/scripts/score.py music_score.py --out music.wav
  python3 <skill>/scripts/engine.py episode.py --out keep-going.mp4 --music music.wav
"""
import math

from storykit import (FALL, HANDS_DOWN, LOOK_HANDS, ONE_KNEE, SIT_DOWN, SIT_UP, STAND, TIRED, Road, cam,
                      cap, clamp, confetti, darkness, dust, ease, eio, faded, fig, finish_arch, halo, impact,
                      lerp, mix, phrase_beats, pose_with, road_sign, stars, steps, struggle_run,
                      title_lines, tremble, walk, zoom_lerp)
from engine import GOLD, Scene

G, S = 1400, 62
SX = 430                         # the FINISH LINE AHEAD sign
XS = 1080                        # where he sits down
ROAD = Road(hc=XS + 560, hw=460, hh=130, ground=G)
HC, XF = ROAD.hc, ROAD.hc + 240  # crest, finish line
STEP_STARTS = [0.4, 1.3, 2.2, 3.0, 3.7, 4.3, 4.9]   # scene 6 footsteps (music_score.py kicks on these)
STRIDE = (HC - XS - 20) / len(STEP_STARTS)


def world(ctx, t, finish_a=0.0, finish_glow=0.0, star_amt=0.5):
    stars(ctx, t, star_amt)
    ROAD.draw(ctx)
    road_sign(ctx, SX, G, ["FINISH LINE", "AHEAD  →"])
    if finish_a > 0:
        faded(ctx, finish_a, lambda: finish_arch(ctx, XF, ROAD.y, finish_glow))


def s1_hook(duration=4.0):
    def draw(ctx, t):
        x = 250 + 160 * t - 30 * ease((t - 0.6) / 0.4)
        trip = math.sin(math.pi * clamp((t - 0.5) / 0.55))         # nearly goes down, catches himself
        pose = mix(struggle_run(x / 26, lean=lerp(0.30, 0.12, ease((t - 2.4) / 0.5))), FALL, 0.6 * trip)
        pull = eio((t - 1.1) / 1.5)
        ctx.save()
        impact(ctx, t - 0.7, shake=5)
        cam(ctx, zoom_lerp(2.0, 0.95, pull), lerp(SX + 30, x + 330, pull), lerp(G - 235, G - 150, pull),
            540, lerp(1050, 1200, pull))
        world(ctx, t)
        fig(ctx, x, G, S, pose, face="strain", knee_shake=tremble(t, 2.0))
        dust(ctx, x + 20, G, (t - 0.7) / 0.6)
        ctx.restore()
        darkness(ctx, 0.9 * pull)
        cap(ctx, t, "The sign said he was close.", "All he could see was more road.", 2.6)
    return Scene(draw, duration, "hook-sign-finish-line-ahead", "The sign said he was close. / All he could see was more road.")


def s2_falls(duration=5.0):
    def draw(ctx, t):
        if t < 1.3:
            x = 860 + 90 * min(t, 1.0) + 10 * ease((t - 1.0) / 0.3)
            pose = mix(struggle_run(x / 24, lean=0.34), FALL, eio((t - 1.0) / 0.3))
        elif t < 3.0:
            x = 960
            pose = mix(mix(FALL, HANDS_DOWN, ease((t - 1.3) / 0.12)), ONE_KNEE, eio((t - 1.8) / 0.5))
            pose = mix(pose, TIRED, eio((t - 2.3) / 0.7))
        elif t < 3.9:
            x = 960 + 80 * eio((t - 3.0) / 0.9)
            pose = pose_with(walk((x - 960) / 28, 0.35), lean=0.25)
        else:
            x = 1040 + 10 * ease((t - 3.9) / 0.3)
            pose = mix(mix(TIRED, FALL, eio((t - 3.9) / 0.15)), HANDS_DOWN, ease((t - 4.05) / 0.15))
            pose = pose_with(pose, lean=pose["lean"] + 0.15 * ease((t - 4.3) / 0.6))
        ctx.save()
        impact(ctx, t - 1.3); impact(ctx, t - 4.2, shake=11)
        cam(ctx, 1.05, 1100, G - 140)
        world(ctx, t)
        fig(ctx, x, G, S, pose, face="strain", knee_shake=tremble(t, 2.2))
        dust(ctx, 965, G, (t - 1.3) / 0.6); dust(ctx, 1050, G, (t - 4.2) / 0.6, spread=1.3)
        ctx.restore()
        darkness(ctx, 0.9)
        cap(ctx, t, "His legs began to shake.", "He fell. Got up. Fell again.", 2.8)
    return Scene(draw, duration, "custom:falls_twice", "His legs began to shake. / He fell. Got up. Fell again.")


def s3_give_up(duration=3.5):
    head = (XS + 26, G - 98)

    def draw(ctx, t):
        push = eio((t - 1.5) / 1.9)
        ctx.save()
        cam(ctx, zoom_lerp(1.05, 2.2, push), lerp(1100, head[0], push), lerp(G - 140, head[1], push),
            540, lerp(1200, 1150, push))
        world(ctx, t)
        x = lerp(1050, XS, eio(t / 0.9))
        pose = mix(mix(HANDS_DOWN, SIT_UP, eio(t / 0.9)), SIT_DOWN, eio((t - 1.0) / 1.0))
        fig(ctx, x, G, S, pose_with(pose, lean=pose["lean"] + 0.03 * math.sin(t * 5)),
            face="closed" if t > 2.4 else "open", knee_shake=tremble(t, 0.8))
        ctx.restore()
        darkness(ctx, 0.9 * (1 - 0.5 * push))
        cap(ctx, t, "Defeated, he sat down.", "Ready to give up.", 1.8)
    return Scene(draw, duration, "custom:ready_to_give_up", "Defeated, he sat down. / Ready to give up.")


def s4_crane(duration=5.5):
    head = (XS + 26, G - 98)

    def draw(ctx, t):
        k = eio((t - 0.2) / 4.0)
        reveal = ease((t - 1.6) / 1.6)
        ctx.save()
        cam(ctx, zoom_lerp(2.2, 0.56, k), lerp(head[0], (XS + XF) / 2 + 40, k), lerp(head[1], G - 380, k),
            540, lerp(1150, 1260, k))
        world(ctx, t, finish_a=ease((t - 1.2) / 1.2), finish_glow=reveal, star_amt=0.5 + 0.5 * k)
        fig(ctx, XS, G, S, pose_with(SIT_DOWN, lean=SIT_DOWN["lean"] + 0.03 * math.sin(t * 2)), face="closed")
        n = int(16 * ease((t - 3.0) / 1.5))            # the few steps between him and the line
        for i in range(n):
            px = lerp(XS + 70, XF - 20, i / 15)
            ctx.new_path(); ctx.arc(px, ROAD.y(px) - 14, 5, 0, 2 * math.pi)
            ctx.set_source_rgba(*GOLD, 0.75); ctx.fill()
        ctx.restore()
        darkness(ctx, 0.9 * (1 - ease((t - 0.6) / 1.8)))
        cap(ctx, t, "Just beyond the hill...", "He had no idea how close he was.", 2.8)
    return Scene(draw, duration, "custom:crane_reveal", "Just beyond the hill... / He had no idea how close he was.")


def s5_hands(duration=4.5):
    def draw(ctx, t):
        up = eio((t - 3.1) / 1.2)
        ctx.save()
        cam(ctx, lerp(1.9, 1.45, up), XS + 40, lerp(G - 85, G - 110, up), 540, 1180)
        world(ctx, t)
        hands = ease((t - 1.0) / 0.4) * (1 - ease((t - 2.4) / 0.3))
        down = eio((t - 2.5) / 0.6)
        pose = mix(SIT_DOWN, SIT_UP, eio((t - 0.6) / 0.4))
        pose = mix(mix(mix(pose, LOOK_HANDS, hands), HANDS_DOWN, down), TIRED, up)
        j = fig(ctx, XS + 20 * down, G, S, pose, face="closed" if t < 0.5 else "open",
                knee_shake=tremble(t, 1.0 + 1.5 * up), hand_shake=tremble(t * 1.3, 2.5 * hands))
        halo(ctx, j["hand_f"][0], j["hand_f"][1], 60, a=0.35 * hands)
        ctx.restore()
        darkness(ctx, 0.9)
        cap(ctx, t, "He looked at his trembling hands.", "Then slowly pushed himself up.", 2.6)
    return Scene(draw, duration, "custom:trembling_hands", "He looked at his trembling hands. / Then slowly pushed himself up.")


def s6_walk(duration=6.0):
    def draw(ctx, t):
        dist, ph = steps(t, STEP_STARTS, dur=0.6, stride=STRIDE)
        x = XS + 20 + dist
        near = clamp((x - XS) / (HC - XS))
        ctx.save()
        cam(ctx, 1.0, x + 200, ROAD.y(x) - 150)
        world(ctx, t, finish_a=ease((near - 0.8) / 0.2), finish_glow=0.6)
        fig(ctx, x, ROAD.y(x), S, pose_with(walk(ph, 0.5), lean=0.10), face="open", knee_shake=tremble(t, 0.9))
        ctx.restore()
        darkness(ctx, 0.9 * (1 - near ** 1.5))
        cap(ctx, t, "This time, he didn't run.", "", 9)
        phrase_beats(ctx, t, list(zip(STEP_STARTS, ["One step.", "Then another.", "And another.", "Then another."])))
    return Scene(draw, duration, "custom:one_step_then_another", "This time, he didn't run. / One step. Then another...")


def s7_cross(duration=6.0):
    def draw(ctx, t):
        x = HC + (XF + 40 - HC) * eio((t - 2.4) / 2.6)
        walking = 2.4 < t < 5.0
        breath = math.sin(math.pi * clamp((t - 1.8) / 0.6))
        pose = pose_with(walk((x - HC) / 30, 0.42), lean=0.04) if walking else pose_with(STAND, lean=-0.04 - 0.06 * breath)
        punch = math.sin(math.pi * clamp((t - 0.1) / 2.2))
        face = "wide" if t < 1.0 else "smile"
        ctx.save()
        cam(ctx, 1.0 + 0.7 * punch, lerp(x + 200, x + 30, punch), ROAD.y(x) - lerp(150, 120, punch))
        world(ctx, t, finish_a=1.0, finish_glow=1.0)
        fig(ctx, x, ROAD.y(x), S, pose, face=face)
        confetti(ctx, t - 4.2, XF, ROAD.y(XF) - 40)
        ctx.restore()
        cap(ctx, t, "There it was.", "He smiled.", 1.1)
    return Scene(draw, duration, "custom:smile_and_cross", "There it was. / He smiled.")


def s8_pull_away(duration=2.5):
    def draw(ctx, t):
        k = eio(t / duration)
        ctx.save()
        cam(ctx, zoom_lerp(1.4, 0.55, k), XF + 30, ROAD.y(XF) - lerp(130, 330, k), 540, 1250)
        world(ctx, t, finish_a=1.0, finish_glow=1.0, star_amt=0.5 + 0.5 * k)
        halo(ctx, XF + 40, ROAD.y(XF) - 100, 200, col=GOLD, a=0.25)
        fig(ctx, XF + 40, ROAD.y(XF + 40), S, pose_with(STAND, lean=0.0, ua_f=0.35, fa_f=0.5), face="smile")
        confetti(ctx, t + 1.8, XF, ROAD.y(XF) - 40)
        ctx.restore()
    return Scene(draw, duration, "custom:pull_away", "")


def s9_message(duration=4.8):
    def draw(ctx, t):
        title_lines(ctx, t, [(0.15, "YOU CAN'T ALWAYS SEE HOW"), (0.75, "CLOSE YOU ARE.")], size=50, y0=860, gap=68)
        title_lines(ctx, t, [(1.9, "KEEP GOING.")], size=66, y0=1060, accent_words={"KEEP", "GOING."})
        a = ease((t - 1.9) / 0.6)
        halo(ctx, 540, 1040, 260, col=GOLD, a=0.12 * a)
    return Scene(draw, duration, "custom:keep_going_card", "YOU CAN'T ALWAYS SEE HOW CLOSE YOU ARE. / KEEP GOING.")


EPISODE = dict(
    title="Keep Going",
    accent=GOLD,
    watermark="",
    fade_out=0.3, black=1 / 30, fade_in=0.35, end_fade=0.6,
    scenes=[s1_hook(), s2_falls(), s3_give_up(), s4_crane(), s5_hands(), s6_walk(), s7_cross(),
            s8_pull_away(), s9_message()],
)
