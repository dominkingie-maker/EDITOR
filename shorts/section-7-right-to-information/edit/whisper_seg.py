"""Transcribe a time range with sherpa-onnx Whisper. Usage: whisper_seg.py model_dir wav16k start end lang"""
import sys, wave
import numpy as np, sherpa_onnx
md, wav, a, b, lang = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
rec = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=f"{md}/small-encoder.int8.onnx", decoder=f"{md}/small-decoder.int8.onnx",
    tokens=f"{md}/small-tokens.txt", language=lang, task="transcribe", num_threads=4)
with wave.open(wav) as w:
    sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
s = rec.create_stream(); s.accept_waveform(sr, x[int(a * sr):int(b * sr)]); rec.decode_stream(s)
print(f"[{lang} {a}-{b}]", s.result.text)
