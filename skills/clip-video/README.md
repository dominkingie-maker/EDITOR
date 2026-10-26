# Claude Clipping Tool ✂️

**Paste any long video link, and Claude finds the best moments and turns them into vertical
shorts** for YouTube Shorts, Instagram Reels and TikTok. It reframes each clip around the
speaker's face, and can add a clean, simple edit: smooth zooms, word-by-word captions in the
creator's brand colours, and a couple of subtle whooshes.

- 🧠 **Claude picks the moments.** It reads the whole transcript like an editor: hook → story → payoff.
- 📱 **Auto 9:16 reframing.** It finds camera cuts and keeps the speaker's face centred in every shot.
- ✨ **Optional simple edit.** Zooms, captions and sound effects, normalised for phone playback (-14 LUFS).
- 💸 **Free and local.** No API keys, no subscriptions, no uploads. It runs on your computer
  inside Claude Code.

---

## What you need
| | |
|---|---|
| **Claude Code** | the CLI or the desktop app ([claude.com/claude-code](https://claude.com/claude-code)) |
| **Python 3.10+** | [python.org](https://www.python.org/downloads/) (Windows: tick "Add Python to PATH") |
| **ffmpeg** | Windows: `winget install -e --id Gyan.FFmpeg` · Mac: `brew install ffmpeg` · Linux: `sudo apt install ffmpeg` |
| **Node.js** *(recommended)* | helps YouTube downloads. Windows: `winget install -e --id OpenJS.NodeJS.LTS` · Mac: `brew install node` |

## Setup (once)
```bash
git clone https://github.com/Plextrang/Claude-Video-Clipper.git
cd Claude-Video-Clipper
python install.py
```
`install.py` creates a private Python environment (`.venv`) and installs everything (yt-dlp,
faster-whisper, OpenCV). It changes nothing else on your system. The first transcription
downloads the Whisper speech model (~500 MB) once.

## Use it
Open the folder in Claude Code and say:

> **clip this video: https://www.youtube.com/watch?v=...**

Claude then works through the steps on its own:

1. **Downloads the audio and transcribes it** with word-level timestamps.
2. **Picks the best 3–8 moments.** Each is a self-contained idea that opens on a hook and ends on a payoff.
3. **Cuts them to 9:16** and reframes around the speaker → `output/<video>/clips/`
4. **Edits them** (zooms + captions + sound effects) → `output/<video>/edited/`
5. **Hands you a table** of clips, each with a ready-to-post caption.

You can also say things like:
- "clip this but only give me the 3 best" · "clips under 30 seconds"
- "don't edit them, just cut" · "no sound effects" · "captions lower / not all caps"
- "use #00E5FF as the caption colour"
- "clip this local file: C:/videos/podcast.mp4"

## Running it by hand (optional)
```bash
python run.py fetch "<url or file>"          # audio + transcript
# ...write output/<project>/clips.json (Claude does this; format in .claude/skills/clip-video/references/picking-moments.md)
python run.py cut  <project>                 # vertical clips
python run.py edit <project>                 # simple edit
python run.py find <project> "exact phrase"  # word-accurate timestamps
python run.py brand <project> --accent "#FFD60A"
```

## The simple edit
- **Zooms**: it opens with a quick zoom-out, then alternates wide and punched-in framing
  every few seconds on sentence ends, with a slow push in between. It always scales around
  the face.
- **Captions**: 1–3 words at a time in bold uppercase (Montserrat), popping in as they're spoken.
  The current word lights up in the accent colour, and key words stay highlighted. An `.srt` is
  included too.
- **Brand colours**: Claude uses the creator's known brand colour if it's confident about it.
  Otherwise the accent is pulled from the video's own colours, and it falls back to a classic
  short-form yellow.
- **Sound**: at most 2 quiet whooshes per clip. Swap in your own by dropping
  files into `assets/sfx/` (see the README there).

### Two render engines
| | `--engine python` (default) | `--engine remotion` |
|---|---|---|
| Look | same plan, same zooms, captions and audio | same (CSS text rendering) |
| Speed (20 s clip) | ~20 s | ~3 min |
| Extra install | none | Node.js + `python install.py --remotion` |
| License | MIT | Remotion is free for individuals and small companies; [larger companies need a license](https://www.remotion.dev/license) |

## Speed
Measured on a mid-range Windows laptop (CPU only):

| Video | Transcribe | Cut 6–7 clips | Simple edit |
|---|---|---|---|
| 10-min talking head | ~1.5 min | ~2.5 min | about as long as each clip |
| 88-min podcast | ~14 min | ~5 min | about as long as each clip |

The very first run also downloads the Whisper speech model (~500 MB) once. With an NVIDIA GPU,
`python run.py fetch <url> --device cuda` is faster (it needs the CUDA libraries).

## Troubleshooting
| Problem | Fix |
|---|---|
| `Sign in to confirm you're not a bot` | `python run.py fetch <url> --cookies-from-browser chrome` (or `firefox` / `edge`) |
| `ffmpeg not found` | install ffmpeg (see above), then **open a new terminal** |
| The download fails after a YouTube change | `.venv` pip upgrade: `python install.py` (it updates yt-dlp) |
| Captions are in the wrong place | ask Claude "move captions higher/lower", or use `--caption-y` |
| Wrong language detected | `python run.py fetch <url> --lang en --retranscribe` |

## Folder layout
```
.claude/skills/clip-video/   the skill Claude follows (SKILL.md + references)
clipper/                     python steps: fetch, cut, reframe, brand, plan, edit, sfx, find
remotion/                    optional Remotion render engine
assets/                      fonts (OFL), face-detection model (MIT), sound effects
output/                      your projects (gitignored)
```

## Please clip responsibly
Only clip and post videos you own or have permission to use. Respect creators' rights and each
platform's rules.

## Credits and licenses
- Code: MIT (see `LICENSE`).
- [Montserrat](https://github.com/JulietaUla/Montserrat) font: SIL Open Font License 1.1.
- [YuNet](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet) face detector: MIT.
- Built on [yt-dlp](https://github.com/yt-dlp/yt-dlp), [faster-whisper](https://github.com/SYSTRAN/faster-whisper),
  [OpenCV](https://opencv.org), [FFmpeg](https://ffmpeg.org) and, optionally, [Remotion](https://www.remotion.dev).
