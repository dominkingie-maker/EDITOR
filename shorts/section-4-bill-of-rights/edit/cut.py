"""Frame-aligned cut: keep [start,end] minus removed pause middles. Writes EDL, retimed transcript, runs ffmpeg once.
Usage: cut.py project_dir"""
import json, subprocess, sys
P = sys.argv[1]; FPS = 30
fr = lambda t: round(t * FPS) / FPS
START, END = 1.93, 51.80
# (source silence, reason) -> middle removed, natural beat kept on both sides
REMOVE = [
    (13.17, 13.48, "sentence break after 'petition.' 0.61s -> 0.30s"),
    (32.42, 32.64, "pause after 'government' 0.46s -> 0.24s"),
    (35.33, 35.76, "sentence break after 'community.' 0.75s -> 0.32s"),
    (41.85, 42.10, "hesitation between 'help' and 'build' 0.45s -> 0.20s"),
    (43.90, 44.18, "sentence break after 'society.' 0.59s -> 0.31s"),
]
keep, t = [], fr(START)
for a, b, _ in REMOVE:
    keep.append((t, fr(a))); t = fr(b)
keep.append((t, fr(END)))
def remap(x):
    out = 0.0
    for a, b in keep:
        if x < a: return out
        if x <= b: return out + x - a
        out += b - a
    return out
raw = json.load(open(f"{P}/assets/raw.json"))
words = [{"text": w["text"], "start": round(remap(w["start"]), 3), "end": round(remap(w["end"]), 3),
          "src_start": w["start"], "src_end": w["end"]} for w in raw["words"]]
dur = round(sum(b - a for a, b in keep), 3)
json.dump({"text": raw["text"], "audio_duration_secs": dur, "words": words}, open(f"{P}/assets/transcript.json", "w"), indent=1)
json.dump({"fps": FPS, "source": "assets/raw.mp4", "keep": keep, "duration": dur,
           "cuts": [{"source_start": fr(a), "source_end": fr(b), "reason": r} for a, b, r in REMOVE] +
                   [{"source_start": 0, "source_end": fr(START), "reason": "silent lead-in before 'Hello'"},
                    {"source_start": fr(END), "source_end": 53.033, "reason": "silence after 'Thank you!'"}]},
          open(f"{P}/assets/edit-decisions.json", "w"), indent=1)
vexpr = "+".join(f"between(n,{round(a * FPS)},{round(b * FPS) - 1})" for a, b in keep)
achain = "".join(f"[0:a]atrim={a:.5f}:{b:.5f},asetpts=PTS-STARTPTS,afade=t=in:d=0.005,afade=t=out:st={b - a - 0.005:.5f}:d=0.005[a{i}];"
                 for i, (a, b) in enumerate(keep)) + "".join(f"[a{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=0:a=1[a]"
grade = "eq=contrast=1.07:brightness=0.015:saturation=1.12:gamma=1.03,colorbalance=rm=0.025:bm=-0.02,scale=1080:1920:flags=lanczos,unsharp=5:5:0.45"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{P}/assets/raw.mp4", "-filter_complex",
    f"[0:v]select='{vexpr}',setpts=N/{FPS}/TB,{grade},format=yuv420p[v];" + achain,
    "-map", "[v]", "-map", "[a]", "-r", str(FPS), "-c:v", "libx264", "-crf", "15", "-preset", "medium",
    "-c:a", "pcm_s16le", f"{P}/assets/edited.mov"], check=True)
print("duration", dur, "segments", len(keep))
