---
name: stickfigure-story-shorts
description: Turn a short written story about a stick figure (struggle → turning point → payoff, ending on a quote) into a finished 1080x1920 YouTube Short / Reel / TikTok — glowing stick figures on black, one gold accent, captions instead of voiceover, an original generated music track timed to the story, and a scroll-stopping visual hook in the first second. Use this whenever the user pastes a beat-by-beat stick-figure story or narration ("A stickman struggles…", "0–3 seconds: …", "Final message: …"), asks for an animated motivational short "with music only / no voiceover", says "do the same" / "again but this" / "one more" after a previous episode, or wants a story told through on-screen captions — even if they don't say "skill" or name the style.
---

# Stick-figure story Shorts

One character, one arc, 30–42 s: **hook → struggle → low point → turning point → payoff → message card.**
Rendering is code (pycairo + ffmpeg via `scripts/engine.py`); music is code too (`scripts/score.py`,
numpy synth, no samples, no licences). Your job is *direction*: staging each beat so it reads with
the sound off, timing the music to it, and checking frames before rendering.

```bash
pip install -q pycairo numpy pillow        # ffmpeg on PATH; Inter font optional (fonts-inter)
K=<this skill dir>/scripts                 # engine.py, storykit.py, score.py, contact.py, props.py
```

## Workflow

### 1. Beat sheet (in your head or as a table for the user)
Split the story into 6–9 scenes, one beat each. If the user gave timings, match them exactly
(scene durations = their ranges). Otherwise: hook 3–4 s, beats 3.5–6 s, final card 3.5–5 s.
- **Captions**: use the user's narration verbatim when given. Otherwise write two lines per scene —
  setup / payoff, ≤ 7 words each ("He fell. Got up. Fell again."). The message card uses the user's
  final message exactly, in caps, with the key word(s) in gold.
- Continuous moments (holding a pose while two caption sets play, sitting then the message) are one
  long scene with `cap(..., a=)` caption swaps — not two scenes with a fade between them.

### 2. Design the hook (frame 0 decides everything)
Frame 0 must already show **the subject in motion, close up**. Then a hit within 0.55–0.75 s.
Proven hooks (pick one that belongs to *this* story; don't reuse the last episode's):
- **Impact**: something slams (a box onto a stack, knees onto the road) → `impact()` shake +
  `flash()` + `dust()` + `settle()` buckle, music `whoosh` → `thud` on the same frame.
- **Readable world text**: a sign/label in close-up at zoom ≈2 ("FINISH LINE AHEAD →") while the
  character stumbles through frame; then pull back to the wide shot that contradicts it.
- **Extreme close-up → reveal**: zoom 2.2–2.6 on a strained face (`face="strain"`), an object drops
  over it, camera pulls back (`zoom_lerp`) to show the situation.
Never open on a title card, an empty frame, or a static wide shot.

### 3. Stage every beat so it reads in one second, sound off
Read `references/recipes.md` — it maps story beats to working techniques (looking at something,
hidden information, offering/refusing, picking things up, lifting, growth montage, crane reveal,
sitting & relaxing, smiling, crossing a line, step-by-step captions). Key rules:
- **Stick figures can't show gaze.** Show "he looks at X" with a soft `halo` on X, a lean/head drop,
  and `head_dx` (head peeks toward X). Show feelings with posture, tremble, and — only in close-ups
  (zoom ≥ 1.6) — `face=` strain / closed / open / wide / smile.
- **Hidden information must be truly hidden.** If the character "can't see" something, don't draw
  it at all (`faded(ctx, 0, …)`), *and* darken that side with `darkness()`; fade it in only at the reveal.
- **Readable left-to-right staging.** Giver — hero — object, never hero reaching across the object
  to someone behind it; turn the hero (`d=-1`) instead.
- **Gold is the payoff.** Everything is grey/white until the turning point or the reward; then gold
  on exactly that (the finish line, the hero's own small box, the bar locking out, the bench glow).
- Secondary characters are grey (`GREY`), slightly smaller (s ≈ 58 vs 62), and never stay in focus.

### 4. Score the music to the scene timeline
Write `music_score.py` (see `examples/keep_going/music_score.py`) with `compose(s)`, using the scene
start times. The arc that works: hit on the hook → sparse minor (heartbeat or slow kick for struggle)
→ thuds on falls → near-silence at the low point → riser → **one beat of silence** at the moment of
realisation → warm major section for the payoff (shimmer on the crossing/lift) → soft resolve under
the message card, with a warm hit when the key line appears. Kicks on footfalls when he walks.
```bash
python3 $K/score.py music_score.py --out music.wav     # prints dB at MARKS
```
You cannot listen — the dB report is your ears: intro −22…−26, build −15…−18, payoff −12…−14,
silence beats ≤ −25. If a section is the wrong level, change its gains and re-run.

### 5. Write the episode
`from storykit import …` and `from engine import GOLD, Scene`. One function per scene returning
`Scene(draw, duration, "custom:name", caption)`. World drawing goes inside
`ctx.save(); cam(...); …; ctx.restore()`; captions, `darkness()` and `flash()` after restoring.
Set quicker fades for short beats: `EPISODE = dict(..., fade_out=0.25–0.3, black=1/30, fade_in=0.3–0.35, end_fade=0.5–0.6)`.
`references/api.md` lists every helper; `examples/keep_going/episode.py` is a complete 9-scene episode.

### 6. Check frames, fix, then render
```bash
python3 $K/contact.py episode.py 0,0.7,3,5.4,8.3,11.5,15.5,19.6,23.3,28.9,32.8,38 --out sheet.png
```
Look at the sheet (Read the PNG). Pick times at frame 0, every impact, reveal, caption change and
the end card. Check: hook frame has motion + subject; nothing the hero "can't see" is visible early;
props sit in hands / on the ground; feet on the ground line; nothing zoomed pokes into the caption
band (cam clips at y=705 — keep it on); captions fit; gold only at the payoff. Fix and re-check
(seconds per iteration), then:
```bash
python3 $K/engine.py episode.py --out short.mp4 --music music.wav
ffprobe -v error -show_entries format=duration -of csv=p=0 short.mp4
```

### 7. Deliver
Send the MP4. Summarise as a table (time · what happens · caption), name the hook, explain any
creative substitutions (how "looks at" or "smiles" was shown), say plainly that the music was
checked by loudness report, not by ear. Add a title, one-line description and 3–5 hashtags.
Keep each episode in its own folder (`episode.py`, `music_score.py`, `music.wav`, the MP4,
`stickfigure_history.json`); a new version of a story gets a new folder, not an overwrite.

## Gotchas (each one cost a re-render once)
- Camera zoom pushes world art into the captions → keep `cam(..., clip=True)` (default).
- The finish line showed through the "darkness" → don't rely on darkness alone; don't draw it.
- A prop meant for a hand floated → `probe(fig, x, G, S, POSE, d=-1)["hand_f"]` gives the exact hand
  position for a pose; place the object (or the standing x) from that.
- Props drawn over the figure's hands look wrong when they should be held → `layered()` draws the
  figure into a group, props behind using its joints, figure on top. Parcels *hugged* in front of the
  body (covering face) are drawn after the figure instead.
- `show_text` leaves a current point → `ctx.new_path()` before any path after text (helpers do).
- Walking in place: scroll the world (`floor(ctx, scroll)` / camera follow) and drive the walk phase
  from distance (`ph = dist / 30`), or use `steps()` for discrete, countable steps.
- Mixing poses with different `hip` values for >0.8 s makes feet float/sink — keep transitions short
  or go through a matching intermediate pose (e.g. SIT → HANDS_DOWN → TIRED).
- Story longer than 35 s is fine for Shorts (< 60 s); tell the user and offer to tighten.
