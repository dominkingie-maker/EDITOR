# Hooks — every video, both modes, no exceptions

A viewer decides in ~1 second whether to keep scrolling. The first 1.5 s of every video is a
designed **hook**: a subject, already in trouble or in motion, and a hard visual hit that lands with
the music. Nothing else in the video matters if this fails, so design it first and verify it last.

## The rules
1. **Frame 0 is the thumbnail.** A clear subject (the character, his face, the object of the story)
   fills a big part of the frame — zoom ≥ 1.8 or a figure ≥ 25 % of the content band. Never black,
   never empty, never a title card, never a calm wide shot, never a fade-in.
2. **It's already moving on frame 0.** Start animations at negative time (a box already mid-air, legs
   already running, a stack already swaying, the camera already creeping in).
3. **A hit lands at 0.4–0.8 s**: impact, snap-out, reveal, light slamming on, a fall. Shake + flash +
   dust or a hard camera move. `score.hook_hit(t_hit, kind)` puts the sound on the same frame.
4. **It poses a question** the rest of the video answers: Will he fall? What's behind the hill? Why
   is the sign lying? Line 1 of the caption starts at t=0 and adds tension, not context.
5. **It belongs to this story** and differs from the last 3 episodes' hooks (check the first scene
   names in `stickfigure_history.json`; name your first scene `hook-<kind>-<what>`).
6. **It passes the gate:** `python3 SKILL_DIR/scripts/hookcheck.py episode.py` → HOOK PASS, *and* the
   frame-0 thumbnail test: open frame 0 alone — would you stop on it? If you can't say what the
   subject is and what's about to happen, redesign.

## The 10 hooks (pick the one that fits the story's core tension)
| # | Hook | Frame 0 | The hit (0.4–0.8 s) | Tools | Sound |
|---|---|---|---|---|---|
| 1 | **Slam** | object mid-air above an overloaded character | it lands: shake, flash, dust, knees buckle | `impact flash dust settle punch_zoom` | `hook_hit(t,"slam")` |
| 2 | **Face → pull-back** | extreme close-up (2.2–2.6) of a strained / scared face | something covers it or the camera rips back to reveal the situation | `cam zoom_lerp fig(face=)` | slam |
| 3 | **Lying sign** | readable world text in close-up ("FINISH LINE AHEAD →", "ALMOST THERE", "YOU'RE LATE") | stumble / pull back to a wide shot that contradicts it | `road_sign` | snap |
| 4 | **Mid-fall** | figure already falling / leaping over a gap / a tower past its tipping point | catch, crash or freeze-frame + flash | `FALL LEAP stack(tilt) impact` | slam |
| 5 | **Smash from black** | a silhouette at the edge of a dim beam, flickering | the spotlight slams on, the figure is in a dramatic pose | `spotlight_snap halo` | snap |
| 6 | **Sprint at camera** | figure running hard, speed lines, camera tracking | a trip / a wall / a door slams — hard stop with shake | `speed_lines struggle_run impact` | slam |
| 7 | **Countdown** | a huge number popping in ("3", "DAY 1", "0:05") behind the figure | the number hits zero / changes and the action starts | `countdown` | snap per number |
| 8 | **Giant vs tiny** | a tiny figure under a gigantic thing (stack, wave, wall, shadow) that is moving | it lurches / looms closer with a camera punch | `stack halo punch_zoom` | slam |
| 9 | **Flash-forward** | the climax for 0.8 s (collapse at the line, the bar crashing, the box falling) | tape-rewind glitch back to the start | `rewind_glitch` | `hook_hit(t,"rewind")` |
| 10 | **Split contrast** | two versions side by side (gives up / keeps going) | one collapses or goes dark with a hit | clip halves, `impact` on one side | slam |

Quote mode (templates): when no custom hook fits, wrap the first scene —
`hooked(scene, focus=(x, y), z0=2.4, t_hit=0.6)` starts tight on `focus` and slams out with shake +
flash. Point `focus` at the figure or the object that's moving at t=0, never at empty space or bare
lines; this wrapper is the minimum, a designed hook (table above) is better.

## Recipes
**Slam** (story mode, as in "You can care without carrying everything"):
```python
imp = t - T_HIT
ctx.save(); impact(ctx, imp, 9); cam(ctx, punch_zoom(t, T_HIT), wx, wy)
pose = mix(CARRY, BUCKLE, 0.15 + 0.85 * settle(imp))
# incoming box on a parabola that started at t = -0.45 so it is on screen at frame 0
... ctx.restore(); flash(ctx, imp, 0.22)
```
**Face → pull-back**: `cam(ctx, zoom_lerp(2.4, 1.0, eio((t-0.85)/1.1)), lerp(head_x, wide_x, k), ...)`,
`face="strain"` until the hit.
**Smash from black** (a dim beam alone is too still — it needs the tight creeping camera):
```python
ctx.save(); impact(ctx, t - 0.5); cam(ctx, punch_zoom(t, 0.5, base=1.9, pre=0.12), x, G - 80, 540, 1150)
lvl = spotlight_snap(ctx, x, 720, G, t, 0.5)          # buzzing ≈0.3 before, slams to 1 at 0.5 s
faded(ctx, 0.15 + 0.85 * lvl, lambda: (floor(ctx), fig(ctx, x + tremble(t, 1.5), G, 62, ONE_KNEE, face="strain")))
ctx.restore(); flash(ctx, t - 0.5)
```
**Flash-forward**: scene 1 plays the climax as its own impact (the fall / the crash, zoom ≈1.8,
`impact` + `flash` at ~0.35 s), then `rewind_glitch(ctx, t, 0.8, 0.5)` as the LAST call in draw (it
tears what's already drawn), then the normal opening from 1.3 s; caption line 1 at 1.3 s ("How did he
get here?"). Score: `hook_hit(0.35, "slam")` and `hook_hit(1.3, "rewind")`.
**Countdown**: `countdown(ctx, t, 0.0, "3")`, `"2"` at 0.35, `"1"` at 0.7 (each with `hook_hit(t,"snap")`),
then the action.

## Verify (mandatory before the final render)
```bash
python3 SKILL_DIR/scripts/hookcheck.py episode.py          # metrics + HOOK PASS / FAIL (exit 1)
python3 SKILL_DIR/scripts/contact.py episode.py 0,0.3,0.6,0.9,1.4 --out hook.png --cols 5
```
Tested tools: slam, face pull-back, lying sign, sprint + countdown, spotlight (with creep) and
flash-forward all PASS as written above. Calibration: strong shipped hooks score lit0 5–13 %, move0 2.8–7.6, hit 8–64 at 0.6–0.8 s; a calm
walk-in scored hit 2.3 and failed. FAIL → make frame 0 tighter / busier, start motion earlier, add a
flash or a bigger camera snap at the hit — then run it again.
