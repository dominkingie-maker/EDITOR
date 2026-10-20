# Writing custom scenes

A scene is any function `draw(ctx, t)` wrapped as `Scene(draw, duration, name, caption)`
(name like `"custom:lighthouse"` and the caption text are recorded in the episode history).
`ctx` is a pycairo context on a transparent 1080x1920 canvas; `t` is seconds since
the scene became visible. The engine adds the fades, bloom, watermark and
encoding — a scene only draws its own content. Put custom scenes directly in the
episode file (see the example at the bottom).

## Canvas layout
```
y=0     ┌──────────────┐
        │   (empty)    │
600/662 │  caption 1/2 │  ← TEXT_Y1 / TEXT_Y2 (baselines)
720     │ ┌──────────┐ │  ← CONTENT_TOP
        │ │ metaphor │ │     keep the main visual in this band, centred on CX=540
1560    │ └──────────┘ │  ← CONTENT_BOTTOM
1660    │  watermark   │
1920    └──────────────┘
```
Ground lines usually sit around y=1250–1350. A figure with `s=62` is ~180 px tall.

## Helpers (all from `engine`)
| Helper | What it does |
|---|---|
| `caption(ctx, t, line1, line2, t2=2.4, accent_words=())` | standard top captions, word-by-word |
| `words(ctx, text, y, t0, t, size=40, accent_words=())` | one animated centred line anywhere |
| `label(ctx, text, x, y, alpha, size=30, col, align)` | small static label |
| `figure(ctx, x, ground, s, pose, col=(1,1,1), alpha, d=±1, bob=0)` | stick figure; feet on `ground`; `d=-1` faces left; `bob` lifts it (jumps, hanging). Returns joints `head neck shoulder hip hand_f hand_b foot_f foot_b r` — attach ropes, strings, props, phones to them |
| poses `STAND SIT SLUMP ARMS_UP PUSH PULL DANGLE PHONE CROUCH LEAP KNEEL LIE CARRY THINK HEAD_IN_HANDS SIT_CHAIR`, cycles `walk(ph) run(ph) climb(ph) wave(ph)`, `mix(p, q, k)` | poses are dicts of joint angles (radians from straight down, + = toward facing direction; `hip` 0 standing → 1 sitting); `mix` blends; copy a dict and tweak keys for new poses |
| `camera(ctx, zoom, fx, fy)` | zoom the world around a fixed focal point — wrap in `ctx.save()/restore()` and draw captions after restoring. Animate `zoom` with `math.exp(lerp(log(a), log(b), eio(...)))` for a smooth pull-back |
| `ease(x)`, `eio(x)`, `clamp`, `lerp` | smoothstep (fades) / ease-in-out (movement) |
| `halo(ctx, x, y, r, col, a)` | soft radial glow behind something |
| `beam(ctx, x, top, ground, a, col)` | spotlight cone + floor pool (accent by default) |
| `polyline(ctx, pts, close)`, `ellipse`, `rounded_rect`, `vgrad(y0,y1,c0,c1)` | shapes & gradient fills |
| `accent()` | the episode's accent colour |

## Props (`from props import ...`, see `assets/props_gallery.png`)
Sky: `sun moon star cloud rain` · Nature: `tree trunk grass flower rock hill waves` ·
Built: `house lamp_post ladder signpost train boat` · Objects: `phone coin heart key lock
bird flame arrow trophy book backpack` · Text: `speech_bubble thought_bubble`.
Arguments follow one convention: `(ctx, x, y_or_ground, size..., a=alpha, t=time)`; a
parameter called `ground` means the prop stands on that line. Several have a built-in
animation input: `flower(bloom=0..1)`, `lock(open_=0..1)`, `book(open_=0..1)`,
`ladder(rungs=n)`, `bird(flap=phase)`, `flame(t=)`, `rain(t=)`, `waves(t=)`, `boat(t=)`,
`phone(glow=0..1)`. Read `scripts/props.py` for the exact signature before using one.

## Animation patterns
- **Progress over the scene:** `p = eio((t - 0.5) / (dur - 1.5))` → use for position.
- **Fade something in at time T:** `a = ease((t - T) / 0.4)`.
- **Walking:** `x = lerp(x0, x1, p)`; `figure(ctx, x, g, s, walk((x - x0) / 35))`.
  The divisor sets step length (≈35 px per half-step at s≈60) so feet don't slide.
- **Pose change:** `mix(SIT, STAND, eio((t - 1.6) / 0.8))`.
- **Reveal by clipping:** `ctx.save(); ctx.rectangle(...); ctx.clip(); ...; ctx.restore()`.
- Always `ctx.new_path()` (or use `polyline`/`ellipse`, which do) before building a
  path right after text — `show_text` leaves a current point and you'll get a stray
  line otherwise.
- Keep 0.5–1 s of stillness at the end of a scene so the fade-out isn't mid-action.
- Physics feel: accelerate falls with `k*k`, settle with a damped wobble
  `target + (start - target) * exp(-3u) * cos(9u)`, add a short screen shake on big impacts
  (`ctx.translate(0, 7 * exp(-8u) * sin(60u))`).
- Text-led scenes (lists, counters, single words) are a good breather between busy ones.
- The templates in `scripts/scenes_extra.py` and `scripts/scenes_more.py` are worked examples of each technique
  (`scenes_more.py` shows heavy prop use: `lighthouse`, `train_leaving`, `notification_swarm`, `lantern_walk`):
  chain reaction (`domino`), joint-attached props (`tug_of_war`, `marionette`, `candle`),
  clipping/splitting (`cocoon`), camera pull-back (`mountain_reveal`), screen-space zoom
  with stars (`planet_zoom`), procedural generation (`maze`), recursion (`roots`),
  damped physics (`scale_balance`). Read the closest one before writing something similar.
- `assets/example_episode.py` contains a complete custom scene (`focus_lens`).

## Look & feel rules
- Greys for everything secondary (0.15–0.5), white for the subject, accent only for
  the payoff. Big filled shapes should be dark (≤0.2) — bloom roughly doubles them.
- Labels inside the scene: 24–30 px; captions: 40 px.
- One focal point per moment; move the eye with light (halo/beam) rather than colour.

## Worked example — "roots before fruit" (now also the `roots` template)
```python
import math
from engine import Scene, caption, figure, STAND, ease, eio, label, accent

def roots(line1, line2, duration=6.4):
    def draw(ctx, t):
        caption(ctx, t, line1, line2, t2=2.8)
        gy = 1080
        ctx.set_line_width(3); ctx.set_source_rgba(0.6, 0.6, 0.6, 1)
        ctx.move_to(140, gy); ctx.line_to(940, gy); ctx.stroke()
        label(ctx, "what people see", 160, gy - 20, 0.6, size=22, align="left")
        label(ctx, "what you build", 160, gy + 40, 0.6, size=22, align="left")
        g = eio((t - 0.3) / 3.2)            # roots grow first...
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
        branch(560, gy, 0.0, 170, 5)
        s = eio((t - 3.4) / 1.4)            # ...then a small sprout
        if s > 0:
            ctx.set_line_width(5); ctx.set_source_rgba(*accent(), 1)
            ctx.move_to(560, gy); ctx.line_to(560, gy - 90 * s); ctx.stroke()
            ctx.arc(560 + 22 * s, gy - 85 * s, 16 * s, 0, 2 * math.pi); ctx.fill()
        figure(ctx, 400, gy, 58, STAND)
    return Scene(draw, duration, "custom:roots", f"{line1} / {line2}")

EPISODE = dict(scenes=[roots("Roots grow in silence.", "Long before anything shows.")])
```
