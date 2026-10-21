---
name: stickfigure-shorts
description: Write, animate and render complete motivational YouTube Shorts, TikToks and Reels in the minimal "glowing stick-figure on black" style as a finished 1080x1920 MP4 with an original generated music track. Two modes: (1) quote mode — a topic or quotes become 4–6 visual-metaphor scenes with word-by-word captions; (2) story mode — the user just tells a story ("A stickman struggles…", "0–3 seconds: …", "Final message: …") and gets one character's whole arc animated with a scroll-stopping hook, captions instead of voiceover, music timed to every beat and a message card. Use this whenever the user wants a new Short/Reel/TikTok "like the last one", "do the same", "again but this", an animated quote video, a stick figure motivation video, pastes a stick-figure story or narration, or wants another episode for their faceless animation channel — even if they don't mention stick figures or this skill by name.
---

# Stick-figure Shorts

Produces original ~30 s vertical videos: black background, white glowing pictogram
figures, one visual metaphor per scene, a short setup→payoff caption appearing word
by word, scenes joined by fade-to-black, one accent colour saved for the payoff.

Everything is rendered with code (pycairo + ffmpeg) by `scripts/engine.py` (45 scene
templates in `scenes*.py`, 31 props in `props.py`, 20 poses), so the real
work is *creative*: choosing the right picture for each idea. **The most common failure
of this skill is visual sameness** — reusing the same handful of scenes in every episode.
A faceless channel lives or dies on viewers thinking "I haven't seen that one before",
so treat variety as a hard requirement, not a nice-to-have (see step 3).

## Two modes — pick from the request
| The user gives… | Mode | Follow |
|---|---|---|
| a topic, a lesson, or a list of quotes | **Quote mode**: 4–6 independent visual metaphors | the workflow below |
| a story: a character, things that happen to him, a turning point, often "Final message: …" | **Story mode**: one continuous arc, 30–42 s | `references/story-mode.md` |

In story mode, **just make the video** — no questions. Missing captions → write them; missing music →
compose it; missing timings → choose them. Story mode builds on `scripts/storykit.py` (figures with
faces / tremble / head moves, front-view lifting rig, boxes, barbells, bench, road with a hill, finish
arch, signs, camera moves, darkness, impact effects, caption helpers) and `scripts/score.py` (original
music). Staging ideas: `references/story-recipes.md`; helper list: `references/story-api.md`;
six complete episodes with their music: `assets/story_examples/` (start with its README — it says
which one to borrow from for each kind of beat). Before the first render in a new output folder with no
`stickfigure_history.json`, copy `assets/channel_history.json` there under that name so the variety rules
know every episode already published.

**Music in both modes:** unless the user supplies a track, write `music_score.py` and render it with
`python3 SKILL_DIR/scripts/score.py music_score.py --out music.wav`, then pass `--music music.wav` to
the engine (see story-mode.md §4 for the arc and the loudness check).

## Every video opens with a very strong visual hook (both modes, mandatory)
The first 1.5 s must stop the scroll: frame 0 already shows a clear subject **close up and moving**,
a hard hit (impact, snap-out, spotlight slam, fall, reveal) lands at 0.4–0.8 s with a matching sound
(`s.hook_hit(t, "slam" | "snap" | "rewind")`), and caption line 1 adds tension from t=0. Pick one of the
10 hooks in **`references/hooks.md`** that fits this video's core tension and wasn't used in the last 3
episodes; name the first scene `hook-<kind>-<what>`. Before the final render it must pass
`python3 SKILL_DIR/scripts/hookcheck.py episode.py` (HOOK PASS) **and** the frame-0 thumbnail test
(look at frame 0 alone: is there a subject, and is something about to happen?). A FAIL is never
shipped — strengthen the opening and re-check.

## Setup (once per machine/session)

```bash
pip install -q pycairo numpy pillow   # ffmpeg must also be on PATH
```

`SKILL_DIR` below means this skill's directory.

## Workflow

### 1. Get the brief
What you need: a **topic or a set of quotes**. Nice to have: accent colour, channel
name for the watermark, a music file. Don't block on the extras — sensible defaults
are gold accent, no watermark, silent video. If the user only gives a topic, write
the quotes yourself.

Check what has already been used: if `stickfigure_history.json` exists in the output
folder (the engine writes it after every render), read it. It lists every previous
episode's templates and captions.

### 2. Write the captions
4–6 scenes, 28–35 s total, ~6 s each. Each scene gets **line 1 (setup)** and
**line 2 (payoff)**, 2–6 words each — the payoff is the twist or the lesson
("People see the result." → "Not the process."). Short lines matter because the text is
small and appears word by word; long sentences won't finish before the scene ends.
Never repeat a caption from the history.

### 3. Choose a visual for each scene — the variety rules
Work **from the idea to the picture**, not from the template list to the idea. Language
models tend to reach for the same first idea every time, so start with a random shortlist:

```bash
python3 SKILL_DIR/scripts/suggest.py --themes "<1-3 theme words, e.g. fear, time>" --n 12 \
    [--history <output folder>/stickfigure_history.json]
```
It shuffles the 45 templates and ~100 custom ideas from `references/visual-ideas.md` for
those themes, drops templates used in the last 3 episodes, leans 60/40 toward custom ideas
and adds wildcards from other themes. (`--list-themes` shows the 19 themes.) Pick from the
shortlist, or let it spark something new — the best scene is the one most surprising
while still readable in one second with the sound off. Read `visual-ideas.md` itself when
you want the full menu or the shot/motion vocabulary.

Rules for every episode:
- **Scene 1 is the hook** (see `references/hooks.md`): a custom hook scene, or the best-fitting scene
  wrapped with `hooked(scene, focus=(x, y))` from `storykit` — focus on the figure or moving object.
- **No template twice** in one episode, and **at most 3 template scenes**.
- **At least 2 scenes custom-built** — from the shortlist, the ideas bank, or newly
  invented — using the props, poses and helpers in `references/custom-scenes.md`.
  Custom scenes are what make a channel feel original.
- **Avoid any template used in the last 3 episodes** (the picker does this for you).
- **Mix it up:** at least 3 different motion types (journey, chain reaction, growth,
  transformation, zoom-out, physics, convergence, text-led…) and 2 shot types (wide, close
  → pull back, top-down, split, cutaway…). Five wide shots of a figure on a line is the trap.
- Don't fall back on the classic five (`stairs`, `iceberg`, `zone_exit`, `meter_drain`,
  `spotlight`) — they're the first ones any model reaches for, so they get stale fastest.
- Don't recreate the reference creator's signature scenes (listed at the end of
  `visual-ideas.md`) — copying risks copyright strikes and reused-content demonetisation.
  If asked for an exact copy, explain this and offer an original scene with the same point.

Show the user a compact plan table (scene · caption · visual · template or custom)
before rendering when they're iterating on ideas; if they just want a video, go ahead —
rendering takes about a minute and they can react to the result.

### 4. The templates (45) and the building blocks
`assets/template_gallery.png` shows one frame of every template;
`assets/props_gallery.png` shows the 31 props and 20 poses for custom scenes.
Every template takes `line1, line2` (setup / payoff), `duration=` and `t2=` (when the
payoff appears), plus the extras listed. Grouped by kind of motion:

| Motion | Templates (extras) |
|---|---|
| Journey / walking | `stairs` (steps, top_label) · `zone_exit` (zone) · `split_compare(top, bottom)` · `shortcut` (short, long_) · `lantern_walk` · `train_leaving` (sign) · `plank_bridge` (helper, planks) |
| Physics / action | `uphill` (load) · `jump_gap` (gap_label) · `domino` (first, last, count) · `scale_balance` (light, heavy) · `juggle` (balls, keep) · `bow_arrow` (setback) · `fall_rise` (falls) · `snowball` (start, end_label) |
| Breaking free / letting go | `chain_break` (weight) · `marionette` (control) · `backpack_drop` (burdens) · `rocket` (stages) · `tug_of_war` (left, right) |
| Transformation / growth | `cocoon` · `roots` (seen, hidden) · `bamboo` · `diamond` (pressure) · `paper_plane` (word) · `bloom_row` · `water_drop` (stone) · `inner_light` (doubts) |
| Reveal / camera | `mountain_reveal` (small) · `planet_zoom` (problem) · `iceberg` (tip, hidden) · `shadow_monster` (real) · `mirror` (reflection) |
| Atmosphere / light | `spotlight` (accent_words) · `lighthouse` · `candle` (label_text) · `kite` (winds) · `compass` (target) · `breathe` |
| Distraction / overload | `notification_swarm` · `meter_drain` (drains) |
| Top-down / text-led | `maze` (seed) · `habit_grid` (days, counter) · `checklist(items)` · `title_card` (accent_words, size) |

### 5. Write the episode file
Copy `assets/example_episode.py` to the working directory as a starting point — it
shows how templates and a custom scene (`focus_lens`) sit together. Replace its scenes
with yours; don't keep its scenes. Set `title`, `accent` (`GOLD`, `TEAL`, `RED` or any
RGB tuple 0–1) and `watermark`. Give custom scenes a name like
`Scene(draw, 6.4, "custom:lighthouse", caption)` so the history records them.

### 6. Preview and inspect before the full render
```bash
python3 SKILL_DIR/scripts/engine.py episode.py --preview preview.png
```
Open the PNG (one row per scene, 4 moments each) and check:
- captions fit and don't collide with the drawing; nothing is cut off at the edges
- the metaphor reads instantly; the focal point is lit and centred in y≈720–1560
- figures stand *on* their ground lines; no stray lines (see custom-scenes.md)
- the accent colour appears only at payoffs
- the six thumbnails in a row look different from each other — if two scenes look
  alike, swap one for a different shot or motion type

Then check the hook: `python3 SKILL_DIR/scripts/hookcheck.py episode.py` must print HOOK PASS, and
`python3 SKILL_DIR/scripts/contact.py episode.py 0,0.3,0.6,0.9,1.4 --out hook.png --cols 5` must show a
subject on frame 0 and a visible hit by 0.8 s.

For a closer look use `--frames 3.5,12.0 --outdir frames` (full-res PNGs). Fix and
re-preview; it's seconds per iteration.

### 7. Render and deliver
```bash
python3 SKILL_DIR/scripts/score.py music_score.py --out music.wav      # original score (default)
python3 SKILL_DIR/scripts/engine.py episode.py --out short.mp4 --music music.wav
#   or the user's own track: --music track.mp3 --music-start 12
```
The render appends the episode to `stickfigure_history.json` next to the video — keep
that file with the user's videos so future episodes can avoid repeats.
With `--music`, the audio is trimmed to the video and faded in/out. Default to an original score
from `scripts/score.py` (quote mode: ~120 BPM, a pad + piano arpeggio that builds and "drops" around the
midpoint, a hit on the payoff scene). Only leave the video silent if the user asks for that.

Save the MP4 where the user can open it, send it, and include a suggested title, a
one-line description and 3–5 hashtags.

## Style rules (and why)
Full measurements are in `references/style-guide.md`. In short:
- **Black background, grey/white figures, one accent colour.** Restraint is the brand;
  colour only means something if it's rare.
- **Fade to black between every scene** (handled by the engine). No hard cuts or swipes:
  the calm rhythm is the style.
- **Small captions in the top third, word by word.** The visual carries the idea; the
  text just names it.
- **One idea per scene, 4–6 scenes.** A list of metaphors, not one story.

## Troubleshooting
- `ModuleNotFoundError: cairo` → run the setup line.
- Text renders in a fallback font → Inter isn't installed; it still works. For the exact
  look install Inter (`fonts-inter` on Debian/Ubuntu).
- A line is too long → `words()` auto-shrinks it, but shorter copy is better.
