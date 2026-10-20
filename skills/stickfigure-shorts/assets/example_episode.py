"""Example episode — shows the shape of an episode file, NOT scenes to reuse.

It mixes four different templates with one custom scene (`focus_lens`) built from an
idea in references/visual-ideas.md. Build your own episode the same way: pick ideas for
the message, use templates where they fit, write custom scenes where they don't.

  python3 <skill>/scripts/engine.py my_episode.py --preview sheet.png
  python3 <skill>/scripts/engine.py my_episode.py --out short.mp4 --music track.mp3
"""
import math
from engine import GOLD, Scene, caption, accent, ease, eio, halo, label, lerp
from scenes import checklist, domino, planet_zoom, spotlight


def focus_lens(line1, line2, duration=6.4):
    """Custom scene: scattered sunbeams do nothing; a lens slides in and gathers them into
    one point that ignites. (Idea bank: Focus & priorities → Magnifying glass.)"""
    gy, top = 1340, 760
    xs = [250 + k * 48 for k in range(12)]

    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2=3.0)
        ctx.set_line_width(3); ctx.set_source_rgba(0.35, 0.35, 0.35, 1)
        ctx.move_to(160, gy); ctx.line_to(920, gy); ctx.stroke()
        lens = eio((t - 1.6) / 0.9)                      # 0 = no lens, 1 = lens in place
        lx, ly = lerp(-200, 540, lens), 1050
        for k, x in enumerate(xs):
            wob = 18 * math.sin(t * 2.3 + k * 1.7) * (1 - lens)
            ctx.set_source_rgba(1, 0.95, 0.8, 0.35); ctx.set_line_width(3)
            ctx.move_to(x, top)
            if lens > 0.05:
                hit_x = lerp(x + wob, x, lens)
                ctx.line_to(hit_x, ly)
                ctx.line_to(lerp(x + wob, 540, lens), gy)
            else:
                ctx.line_to(x + wob, gy)
            ctx.stroke()
        if lens > 0:
            ctx.new_path(); ctx.save(); ctx.translate(lx, ly); ctx.scale(1, 0.16)
            ctx.arc(0, 0, 330, 0, 2 * math.pi); ctx.restore()
            ctx.set_source_rgba(0.7, 0.85, 1.0, 0.12); ctx.fill_preserve()
            ctx.set_source_rgba(0.9, 0.9, 0.9, 1); ctx.set_line_width(5); ctx.stroke()
            ctx.move_to(lx + 330, ly); ctx.line_to(lx + 420, ly + 80)
            ctx.set_line_width(14); ctx.stroke()
        burn = ease((t - 2.9) / 1.0)
        if burn > 0:
            halo(ctx, 540, gy - 10, 60 + 160 * burn, col=accent(), a=0.5 * burn)
            fl = 1 + 0.15 * math.sin(t * 19)
            h = 70 * burn * fl
            ctx.move_to(540, gy - h)
            ctx.curve_to(540 + 26 * burn, gy - h * 0.4, 540 + 18 * burn, gy, 540, gy)
            ctx.curve_to(540 - 18 * burn, gy, 540 - 26 * burn, gy - h * 0.4, 540, gy - h)
            ctx.set_source_rgba(*accent(), 1); ctx.fill()
        label(ctx, "scattered", 250, top - 20, 0.6 * (1 - lens), size=24, align="left")
    return Scene(draw, duration, "custom:focus_lens", f"{line1} / {line2}")


EPISODE = dict(
    title="Focus",
    accent=GOLD,            # one accent colour per video, saved for the payoff
    watermark="",           # e.g. "your channel name": drawn small and faint at the bottom
    scenes=[
        focus_lens("Scattered energy does nothing.", "Focused energy burns."),
        domino("One small habit.", "Changes everything.", first="1 habit", last="Your life"),
        planet_zoom("It feels huge right now.", "Zoom out.", problem="Your problem"),
        checklist(["Wake up early", "Move your body", "Read 10 pages", "Do the hard thing first"],
                  "Your morning decides your day."),
        spotlight("Everyone waits for the right time.", "Be the one who starts.",
                  accent_words={"starts."}),
    ],
)
