# Section 4 of the Bill of Rights

Talking-head explainer, 1080x1920, 53.4 s (48.4 s of speech plus a 5 s end card).
Edited with free247editor / Herk Edit Kit (HyperFrames + GSAP). Final: `section-4-bill-of-rights.mp4`.

## What the edit does

- **Cut:** removes the 1.9 s silent lead-in and the tail after "Thank you!", and shortens five long
  pauses to natural beats (0.20-0.32 s). No words are cut and the voice is never sped up.
  Every decision with its reason is in `edit/edit-decisions.json`.
- **Picture:** upscaled 720x1280 to 1080x1920, light contrast/warmth grade, slow push-in, and hard
  punch-ins on "It allows us to share our opinions freely", "important because...", and "Thank you!".
- **Hook (0-3 s):** a SECTION 4 / Bill of Rights, Article III card is on screen from the first frame;
  the 4 pulses when she says it.
- **Five freedoms:** Speech, Expression, Press, Assembly, Petition land as chips on each spoken word,
  then fly up into a 0/5 tracker. Each gets a gold check when she explains it (speak, express,
  the press, gather, government) until 5/5 on "community".
- **Payoff beats:** "Speak up" and "Share thoughts" bricks hold up "Better society"; a balance scale
  tips on "freedom" and levels on "respect the rights of others".
- **End card:** the actual text of Article III, Section 4 of the 1987 Philippine Constitution.
- **Captions:** 1-3 word phrases on the shirt, never over the mouth, exact script wording, gold for
  the rights, blue for actions, green for the payoff, serif for the greetings.
- **Sound:** voice high-passed and lightly compressed (no noise reduction: it blurred consonants),
  soft synthesized taps/ticks/knocks on each visual landing, mastered to -16 LUFS. No music.

## Rebuild

Word timings come from a local sherpa-onnx zipformer pass aligned to the known script
(`edit/script.txt`), so captions use the script's exact words.

```sh
python edit/asr.py <sherpa-model-dir> audio16k.wav asr.json
python edit/align.py edit/script.txt asr.json 53.033 <project>/assets/raw.json
python edit/cut.py <project>                 # frame-accurate cut + grade -> assets/edited.mov, transcript.json
python edit/build.py <project>               # SFX, mix, index.html, cue-sheet.json
cd <project> && npx hyperframes render --quality high --output renders/final.mp4
```

## Checks on the delivered file

- 1080x1920, 30 fps, 53.43 s video and audio; -16.0 LUFS integrated, -1.4 dBFS peak.
- Fresh transcription of the final mix contains every scripted word across all five pause cuts.
- Frames inspected at every beat, plus a frame strip across the chip-to-tracker change: nothing
  covers the mouth, and captions stay on the shirt.

`align.py` places the first three words from a second pass (speech starts at 2.0 s; the first pass
put "Hello" in the silent lead-in). `<project>` is a Herk Edit Kit video project with the raw
recording at `assets/raw.mp4` (the raw footage is not committed).
