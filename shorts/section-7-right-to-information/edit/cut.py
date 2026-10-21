"""Frame-aligned cut: keep [start,end] minus removed pause middles. Writes EDL, retimed transcript, runs ffmpeg once.
Usage: cut.py project_dir"""
import json, subprocess, sys
P = sys.argv[1]; FPS = 30
fr = lambda t: round(t * FPS) / FPS
START, END = 0.0, 47.00
# (source silence, reason) -> middle removed, natural beat kept on both sides
REMOVE = [
    (6.26, 6.59, "sentence break after 'Information.' 0.63s -> 0.30s"),
    (15.72, 16.08, "pause after 'For example,' 0.57s -> 0.21s"),
    (20.14, 20.38, "sentence break after 'road.' 0.54s -> 0.30s"),
    (27.55, 27.76, "sentence break after 'completed.' 0.51s -> 0.30s"),
    (35.50, 35.67, "pause after 'important?' 0.47s -> 0.30s"),
    (46.08, 46.26, "pause before 'Thank you!' 0.46s -> 0.28s"),
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
                   [{"source_start": fr(END), "source_end": 49.5, "reason": "handling noise after 'Thank you!'"}]},
          open(f"{P}/assets/edit-decisions.json", "w"), indent=1)
vexpr = "+".join(f"between(n,{round(a * FPS)},{round(b * FPS) - 1})" for a, b in keep)
achain = "".join(f"[0:a]atrim={a:.5f}:{b:.5f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={b - a - 0.005:.5f}:d=0.005[a{i}];"
                 for i, (a, b) in enumerate(keep)) + "".join(f"[a{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=0:a=1[a]"
grade = "hqdn3d=2:1.5:4:3,eq=contrast=1.10:brightness=0.01:saturation=0.98:gamma=1.02,scale=1080:1920:flags=lanczos,unsharp=5:5:0.6"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{P}/assets/raw.mp4", "-filter_complex",
    f"[0:v]select='{vexpr}',setpts=N/{FPS}/TB,{grade},format=yuv420p[v];" + achain,
    "-map", "[v]", "-map", "[a]", "-r", str(FPS), "-c:v", "libx264", "-crf", "15", "-preset", "medium",
    "-c:a", "pcm_s16le", f"{P}/assets/edited.mov"], check=True)
print("duration", dur, "segments", len(keep))
