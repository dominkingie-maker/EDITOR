"""Word timestamps via sherpa-onnx zipformer (offline). Usage: asr.py model_dir wav16k out.json"""
import json, sys, wave
import numpy as np, sherpa_onnx
md, wav, out = sys.argv[1:4]
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f"{md}/encoder-epoch-99-avg-1.onnx", decoder=f"{md}/decoder-epoch-99-avg-1.onnx",
    joiner=f"{md}/joiner-epoch-99-avg-1.onnx", tokens=f"{md}/tokens.txt", num_threads=4,
    decoding_method="modified_beam_search")
with wave.open(wav) as w:
    sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
# chunk at ~20 s windows, cut at quiet points
win = sr * 20; pos = 0; words = []
while pos < len(a):
    end = min(len(a), pos + win)
    if end < len(a):
        seg = a[end - sr * 4:end]; e = np.convolve(seg ** 2, np.ones(1600) / 1600, 'same')
        end = end - sr * 4 + int(np.argmin(e))
    s = rec.create_stream(); s.accept_waveform(sr, a[pos:end]); rec.decode_stream(s)
    r = s.result; off = pos / sr
    cur = None
    for tok, t in zip(r.tokens, r.timestamps):
        if tok.startswith(("▁", " ")) or cur is None:
            if cur: words.append(cur)
            cur = {"text": tok.lstrip("▁ "), "start": off + t, "end": off + t + 0.08}
        else:
            cur["text"] += tok; cur["end"] = off + t + 0.08
    if cur: words.append(cur)
    pos = end
json.dump(words, open(out, "w"), indent=1)
print(" ".join(w["text"] for w in words))
