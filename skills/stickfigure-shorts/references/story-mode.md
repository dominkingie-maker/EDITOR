# Story mode — a whole Short from a told story

The user tells a story ("A stickman struggles to run… he sits… the camera rises… Final message: …")
and expects a finished video back. **Don't ask questions — make it.** No captions given → write them.
No music given → compose an original score. No timings given → choose them. Deliver the MP4.

One character, one arc, 30–42 s: **hook → struggle → low point → turning point → payoff → message card.**
Building blocks: `scripts/storykit.py` (rigs, poses, props, worlds, camera, effects, captions),
`scripts/score.py` (numpy music synth), `scripts/contact.py` (frame sheets). One-page list of every
helper: `references/story-api.md`. Staging techniques per beat: `references/story-recipes.md`.
Complete worked episode: `assets/story_example/episode.py` + `music_score.py` (9 scenes, 41.8 s).

## 1. Beat sheet
Split the story into 6–9 scenes, one beat each. If the user gave timings ("0–3 seconds: …"), match
them exactly. Otherwise: hook 3–4 s, beats 3.5–6 s, final card 3.5–5 s; total 30–42 s.
- **Captions**: the user's narration verbatim when given. Otherwise two lines per scene — setup /
  payoff, ≤ 7 words each ("He fell. Got up. Fell again."). The message card is the user's final
  message exactly, in caps, the key words in gold.
- A continuous moment (holding a pose while two caption sets play; sitting, then the message) is one
  long scene with `cap(..., a=)` caption swaps, not two scenes with a fade between them.

## 2. The hook (frame 0 decides everything) — full playbook in `references/hooks.md`
Frame 0 shows **the subject, close, already moving**; a hit lands within 0.55–0.75 s. Pick a hook that
belongs to this story and differs from the past episodes table in `story-recipes.md` §12:
- **Impact**: a box slams onto a stack / knees hit the road → `impact()` shake + `flash()` + `dust()` +
  `settle()` buckle; score `whoosh` → `thud` on the same frame.
- **Readable world text**: a sign in close-up at zoom ≈ 2 ("FINISH LINE AHEAD →") as he stumbles past;
  pull back to the wide shot that contradicts it.
- **Extreme close-up → reveal**: zoom 2.2–2.6 on a strained face, something drops over it, pull back.
Never open on a title card, an empty frame or a static wide shot. Seven more hook types (smash from
black, sprint at camera, countdown, giant vs tiny, flash-forward with a rewind glitch, split contrast,
mid-fall) are in `hooks.md`. Name the first scene `hook-<kind>-<what>`; put `s.hook_hit(t_hit, kind)`
in the score.

## 3. Stage each beat to read in one second, sound off
- **Gaze can't be drawn.** "He looks at X" = soft `halo` on X + lean/head drop + `head_dx` toward X.
  Feelings = posture, tremble, and only in close-ups (zoom ≥ 1.6) `face=` strain/closed/open/wide/smile.
- **Hidden means not drawn.** If he can't see something, don't draw it (`faded(ctx, 0, …)`) *and* add
  `darkness()` on that side; fade it in only at the reveal (crane shot, reaching the crest).
- **Left-to-right staging**: giver — hero — object; turn the hero (`d=-1`) rather than reach across.
- **Gold = the payoff only** (the finish line, his own small box, the bar locking out, the bench glow).
- Secondary characters grey (`GREY`), s ≈ 58 vs hero 62.

## 4. Score the music to the scenes
Write `music_score.py` (`DUR`, `SEED`, `MARKS`, `compose(s)`) using the scene start times. The arc:
hit on the hook → sparse minor (heartbeat / slow kick while struggling) → `thud` on every fall →
near-silence at the low point → `riser` → **one beat of silence** at the realisation → warm major for
the payoff (`shimmer` on the crossing / lift) → soft resolve under the card, warm hit when the key
line appears. Kicks on footfalls when he walks (`steps()` gives the times).
```bash
python3 SKILL_DIR/scripts/score.py music_score.py --out music.wav     # prints dB at each MARK
```
You can't listen; the dB report is your ears: intro −22…−26, build −15…−18, payoff −12…−14,
silence beats ≤ −25. Adjust gains and re-run until the curve matches the story.

## 5. Write the episode
```python
from storykit import (...)            # see story-api.md
from engine import GOLD, Scene
def s1_hook(duration=3.5):
    def draw(ctx, t):
        ctx.save(); impact(ctx, t - 0.75); cam(ctx, z, wx, wy)   # world space
        ...environment, background figures, props, hero, effects...
        ctx.restore(); darkness(ctx, amt); flash(ctx, t - 0.75)  # screen space
        cap(ctx, t, "Line one.", "Line two.", 1.2)
    return Scene(draw, duration, "custom:hook_name", "Line one. / Line two.")
EPISODE = dict(title=..., accent=GOLD, watermark="", scenes=[...],
               fade_out=0.3, black=1/30, fade_in=0.35, end_fade=0.6)   # quicker fades for short beats
```

## 6. Check frames, fix, render
```bash
python3 SKILL_DIR/scripts/contact.py episode.py 0,0.7,3,5.4,8.3,12.5,15.5,19.6,23.3,28.9,32.8,38 --out sheet.png
```
Read the sheet. Times: frame 0, every impact, reveal, caption change, the end card. Check: the hook
frame has motion and a subject; nothing he "can't see" shows early; held props sit in hands; feet on
the ground line; nothing zoomed enters the caption band (`cam` clips at y=705 — keep it); captions
fit; gold only at the payoff. Then the hook gate: `python3 SKILL_DIR/scripts/hookcheck.py episode.py`
must print HOOK PASS (never ship a FAIL). Fix and re-check (seconds each), then:
```bash
python3 SKILL_DIR/scripts/engine.py episode.py --out short.mp4 --music music.wav
```

## 7. Deliver
Send the MP4 with a table (time · what happens · caption), name the hook, explain substitutions
(how "looks at" or "smiles" was shown), say the music was checked by loudness report, not by ear,
and add a title, a one-line description and 3–5 hashtags. One folder per episode (`episode.py`,
`music_score.py`, `music.wav`, MP4, `stickfigure_history.json`); a new version of a story gets a
new folder.

## Gotchas (each cost a re-render once)
- Zoom pushes world art into the captions → keep `cam(..., clip=True)`.
- The reveal object showed through `darkness()` → don't draw it until the reveal.
- A held prop floated → `probe(fig, x, G, S, POSE, d=-1)["hand_f"]` gives the exact hand position.
- Held props should sit *behind* the hands → `layered()`; parcels hugged over the face go *after*.
- Walking in place: scroll the world (`floor/park(ctx, scroll)`) or follow with the camera; drive
  the walk phase from distance (`ph = dist / 30`) or use `steps()` for countable steps.
- Blending poses with different `hip` for > 0.8 s makes feet float — go through a matching pose
  (SIT → HANDS_DOWN → TIRED).
- Stereo buffers: `score.py` already handles them; if you write raw numpy audio, slice the last axis.
