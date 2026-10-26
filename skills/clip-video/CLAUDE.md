# Claude Clipping Tool

This repo turns long videos into vertical short-form clips. When the user pastes a video link or
file, or asks for clips, shorts, reels or TikToks, **use the `clip-video` skill**
(`.claude/skills/clip-video/SKILL.md`) and follow it end to end without stopping for confirmation.

- Run everything through `python run.py <command>` from the repo root. Setup is `python install.py`.
- Results go to `output/<project>/` (gitignored). Never commit or upload user videos.
- Long steps (transcription, rendering) should run in the background, with a progress update to the user.
