# Recipes — story beats that worked

Every recipe below shipped in a finished episode. Coordinates: ground `G = 1400`, hero `S = 62`
(side view) or 56–58 (front view), others 58–60. Times `t` are seconds since the scene started.

## Contents
1. Hooks · 2. Struggle & falling · 3. Looking / noticing · 4. Hidden information & reveals ·
5. Giving, offering, refusing · 6. Carrying & loads · 7. Lifting (front view) · 8. Progress over
time · 9. Walking, steps, crossing · 10. Rest, relief, smiling · 11. Endings & message cards ·
12. Past episodes (avoid repeating their hooks)

---

## 1. Hooks
**Impact on frame ~0.55–0.75 s** (box slam, knees hitting the road):
```python
imp = t - t_hit
ctx.save(); impact(ctx, imp, shake=9)            # shake BEFORE cam
cam(ctx, 1.0 + 0.10 * math.exp(-5 * imp) if imp > 0 else 1.0 + 0.05 * eio(t / t_hit), ...)  # zoom punch
... b = settle(imp)                              # 0→1 with overshoot: knees buckle, stack squashes
pose = mix(CARRY, BUCKLE, b)
dust(ctx, x, G, imp / 0.7)
ctx.restore(); flash(ctx, imp, 0.2)
```
Something must already be moving on frame 0 (a box mid-air on a parabola, legs running, a box
coming down from someone's hands — start its path at negative time so it's on screen at t=0).
**Close-up → pull back**: `cam(ctx, zoom_lerp(2.3, 1.0, pull), lerp(head_x, wide_x, pull), ...)`
with `pull = eio((t - 0.85) / 1.1)`; frame 0 is the strained face, after the hit we see the world.
**World text**: `road_sign(ctx, SX, G, ["FINISH LINE", "AHEAD  →"])` filling the frame at zoom 2.0
on frame 0 while he stumbles past (`mix(struggle_run(...), FALL, 0.6 * trip)` — nearly falls).

## 2. Struggle & falling
- Shaking legs: `fig(..., knee_shake=tremble(t, 2.0))`; trembling hands `hand_shake=tremble(t*1.3, 2.5)`.
- Struggling run: `struggle_run(x / 26, lean=0.30)` while `x` advances ~150 px/s.
- Fall to knees: `mix(run_pose, FALL, eio((t-t0)/0.3))` → at impact `mix(FALL, HANDS_DOWN, ease(imp/0.12))`
  → later `KNEEL_UP` (panting: lean += 0.05·sin(9t)). Thud in the score on the impact time.
- Get up: HANDS_DOWN → ONE_KNEE → TIRED over ~1.2 s, tremble throughout.
- Collapse again: TIRED → FALL (0.15 s) → HANDS_DOWN, then slump: lean += 0.15.
- Defeated: sit `SIT_UP` → `SIT_DOWN` (head on knees), eyes `face="closed"` under a push-in.
- Strain: `strain_lines(ctx, head, r, a, t)`, `sweat(ctx, head, r, t, t0, ±1)` (front view close-ups).

## 3. Looking / noticing (stick figures can't show gaze)
- **Look at X**: halo on X (`halo(ctx, X, Y, 60–300, a=0.35*k)`) + head drop (lean +0.15–0.3) for
  things below; `head_dx` toward X for things behind (head peeks out past what he's carrying).
- **Look at A, then B**: two halos in sequence (1.3 s each) — others' empty hands, then his own stack;
  his shaking knees, then the empty bench.
- **Longing**: slow the walk next to the object (distance grows slower), halo on it, head peeks back.

## 4. Hidden information & reveals
- Hide: don't draw the object (`faded(ctx, finish_a, ...)` with `finish_a = 0`) + `darkness(ctx, 0.9)`
  over the right side in every shot from his point of view.
- **Crane reveal** (the camera "rises above him"): from a close-up on his head,
  `cam(ctx, zoom_lerp(2.2, 0.56, k), lerp(head_x, mid_x, k), lerp(head_y, G - 380, k), 540, lerp(1150, 1260, k))`,
  `k = eio((t-0.2)/4.0)`; stars brighten with k; darkness fades; the object fades in with gold glow.
  A dotted gold path from him to it (`16` dots appearing over 1.5 s) makes "only a few steps" literal.
- Reveal for the character: as he climbs, `darkness(0.9 * (1 - progress**1.5))` and fade the object
  in over the last 20 % of the climb; then a punch-in on his face (`face="wide"`) and a beat of silence.
- Use a `Road(hc, hw, hh)` hill: the crest is the natural occluder; put the reveal object 240 px past it.

## 5. Giving, offering, refusing
- Offer: grey figure facing the hero (`d=-1`) with `HOLD_OUT` arms, box at `hand_f` (+ ~22 px).
- Thrown onto a pile: box on a parabola from the giver's hands to `stack(...)`'s returned top.
- Pointing onward: `POINT` arms on a figure ahead on the path.
- **Saying no**: hero turns to face the giver (`d=-1`, giver comes from behind), raises `PALM_UP`
  (halo on the hand) and shakes his head `head_dx = 5–6·sin(2π·1.6–2.6·t)` for ~1 s.
- Disappointment: giver lean → 0.42 and arms drop (0.6 s), a pause (~1 s), then turns and carries the
  box away themselves (`CARRY` arms, walking off-frame).

## 6. Carrying & loads
- Tall stack in front: `stack(ctx, hand_f_x + w0*0.32, min(hand ys) + 6, boxes, tilt, sway, squash)`
  drawn *before* the figure (via `layered`) so the hands are in front.
- Tipping: `tilt = 0.17 * eio((t-2)/2.2) + 0.035·sin(5.2t)`, sway grows; steadying: damped
  `0.17·e^(−2.6u)·cos(6u)`.
- Hugged parcels covering the face: thin boxes from the hands up to the chin, drawn *after* the figure;
  the "one more" box on top hides the head.
- Setting it down: `SQUAT_CARRY`, stack base lerps from the hands to `G`; then the stack stays put.
- His own small box at the end: `box(..., rim=accent(), glow=0.8)` — the gold payoff.

## 7. Lifting (front-view rig)
- `rig(x, G, s, build=0..1, hands=[...], hip_h=...)` + `draw_body(ctx, j, col, smile=)`. Muscular
  lifters: `build=1`, grey; skinny hero `build=0`; growth over a montage: 0 → 0.32.
- Deadlift: `bar_y` from `G - R` to `deadlift_top(...)`, `hip_h = deadlift_hip(G, s, bar_y, grip, build)`,
  hands at `(x ± grip, bar_y)`; draw the body, then `barbell(...)` in front. Can't lift: hold the grip,
  `bend = 3.5 + 1.5 sin(9t)` on the bar, x shake, strain lines, sweat — the bar never leaves the floor.
- Overhead press / squat: hands targets around the shoulders; draw the bar first (behind).
- Tiny dumbbell pick-up (side view): stop where `probe(fig, 0, 0, S, REACH_FLOOR, d=-1)["hand"]` lands on
  it, crouch `REACH_FLOOR`, attach to `hand_f`, curl with `hold_curl(sin²)`. Glint: halo + `star()`.
- Payoff: bar rims and the overhead lamp lerp to `accent()`, gold halo; push in on the face and
  `smile` draws in (front view `front_face`).

## 8. Progress over time
Montage scene: stages of ~2 s each with a dim "blink" between (`faded(ctx, blink, ...)` with
`blink = ease(u/0.22)·ease((STAGE-u)/0.22)`), a `DAY n` label + progress dots, heavier weight and
slightly bigger `build` each stage. Caption: "So he came back." / "A little heavier every time."

## 9. Walking, steps, crossing
- Walk in place: world scrolls (`floor(ctx, scroll)` / `park(ctx, scroll)` with parallax trees);
  `ph = dist / 34`. Speed ramps make starting/stopping feel physical.
- **Countable steps**: `dist, ph = steps(t, STARTS, 0.6, stride)`; captions per step with
  `phrase_beats(ctx, t, zip(STARTS, ["One step.", "Then another.", "And another.", "Then another."]))`;
  the score puts a kick at each `start + 0.6` (the footfall).
- Uphill: `fig(ctx, x, ROAD.y(x), ...)`; camera follows `cam(ctx, 1.0, x + 200, ROAD.y(x) - 150)`.
- Crossing: `finish_arch(ctx, XF, ROAD.y)` + `confetti(ctx, t - t_cross, XF, y - 40)`; time the eased
  walk so he passes XF exactly on the score's shimmer.

## 10. Rest, relief, smiling
- Bench: `bench(ctx, x)` + `SLUMP_SIT → REST_SIT` (shoulders relax over 1.6 s, lean −0.06), slow
  breathing (lean ±0.02·sin(1.6t)), gold halo grows, bench rim lerps toward gold, the abandoned load dims.
- Smile: side view `face="smile"` (after `face="wide"` for disbelief); front view `front_face(smile=)`.
  Only in close-ups — push in first (zoom 1.6–2.6).
- "Nobody cheered": keep background characters doing their thing, untouched, while he smiles.

## 11. Endings & message cards
- Pull away: `zoom_lerp(1.4–1.5, 0.55, k)` up and back from the payoff, stars brighten, the scene fades
  (engine `fade_out`). 2.5–3 s, no caption.
- Card: `title_lines(...)` on black, 50–54 px; the final key line bigger (64–66) in gold, appearing
  ~1.9 s in on a warm music hit. A tiny gold callback object (dumbbell, line) is optional.
- If the message shares a scene with the last action (bench rest), fade the narrative caption out
  (`cap(..., a=1-ease((t-2.6)/0.4))`) and bring the message in at the caption positions.

## 12. Past episodes (vary hooks and set pieces)
| Episode | Hook | Set piece | Payoff in gold |
|---|---|---|---|
| You start to become strong (57 s) | skinny guy walks into a gym of muscular lifters | bar won't move · tiny dumbbell · DAY montage | bar rims + lamp at lockout, smile push-in |
| You can care without carrying everything (30 s) | box flies onto a swaying tower, slam | stack tips · palm "no" · others carry their own | his own small box |
| One more favor (30 s) | face close-up, box drops over it | bench he can't stop at · knees/bench halos | bench glow while resting |
| How close you are / Keep going (35–42 s) | knees slam the road · FINISH LINE AHEAD sign | crane reveal · darkness · steps · crest | finish arch, confetti |
