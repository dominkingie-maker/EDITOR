"""Map the known script onto ASR word timings. Usage: align.py script.txt asr.json duration out.json"""
import json, re, sys, difflib
script, asr, dur, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
sw = open(script).read().split()
aw = json.load(open(asr))
norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower()).replace("10", "ten").replace("7", "seven")
a_n = [norm(w["text"]) for w in aw]; s_n = [norm(w) for w in sw]
times = [None] * len(sw)
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, s_n, a_n, autojunk=False).get_opcodes():
    if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):
        for k in range(i2 - i1): times[i1 + k] = [aw[j1 + k]["start"], aw[j1 + k]["end"]]
    elif tag == "replace":  # spread the matched ASR span over the script words
        st, en = aw[j1]["start"], aw[j2 - 1]["end"]; n = i2 - i1
        for k in range(n): times[i1 + k] = [st + (en - st) * k / n, st + (en - st) * (k + 1) / n]
# fill gaps (deleted words) by interpolation between neighbours
for i, t in enumerate(times):
    if t is None:
        p = next((times[j][1] for j in range(i - 1, -1, -1) if times[j]), 0)
        q = next((times[j][0] for j in range(i + 1, len(times)) if times[j]), p + 0.3)
        times[i] = [p, min(q, p + 0.3)]
# ASR end stamps are token onsets; stretch each word to the next word's start when the gap is short
for i in range(len(times) - 1):
    gap = times[i + 1][0] - times[i][1]
    if 0 < gap < 0.35: times[i][1] = times[i + 1][0]
times[-1][1] = max(times[-1][1], times[-1][0] + 0.4)
# "Thank you!" is a quick 0.4 s burst at 46.44 s (RMS envelope); the ASR put its onset 0.15 s early.
times[-2], times[-1] = [46.44, 46.62], [46.62, 46.86]
words = [{"text": w, "start": round(t[0], 3), "end": round(t[1], 3)} for w, t in zip(sw, times)]
json.dump({"text": " ".join(sw), "audio_duration_secs": dur, "words": words}, open(out, "w"), indent=1)
for w in words: print(f'{w["start"]:6.2f} {w["end"]:6.2f} {w["text"]}')
