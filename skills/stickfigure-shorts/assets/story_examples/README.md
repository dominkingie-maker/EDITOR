# Story examples — every finished story episode, complete and runnable

Each folder is the full source of a published-quality Short: `episode.py` (all scenes) and its music
(`music_score.py` for `scripts/score.py`, or an older standalone `music.py`). Copy a folder next to
your output, read it, and borrow techniques — don't re-render them as new episodes.

```bash
cp -r SKILL_DIR/assets/story_examples/keep-going my-episode && cd my-episode
python3 SKILL_DIR/scripts/score.py music_score.py --out music.wav     # or: python3 music.py music.wav
python3 SKILL_DIR/scripts/hookcheck.py episode.py
python3 SKILL_DIR/scripts/engine.py episode.py --out short.mp4 --music music.wav
```

| Folder | Length | Hook | Borrow it for | Music |
|---|---|---|---|---|
| `discipline-makes-no-noise` | 37 s | **Flash-forward** → rewind glitch | being mocked (look-back + "HA!" bubbles), falls, DAY montage (rain, worn-shoe close-up, night, dawn), a character passing others on the drop, `shoes()` | `music_score.py` |
| `keep-going` | 41.8 s | **Lying sign** (FINISH LINE AHEAD) + stumble | two falls, giving up, crane reveal, darkness hiding the goal, countable steps with `phrase_beats`, smile at the crest, crossing + confetti, two-part end card | `music_score.py` |
| `how-close-you-are` | 35 s | **Impact**: knees slam the road | the same story built directly (before storykit): `Road` hill, finish arch, crane, darkness | `music.py` |
| `one-more-favor` | 30 s | **Face → box drop**: extreme close-up, a box covers his face | hugged parcels, bench he can't stop at, someone pointing onward, halos on knees/bench, refusing, others' disappointment, sitting & relaxing in gold | `music.py` |
| `care-without-carrying` | 30 s | **Slam**: a box flies onto a swaying tower | carrying a tall stack, tipping & steadying, the palm-up "no" with a head shake, others carrying their own, his small gold box | `music.py` |
| `start-to-become-strong` | 57 s | ⚠ none — a calm walk-in (FAILS `hookcheck`; made before the hook rules) | the **front-view lifting rig** (skinny → muscular `build`), barbells & deadlifts, failing a lift (bar flex, strain lines, sweat), tiny-dumbbell pickup, DAY montage with growth, gold lockout + smile push-in. **Never copy its opening** — give it a hook from `references/hooks.md` | silent (made before music) |

`assets/channel_history.json` lists all of these episodes (titles, scene names, captions). Copy it into
your output folder as `stickfigure_history.json` when that folder has none, so the variety rules
(no repeated hook or template in the last 3 episodes) know what the channel has already used.
