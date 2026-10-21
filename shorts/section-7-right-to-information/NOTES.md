# Section 7 - Right to Information

Talking-head explainer, 1080x1920, 48.5 s (45.5 s of speech plus a 3 s thank-you card), built from the
user's asset board: black / white / red, condensed bold type, torn paper, red brush strokes, film grain.
Edited with free247editor / Herk Edit Kit (HyperFrames + GSAP). Final: `section-7-right-to-information.mp4`.

## What the edit does

| Board | Edited time | Layout | Graphics |
| --- | --- | --- | --- |
| 01 Intro | 0-6.0 | full | SECTION 7 / RIGHT TO INFORMATION slams in with a brush underline; ROGIE DOMIN / PRESENTER lower third |
| 02 What it means | 6.0-14.2 | split | line-drawn government building and flag, document + magnifier, RIGHT TO KNOW stamp, PUBLIC MONEY callout |
| 03 Example | 14.2-19.2 | split | GOVERNMENT ALLOCATES, peso counter to 10,000,000 on "10 million pesos", FOR ROAD CONSTRUCTION, moving road and excavator |
| 04 Questions | 19.2-26.3 | split | three icon cards (ASA PADULONG ANG KWARTA? / GIUNSA PAGGASTO? / IS THE PROJECT ACTUALLY COMPLETED?) on each question |
| 05 Limitations | 26.3-32.5 | split | folders, CONFIDENTIAL stamp, padlock snaps shut on "protected", swaying scales |
| 06 Why it matters | 32.5-39.1 | split | TRANSPARENCY / ACCOUNTABILITY / HELPS PREVENT CORRUPTION icons drawn on each word |
| 07 Closing | 39.1-45.5 | full | slow push-in, THE GOVERNMENT SERVES THE PEOPLE + red/white callouts |
| 08 Thank you | 45.5-48.5 | card | brush-script Thank You!, red stroke, sun |

- **Cut:** six long pauses shortened to natural beats, the handling noise after "Thank you!" removed;
  no words cut, voice never sped up (`edit/edit-decisions.json`).
- **Clearer picture:** light denoise (hqdn3d), contrast, lanczos upscale 720x1280 to 1080x1920, sharpening.
- **Captions:** exact spoken words (including the Cebuano lines), 1-4 word phrases in condensed caps,
  black boxes with red callout boxes for key phrases, on the shirt in full layout and on the seam in split.
- **Sound:** original music bed (`edit/music_score.py`, the repo's `score.py` synth), ducked under the
  voice; synthesized paper tears, stamps, ticks and hits on each visual landing; -16 LUFS.

The recording starts mid-greeting, on "everyone"; "Good day" is not in the file, so the captions start there.
Spoken wording differs slightly from the written script ("Bill of Rights Section 7", "para sa construction
sa road", "giunsa ni siya paggasto", "actually being completed"); captions follow what was said, checked
with a Whisper pass (`edit/whisper_seg.py`).

## Rebuild

```sh
python edit/asr.py <sherpa-zipformer-dir> audio16k.wav asr.json
python edit/align.py edit/script.txt asr.json 49.5 <project>/assets/raw.json
python edit/cut.py <project>                  # cut + clarity grade -> assets/edited.mov, transcript.json
python skills/stickfigure-shorts/scripts/score.py edit/music_score.py --out <project>/assets/audio/music.wav
python edit/build.py <project>                # SFX, mix, index.html, cue-sheet.json
cd <project> && npx hyperframes render --quality high --output renders/final.mp4
```

`build.py` also needs the fonts (Anton, Oswald, Kaushan Script from Google Fonts) in `assets/fonts/` and
six grain tiles in `assets/grain/` (`ffmpeg -f lavfi -i color=c=gray:s=540x960 -vf noise=alls=80:allf=t+u -frames:v 6 g%d.png`).
