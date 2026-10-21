# API — one page

## engine.py (render, from the original stickfigure-shorts skill)
`Scene(draw, duration, name, caption)` · `EPISODE = dict(title, accent, watermark, scenes, fade_out,
black, fade_in, end_fade)` · CLI `engine.py episode.py --preview p.png | --frames 1,2 --outdir d |
--out v.mp4 [--music m.wav]`. Canvas 1080×1920, 30 fps; captions at y 600/662; content 720–1560.
Helpers: `caption words label halo beam ease eio clamp lerp mix polyline ellipse rounded_rect vgrad
accent figure walk run climb wave` and poses `STAND SIT SLUMP ARMS_UP PUSH PULL DANGLE PHONE CROUCH
LEAP KNEEL LIE CARRY THINK HEAD_IN_HANDS SIT_CHAIR`. Colours `GOLD TEAL RED`.

## storykit.py
| Group | Names |
|---|---|
| Poses | `TIRED BUCKLE SQUAT_CARRY REACH_FLOOR FALL HANDS_DOWN KNEEL_UP ONE_KNEE HALF_UP SIT_UP SIT_DOWN LOOK_HANDS SLUMP_SIT REST_SIT` |
| Arm sets (`pose_with(p, **ARMS)`) | `CARRY_ARMS HUG_ARMS HOLD_OUT POINT PALM_UP THROWN` |
| Pose helpers | `pose_with(p, **kw)` · `struggle_run(ph, lean)` · `carry_walk(ph, lean, arms)` · `slump_walk(ph)` · `hold_curl(k)` · `steps(t, starts, dur, stride) → (dist, ph)` |
| Side figure | `fig(ctx, x, ground, s, pose, col, a, d, lw, head_dx, knee_shake, hand_shake, face) → {head, hand_f, hand_b, knees, feet, hip, r}`; faces `strain closed open wide smile` |
| Front rig | `rig(x, ground, s, hip_h, feet, hands, build, nod, breath, elbow)` · `draw_body(ctx, j, col, a, smile)` · `deadlift_hip / deadlift_top` · `ik` · `stand_h` · `shoulder_w` · `front_face` |
| Placement | `probe(fn, *args)` (joints without drawing) · `layered(ctx, draw_fig, draw_props)` (props behind a figure) |
| Objects | `box stack barbell dumbbell bench road_sign finish_arch hanging_lamp` (+ `props.py`: sun moon star cloud rain tree trunk grass flower rock hill waves house lamp_post ladder signpost train boat phone coin heart key lock bird flame arrow speech_bubble thought_bubble trophy book backpack) |
| Environments | `floor(ctx, scroll, ground)` · `park(ctx, scroll)` · `Road(hc, hw, hh).y(x) / .draw(ctx)` · `stars(ctx, t, amt)` |
| Effects | `tremble(t, amt)` · `impact(ctx, imp, shake)` · `flash(ctx, imp, a)` · `settle(imp)` · `dust` · `strain_lines` · `sweat` · `confetti(ctx, t, x, y)` |
| Camera & text | `cam(ctx, z, wx, wy, sx, sy, clip)` · `zoom_lerp(a, b, k)` · `darkness(ctx, amt)` · `faded(ctx, a, fn)` · `cap(ctx, t, l1, l2, t2, a, accent_words)` · `phrase_beats(ctx, t, [(t0, text)…])` · `title_lines(ctx, t, [(t0, text)…], size, y0, gap, accent_words)` |
| Hooks | `hooked(scene, focus, z0, t_hit)` (wrap any scene) · `punch_zoom(t, t_hit)` · `speed_lines` · `spotlight_snap(ctx, x, top, ground, t, t_on) → lvl` · `rewind_glitch(ctx, t, t0, dur)` · `countdown(ctx, t, t0, text)` |
| Constants | `G = 1400` · `GREY` · `RIM` |

Draw order inside a scene: `ctx.save()` → `impact()` → `cam()` → environment → background characters
→ props behind → hero → props in front / effects → `ctx.restore()` → `darkness()` → `flash()` → captions.

## score.py
`Score(dur, seed)`; a score file defines `DUR`, optional `SEED`, `MARKS`, and `compose(s)`.
Instruments: `piano(t, midi, dur, vel)` · `notes(t0, [(dt, midi)…])` · `arp(t0, length, chord, step,
vel, octave, pattern)` · `pad(t0, chord, dur, gain, harmonics, attack)` · `bass(t0, midi, dur, vel)` ·
`kick(t, strength, length, f0, f1)` · `heartbeat(t, strength)` · `hat` · `clap`.
Story FX: `hook_hit(t, "slam"|"snap"|"rewind")` (every score) · `thud(t, strength)` · `whoosh(t, dur, gain)` (rises INTO t+dur) · `riser(t, dur, gain)` ·
`shimmer(t)` · `duck(t0, t1, every, depth)`. Chords: `AM C D DM EM F G GM BB C_MAJ_WIDE` (MIDI tuples).
CLI: `score.py music_score.py --out music.wav` → prints dB at each MARK.

## hookcheck.py / contact.py
`hookcheck.py episode.py` → lit0 / move0 / hit metrics, HOOK PASS or FAIL (exit 1). `contact.py episode.py t1,t2,… --out sheet.png [--cols N]` → frame sheet.
