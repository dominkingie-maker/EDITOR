"""Section 4 short: builds sound effects, the audio mix and the HyperFrames composition from the
retimed transcript, so every visual and sound cue is anchored to a spoken word.

Usage: build.py <project_dir>
"""
import json, re, subprocess, sys, wave
import numpy as np

P = sys.argv[1]
SR, FPS = 48000, 30
T = json.load(open(f"{P}/assets/transcript.json"))
W = T["words"]
SPEECH_END = T["audio_duration_secs"]          # 48.433
END_CARD = 5.0
DUR = round(SPEECH_END + END_CARD, 3)


def at(i, lead=0.0):
    """Onset of word i (edited time), minus a small visual anticipation."""
    return round(max(0.0, W[i]["start"] - lead), 3)


# ---------- beat anchors (word indices from transcript.json) ----------
FOUR = at(7)
CHIPS = [("speech", "Speech", 18), ("expression", "Expression", 19), ("press", "Press", 21),
         ("assembly", "Assembly", 22), ("petition", "Petition", 24)]
CHIP_T = {k: at(i, 0.07) for k, _, i in CHIPS}
TO_TRACKER = round(W[24]["end"] + 0.35, 3)    # pause after "petition."
CHECKS = {"speech": at(31), "expression": at(32), "press": at(39),   # speak / express / the press
          "assembly": at(55), "petition": at(65)}                     # gather / government
ALL_DONE = at(72)                               # "community."
TRACKER_OUT = round(W[72]["end"] + 0.15, 3)
PUNCHES = [(at(42, 0.0), at(49, 0.0) - 0.05),   # "allows us to share our opinions freely"
           (at(76), at(82)),                     # "important because it allows us to"
           (at(108), SPEECH_END)]                # "Thank you!"
BRICK_IN = at(82, 0.1)
BRICKS = [("Speak up", at(82, 0.05)), ("Share thoughts", at(84, 0.05)), ("Better society", at(91, 0.05))]
BRICK_OUT = round(W[92]["end"] + 0.1, 3)
SCALE_IN = at(93, 0.1)
FREEDOM = at(96, 0.05)
RESPECT = at(103, 0.05)
BALANCED = at(107)
SCALE_OUT = SPEECH_END

# ---------- captions ----------
# Explicit phrase groups: (first word, last word, colour). gold = the right itself,
# blue = an action the right allows, green = the payoff. Serif marks the soft greetings.
GROUPS = [(0, 0, ""), (1, 1, ""), (2, 2, ""), (3, 5, ""), (6, 7, "gold"), (8, 9, ""), (10, 12, "gold"),
          (13, 15, ""), (16, 18, "gold"), (19, 19, "gold"), (20, 21, "gold"), (22, 22, "gold"), (23, 24, "gold"),
          (25, 26, "gold"), (27, 29, "gold"), (30, 31, "blue"), (32, 34, "blue"), (35, 37, "blue"), (38, 40, "gold"),
          (41, 43, ""), (44, 46, "blue"), (47, 48, "blue"), (49, 51, ""), (52, 54, "gold"), (55, 56, "blue"),
          (57, 59, ""), (60, 62, "blue"), (63, 65, "blue"), (66, 68, ""), (69, 71, "green"), (72, 72, "green"),
          (73, 74, "gold"), (75, 77, "green"), (78, 81, ""), (82, 83, "blue"), (84, 86, "blue"), (87, 89, "blue"),
          (90, 92, "green"), (93, 93, ""), (94, 96, "gold"), (97, 98, "gold"), (99, 101, ""), (102, 103, "green"),
          (104, 106, "gold"), (107, 107, "green"), (108, 109, "")]
SERIF = {0, 93, 108}   # "Hello,"  "Remember,"  "Thank you!"
assert [i for a_, b_, _ in GROUPS for i in range(a_, b_ + 1)] == list(range(len(W))), "groups must cover every word once"
HIDE = [(CHIP_T["speech"], TO_TRACKER + 0.4)]   # chips carry the words

CAPS = [{"idx": list(range(a_, b_ + 1)), "color": col, "start": round(max(0, W[a_]["start"] - 2 / FPS), 3)}
        for a_, b_, col in GROUPS]
for k, c in enumerate(CAPS):
    c["end"] = CAPS[k + 1]["start"] if k + 1 < len(CAPS) else SPEECH_END
    c["end"] = round(min(c["end"], W[c["idx"][-1]]["end"] + 0.6), 3)   # do not hold a chunk across a long gap
    c["serif"] = c["idx"][0] in SERIF
    c["text"] = " ".join(W[j]["text"] for j in c["idx"])
# trim chunks into hide windows
VIS = []
for c in CAPS:
    s, e = c["start"], c["end"]
    for hs, he in HIDE:
        if s >= hs and e <= he: s = e = None; break
        if s < hs < e: e = hs
        if s < he < e and s >= hs: s = he
    if s is not None and e - s > 0.05:
        VIS.append({**c, "start": s, "end": e})

# ---------- sound effects ----------
rng = np.random.default_rng(4)


def env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay)


def bandnoise(n, lo, hi):
    x = rng.standard_normal(n)
    f = np.fft.rfftfreq(n, 1 / SR); X = np.fft.rfft(x)
    X[(f < lo) | (f > hi)] = 0
    y = np.fft.irfft(X, n); return y / (np.abs(y).max() + 1e-9)


def tap(freq):          # soft dry tap for a chip landing
    n = int(SR * 0.12); t = np.arange(n) / SR
    return 0.6 * bandnoise(n, 1500, 6000) * env(n, 0.001, 0.012) + 0.5 * np.sin(2 * np.pi * freq * t) * env(n, 0.002, 0.03)


def tick(freq):         # warm short tone for a check
    n = int(SR * 0.6); t = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * freq * m * t) for m, a in ((1, 1), (2, 0.35), (3, 0.12)))
    return 0.55 * y * env(n, 0.004, 0.14)


def knock():            # damped wooden contact for bricks and scale pans
    n = int(SR * 0.25); t = np.arange(n) / SR
    return (0.8 * np.sin(2 * np.pi * 190 * t) * env(n, 0.001, 0.05)
            + 0.35 * bandnoise(n, 400, 2500) * env(n, 0.0005, 0.015))


def whoosh(d=0.45):     # soft air move
    n = int(SR * d); t = np.arange(n) / SR
    shape = np.sin(np.pi * t / d) ** 2
    return 0.5 * bandnoise(n, 500, 4000) * shape


def chime(f1, f2):      # gentle two-note completion
    n = int(SR * 1.6); t = np.arange(n) / SR; y = np.zeros(n)
    for f, off in ((f1, 0), (f2, 0.11)):
        k = int(off * SR); m = n - k; tt = t[:m]
        y[k:] += (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt)) * env(m, 0.005, 0.4)
    return 0.4 * y


CUES = [(FOUR, knock(), -14, "the '4' pulses on 'four'")]
for (k, _, _), f in zip(CHIPS, (1200, 1350, 1100, 1500, 1300)):
    CUES.append((CHIP_T[k] + 0.07, tap(f), -15, f"chip '{k}' lands"))
CUES.append((TO_TRACKER - 0.1, whoosh(), -20, "chips fly up into the tracker"))
for (k, t), f in zip(CHECKS.items(), (523.3, 587.3, 659.3, 698.5, 784.0)):
    CUES.append((t + 0.08, tick(f), -16, f"'{k}' checked"))
CUES.append((ALL_DONE + 0.1, chime(784.0, 1046.5), -19, "all five protected"))
CUES.append((TRACKER_OUT, whoosh(0.35), -24, "tracker exits"))
for name, t in BRICKS:
    CUES.append((t + 0.18, knock(), -15, f"brick '{name}' lands"))
CUES.append((FREEDOM + 0.22, knock(), -14, "'freedom' drops into the scale"))
CUES.append((RESPECT + 0.22, knock(), -14, "'respect' drops in, scale levels"))
CUES.append((BALANCED + 0.05, tick(880), -20, "balanced glow"))
CUES.append((SPEECH_END + 0.05, whoosh(0.5), -22, "end card"))
CUES.append((SPEECH_END + 0.4, chime(659.3, 987.8), -20, "end card settles"))

# ---------- audio mix ----------
A = f"{P}/assets/audio"
subprocess.run(["mkdir", "-p", A], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{P}/assets/edited.mov", "-vn", "-af",
                "highpass=f=80,acompressor=threshold=-24dB:ratio=2:attack=10:release=150:makeup=2,"
                f"apad=whole_dur={DUR}", "-ar", str(SR), "-ac", "1", f"{A}/voice.wav"], check=True)
with wave.open(f"{A}/voice.wav") as w:
    voice = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
N = int(DUR * SR); voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]
vpk = np.percentile(np.abs(voice[voice != 0]), 99.5)
sfx = np.zeros(N)
for t, y, db, _ in CUES:
    k = int(t * SR); y = y[: max(0, N - k)]
    sfx[k:k + len(y)] += y / (np.abs(y).max() + 1e-9) * vpk * 10 ** (db / 20) * 2.2
mix = voice + sfx
mix = mix / max(1.0, np.abs(mix).max() / 0.95)
stereo = (np.repeat(mix[:, None], 2, axis=1) * 32767).astype(np.int16)
with wave.open(f"{A}/premix.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(stereo.tobytes())
with wave.open(f"{A}/sfx.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(sfx, -1, 1) * 32767).astype(np.int16).tobytes())
# two-pass loudness: -16 LUFS integrated, -1.5 dBTP
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{A}/premix.wav", "-af",
                    "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True)
m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{A}/premix.wav", "-af",
                f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,"
                f"afade=t=out:st={DUR - 0.5}:d=0.5", "-ar", str(SR), f"{A}/mix.wav"], check=True)

# last frame for the end card
subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.1", "-i", f"{P}/assets/edited.mov",
                "-frames:v", "1", "-update", "1", f"{P}/assets/last-frame.jpg"], check=True)

# ---------- composition ----------
ICON = {
    "speech": '<path d="M10 14h44a6 6 0 0 1 6 6v22a6 6 0 0 1-6 6H30l-12 10v-10h-8a6 6 0 0 1-6-6V20a6 6 0 0 1 6-6z"/>',
    "expression": '<path d="M32 8a18 18 0 0 0-10 33v7h20v-7A18 18 0 0 0 32 8z"/><path d="M24 54h16M27 60h10"/>',
    "press": '<rect x="8" y="12" width="40" height="42" rx="4"/><path d="M48 22h8v26a6 6 0 0 1-12 0M16 22h24M16 32h24M16 42h14"/>',
    "assembly": '<circle cx="32" cy="20" r="7"/><circle cx="14" cy="26" r="6"/><circle cx="50" cy="26" r="6"/>'
                '<path d="M20 54v-8a12 12 0 0 1 24 0v8M4 54v-6a10 10 0 0 1 14-9M60 54v-6a10 10 0 0 0-14-9"/>',
    "petition": '<path d="M14 6h26l12 12v40H14z"/><path d="M40 6v12h12M22 30h20M22 40h20M22 50h12"/>',
}
svg = lambda k, cls="": f'<svg class="ico {cls}" viewBox="0 0 64 64">{ICON[k]}</svg>'


def caption_html():
    out = []
    for n, c in enumerate(VIS):
        cls = "cap " + c["color"] + (" serif" if c["serif"] else "")
        out.append(f'<div class="{cls}" id="cap{n}"><span>{c["text"]}</span></div>')
    return "\n".join(out)


chips = "\n".join(f'<div class="chip" id="chip-{k}"><div class="chip-ico">{svg(k)}</div><div class="chip-txt">{label}</div></div>'
                  for k, label, _ in CHIPS)
slots = "\n".join(f'<div class="slot" id="slot-{k}"><div class="slot-ico">{svg(k)}<div class="tick">'
                  f'<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7"/></svg></div></div><div class="slot-txt">{label}</div></div>'
                  for k, label, _ in CHIPS)

js = []
add = js.append
# hook card: visible from frame 0, the 4 pulses on its word
add(f"tl.fromTo('#hook-4',{{scale:1}},{{scale:1.28,duration:.12,ease:'power2.out'}},{FOUR});")
add(f"tl.to('#hook-4',{{scale:1,duration:.35,ease:'back.out(3)'}},{FOUR + 0.12});")
add(f"tl.fromTo('#hook-line',{{scaleX:0}},{{scaleX:1,duration:.5,ease:'power3.out'}},{at(10)});")
# chips land on their words
for k, _, _ in CHIPS:
    add(f"tl.fromTo('#chip-{k}',{{opacity:0,x:-60,scale:.92}},{{opacity:1,x:0,scale:1,duration:.32,ease:'back.out(1.8)'}},{CHIP_T[k]});")
# chips fly into the top tracker; hook card content swaps
add(f"tl.to('.chip',{{y:-1000,scale:.35,opacity:0,duration:.5,ease:'power3.in',stagger:.04}},{TO_TRACKER - 0.2});")
add(f"tl.to('#hook-inner',{{opacity:0,y:-20,duration:.25}},{TO_TRACKER - 0.1});")
add(f"tl.to('#topcard',{{height:196,duration:.35,ease:'power2.inOut'}},{TO_TRACKER - 0.1});")
add(f"tl.fromTo('#tracker',{{opacity:0}},{{opacity:1,duration:.2}},{TO_TRACKER + 0.15});")
add(f"tl.from('.slot',{{y:40,opacity:0,duration:.35,ease:'back.out(1.6)',stagger:.05}},{TO_TRACKER + 0.15});")
for k, t in CHECKS.items():
    add(f"tl.to('#slot-{k}',{{opacity:1,duration:.15}},{t});")
    add(f"tl.to('#slot-{k} .slot-ico',{{backgroundColor:'#FCD116',color:'#0b1626',duration:.18}},{t});")
    add(f"tl.fromTo('#slot-{k} .slot-ico',{{scale:1}},{{scale:1.18,duration:.12,yoyo:true,repeat:1,ease:'power2.out'}},{t});")
    add(f"tl.fromTo('#slot-{k} .tick',{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:'back.out(3)'}},{t + 0.06});")
    add(f"tl.to('#slot-{k} .slot-txt',{{color:'#FCD116',duration:.18}},{t});")
add(f"tl.fromTo('#tracker-title',{{opacity:.75}},{{opacity:1,duration:.1}},{ALL_DONE});")
add(f"tl.to('#tracker-count',{{color:'#FCD116',scale:1.15,duration:.15,yoyo:true,repeat:1}},{ALL_DONE});")
add(f"tl.to('#topcard',{{y:-260,opacity:0,duration:.4,ease:'power2.in'}},{TRACKER_OUT});")
add("const counter={n:0};const cnt=document.getElementById('tracker-count');")
for n, t in enumerate(CHECKS.values(), 1):
    add(f"tl.call(()=>{{cnt.textContent='{n}/5'}},null,{t});")
add(f"tl.call(()=>{{cnt.textContent='0/5'}},null,{TO_TRACKER});")
# bricks build a better society
add(f"tl.fromTo('#bricks',{{opacity:0,y:-30}},{{opacity:1,y:0,duration:.3,ease:'power2.out'}},{BRICK_IN});")
for n, (_, t) in enumerate(BRICKS):
    add(f"tl.fromTo('#brick{n}',{{y:-220,opacity:0}},{{y:0,opacity:1,duration:.28,ease:'bounce.out'}},{t});")
add(f"tl.to('#brick2',{{backgroundColor:'#FCD116',color:'#0b1626',duration:.2}},{at(92)});")
add(f"tl.to('#bricks',{{opacity:0,y:-40,duration:.25,ease:'power2.in'}},{BRICK_OUT});")
# balance scale: freedom tips it, respect levels it
add(f"tl.fromTo('#scale',{{opacity:0,y:-30}},{{opacity:1,y:0,duration:.3,ease:'power2.out'}},{SCALE_IN});")
add(f"tl.fromTo('#w-free',{{y:-160,opacity:0}},{{y:0,opacity:1,duration:.25,ease:'power2.in'}},{FREEDOM});")
add(f"tl.to('#beam',{{rotation:-6,duration:.6,ease:'elastic.out(1,.5)'}},{FREEDOM + 0.22});")
add(f"tl.to('#pan-l',{{y:30,duration:.6,ease:'elastic.out(1,.5)'}},{FREEDOM + 0.22});")
add(f"tl.to('#pan-r',{{y:-30,duration:.6,ease:'elastic.out(1,.5)'}},{FREEDOM + 0.22});")
add(f"tl.fromTo('#w-resp',{{y:-200,opacity:0}},{{y:0,opacity:1,duration:.25,ease:'power2.in'}},{RESPECT});")
add(f"tl.to('#beam',{{rotation:0,duration:.8,ease:'elastic.out(1,.45)'}},{RESPECT + 0.22});")
add(f"tl.to('#pan-l',{{y:0,duration:.8,ease:'elastic.out(1,.45)'}},{RESPECT + 0.22});")
add(f"tl.to('#pan-r',{{y:0,duration:.8,ease:'elastic.out(1,.45)'}},{RESPECT + 0.22});")
add(f"tl.fromTo('#balance-tag',{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.35,ease:'back.out(2)'}},{BALANCED});")
add(f"tl.to('#fulcrum',{{fill:'#FCD116',duration:.3}},{BALANCED});")
add(f"tl.to('#scale',{{opacity:0,duration:.3}},{SCALE_OUT - 0.3});")
add(f"tl.set('#scale',{{opacity:0}},{SCALE_OUT});")
# camera: slow drift plus hard punch-ins
add(f"tl.fromTo('#cam',{{scale:1}},{{scale:1.035,duration:{SPEECH_END},ease:'none'}},0);")
for a, b in PUNCHES:
    add(f"tl.set('#punch',{{scale:1.14}},{a});tl.set('#punch',{{scale:1}},{b});")
# captions: hard swaps
for n, c in enumerate(VIS):
    add(f"tl.set('#cap{n}',{{opacity:1}},{c['start']});tl.set('#cap{n}',{{opacity:0}},{c['end']});")
# end card
add(f"tl.fromTo('#end-dim',{{opacity:0}},{{opacity:1,duration:.5}},{SPEECH_END});")
add(f"tl.from('#end-card > *',{{opacity:0,y:30,duration:.5,ease:'power2.out',stagger:.18}},{SPEECH_END + 0.15});")
add(f"tl.to('#fade',{{opacity:1,duration:.5}},{DUR - 0.5});")

brick_html = "".join(f'<div class="brick" id="brick{n}">{name}</div>' for n, (name, _) in enumerate(BRICKS))

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1080, height=1920">
<title>Section 4 - Bill of Rights</title>
<script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:'Montserrat';src:url(assets/fonts/montserrat-latin.woff2) format('woff2');font-weight:100 900;font-display:block}}
@font-face{{font-family:'Abril Fatface';src:url(assets/fonts/abril-latin.woff2) format('woff2');font-display:block}}
:root{{--navy:#0b1626;--blue:#0038A8;--red:#CE1126;--gold:#FCD116;--sky:#8EC5FF;--mint:#7BE3A8}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000;font-family:'Montserrat',sans-serif;color:#fff}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}}
.layer{{position:absolute;inset:0;width:1080px;height:1920px}}
#cam,#punch{{position:absolute;inset:0;transform-origin:540px 640px}}
#face{{display:block;width:1080px;height:1920px;object-fit:cover}}
#freeze{{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}}
/* top card: hook title, then the five-freedoms tracker */
#topcard{{position:absolute;left:90px;top:92px;width:900px;height:236px;border-radius:28px;overflow:hidden;
  background:linear-gradient(160deg,rgba(13,30,58,.94),rgba(8,16,30,.94));border:2px solid rgba(255,255,255,.18);
  box-shadow:0 18px 40px rgba(0,0,0,.35)}}
#topcard::before{{content:'';position:absolute;left:0;top:0;bottom:0;width:12px;
  background:linear-gradient(var(--blue) 0 50%,var(--red) 50% 100%)}}
#hook-inner{{position:absolute;inset:0;padding:26px 44px 0 60px}}
.kicker{{font-weight:700;font-size:25px;letter-spacing:5px;color:var(--gold);text-transform:uppercase}}
.hook-title{{font-weight:900;font-size:112px;line-height:1;letter-spacing:-3px;margin-top:8px;white-space:nowrap}}
#hook-4{{display:inline-block;color:var(--gold);transform-origin:50% 60%}}
#hook-line{{height:4px;width:330px;background:var(--gold);margin-top:12px;transform-origin:0 50%;border-radius:2px}}
.hook-sub{{position:absolute;right:44px;bottom:28px;font-weight:600;font-size:22px;color:#c9d4e4;text-align:right;line-height:1.35}}
#tracker{{position:absolute;inset:0;padding:20px 30px 0 46px;opacity:0}}
.tr-head{{display:flex;justify-content:space-between;align-items:center;font-weight:800;font-size:22px;letter-spacing:4px;color:#c9d4e4}}
#tracker-count{{color:#fff;font-size:26px;letter-spacing:1px;display:inline-block}}
.slots{{display:flex;justify-content:space-between;margin-top:16px}}
.slot{{width:160px;display:flex;flex-direction:column;align-items:center;opacity:.55}}
.slot-ico{{position:relative;width:84px;height:84px;border-radius:50%;background:rgba(255,255,255,.1);color:#fff;
  display:flex;align-items:center;justify-content:center}}
.slot-ico .ico{{width:48px;height:48px}}
.slot-txt{{margin-top:8px;font-weight:800;font-size:19px;letter-spacing:1px;text-transform:uppercase}}
.tick{{position:absolute;right:-6px;top:-6px;width:36px;height:36px;border-radius:50%;background:#18a058;opacity:0;
  border:3px solid var(--navy);display:flex;align-items:center;justify-content:center}}
.tick svg{{width:22px;height:22px;fill:none;stroke:#fff;stroke-width:3.5;stroke-linecap:round;stroke-linejoin:round}}
.ico{{fill:none;stroke:currentColor;stroke-width:4.5;stroke-linecap:round;stroke-linejoin:round}}
/* five chips over the shirt */
#chips{{position:absolute;left:0;top:1150px;width:1080px}}
.chip{{width:600px;height:78px;margin:0 auto 12px;border-radius:40px;display:flex;align-items:center;gap:22px;padding:0 30px 0 9px;
  background:rgba(11,22,38,.9);border:2px solid rgba(255,255,255,.22);opacity:0}}
.chip-ico{{width:60px;height:60px;border-radius:50%;background:var(--gold);color:var(--navy);display:flex;align-items:center;justify-content:center}}
.chip-ico .ico{{width:36px;height:36px}}
.chip-txt{{font-weight:900;font-size:44px;letter-spacing:1px;text-transform:uppercase}}
/* bricks */
#bricks{{position:absolute;left:90px;top:92px;width:900px;height:236px;opacity:0;display:grid;
  grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:14px;padding:22px 40px}}
.brick{{display:flex;align-items:center;justify-content:center;border-radius:16px;font-weight:900;font-size:34px;white-space:nowrap;
  text-transform:uppercase;background:rgba(11,22,38,.92);border:2px solid rgba(255,255,255,.22);box-shadow:0 10px 24px rgba(0,0,0,.3)}}
#brick2{{grid-column:1 / span 2;grid-row:1}}#brick0{{grid-row:2;grid-column:1}}#brick1{{grid-row:2;grid-column:2}}
/* balance scale */
#scale{{position:absolute;left:90px;top:92px;width:900px;height:236px;opacity:0;border-radius:28px;
  background:linear-gradient(160deg,rgba(13,30,58,.94),rgba(8,16,30,.94));border:2px solid rgba(255,255,255,.18);box-shadow:0 18px 40px rgba(0,0,0,.35)}}
#scale svg{{position:absolute;inset:0;overflow:visible}}
.weight{{position:absolute;width:250px;height:52px;border-radius:12px;display:flex;align-items:center;justify-content:center;
  font-weight:900;font-size:30px;letter-spacing:1px;color:var(--navy)}}
#w-free{{background:var(--gold)}}#w-resp{{background:var(--mint)}}
#pan-l,#pan-r{{position:absolute;top:96px;width:250px;height:100px}}
#pan-l{{left:45px}}#pan-r{{right:45px}}
.string{{position:absolute;left:123px;top:-26px;width:4px;height:60px;background:#e8edf5;border-radius:2px}}
.pan-plate{{position:absolute;bottom:0;left:0;width:250px;height:14px;border-radius:0 0 30px 30px;background:#e8edf5}}
#w-free,#w-resp{{left:0;bottom:14px}}
#balance-tag{{position:absolute;left:360px;top:8px;width:180px;text-align:center;font-weight:900;font-size:22px;letter-spacing:4px;
  color:var(--navy);background:var(--gold);border-radius:20px;padding:5px 0;opacity:0}}
/* captions */
.cap{{position:absolute;left:0;top:1205px;width:1080px;display:flex;justify-content:center;opacity:0}}
.cap span{{display:inline-block;max-width:900px;text-align:center;font-weight:800;font-size:64px;line-height:1.1;text-transform:uppercase;
  padding:12px 30px 14px;border-radius:18px;background:rgba(10,18,32,.86);border:2px solid rgba(255,255,255,.26)}}
.cap.gold span{{color:var(--gold)}}.cap.blue span{{color:var(--sky)}}.cap.green span{{color:var(--mint)}}
.cap.serif span{{font-family:'Abril Fatface',serif;font-weight:400;text-transform:none;font-size:70px}}
/* end card */
#end-dim{{position:absolute;inset:0;background:rgba(8,14,26,.84)}}
#end-card{{position:absolute;left:90px;top:520px;width:900px;text-align:left}}
.end-kicker{{font-weight:800;font-size:28px;letter-spacing:5px;color:var(--gold)}}
.end-title{{font-weight:900;font-size:76px;line-height:1;margin:14px 0 34px;letter-spacing:-2px}}
.end-quote{{font-family:'Abril Fatface',serif;font-size:50px;line-height:1.28;color:#fff;border-left:8px solid var(--gold);padding-left:34px}}
.end-src{{margin-top:34px;font-weight:600;font-size:26px;color:#b8c4d6;letter-spacing:1px}}
#fade{{position:absolute;inset:0;background:#000;opacity:0}}
</style></head><body>
<div id="root" data-composition-id="main" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="cam"><div id="punch">
    <video id="face" src="assets/edited.mov" muted playsinline data-start="0" data-duration="{SPEECH_END}" data-track-index="0"></video>
  </div></div>
  <img id="freeze" class="clip" src="assets/last-frame.jpg" alt="" data-start="{SPEECH_END}" data-duration="{END_CARD}" data-track-index="1">
  <audio id="mix" src="assets/audio/mix.wav" data-start="0" data-duration="{DUR}" data-track-index="2" data-volume="1"></audio>
  <div id="gfx" class="layer clip" data-start="0" data-duration="{SPEECH_END}" data-track-index="3">
    <div id="topcard">
      <div id="hook-inner">
        <div class="kicker">Bill of Rights &middot; Article III</div>
        <div class="hook-title">SECTION <span id="hook-4">4</span></div>
        <div id="hook-line"></div>
        <div class="hook-sub">1987 Philippine<br>Constitution</div>
      </div>
      <div id="tracker">
        <div class="tr-head"><span id="tracker-title">SECTION 4 PROTECTS</span><span id="tracker-count">0/5</span></div>
        <div class="slots">{slots}</div>
      </div>
    </div>
    <div id="chips">{chips}</div>
    <div id="bricks">{brick_html}</div>
    <div id="scale">
      <svg viewBox="0 0 900 236">
        <polygon id="fulcrum" points="450,70 424,214 476,214" fill="#e8edf5"/>
        <rect x="390" y="210" width="120" height="12" rx="6" fill="#e8edf5"/>
        <g id="beam" style="transform-origin:450px 70px"><rect x="160" y="62" width="580" height="16" rx="8" fill="#e8edf5"/>
          <circle cx="450" cy="70" r="16" fill="#0b1626" stroke="#e8edf5" stroke-width="5"/></g>
      </svg>
      <div id="pan-l"><div class="string"></div><div class="weight" id="w-free">FREEDOM</div><div class="pan-plate"></div></div>
      <div id="pan-r"><div class="string"></div><div class="weight" id="w-resp">RESPECT</div><div class="pan-plate"></div></div>
      <div id="balance-tag">BALANCE</div>
    </div>
  </div>
  <div id="caps" class="layer clip" data-start="0" data-duration="{SPEECH_END}" data-track-index="4">
{caption_html()}
  </div>
  <div id="end" class="layer clip" data-start="{SPEECH_END}" data-duration="{END_CARD}" data-track-index="5">
    <div id="end-dim"></div>
    <div id="end-card">
      <div class="end-kicker">ARTICLE III &middot; BILL OF RIGHTS</div>
      <div class="end-title">Section 4</div>
      <div class="end-quote">&ldquo;No law shall be passed abridging the freedom of speech, of expression, or of the press, or the right of the people peaceably to assemble and petition the government for redress of grievances.&rdquo;</div>
      <div class="end-src">1987 Constitution of the Republic of the Philippines</div>
    </div>
    <div id="fade"></div>
  </div>
</div>
<script>
const tl=gsap.timeline({{paused:true}});
{chr(10).join(js)}
tl.set({{}},{{}},{DUR});
window.__timelines=window.__timelines||{{}};window.__timelines['main']=tl;
</script>
</body></html>
"""
open(f"{P}/index.html", "w").write(html)
json.dump({"id": "main", "name": "section-4-bill-of-rights-2026-10-20", "width": 1080, "height": 1920, "fps": FPS},
          open(f"{P}/meta.json", "w"), indent=2)
json.dump({"duration": DUR, "captions": [{k: c[k] for k in ("text", "start", "end", "color")} for c in VIS],
           "sound_cues": [{"time": round(t, 3), "level_db": db, "purpose": why} for t, _, db, why in CUES],
           "beats": {"four": FOUR, "chips": CHIP_T, "to_tracker": TO_TRACKER, "checks": CHECKS, "tracker_out": TRACKER_OUT,
                     "punch_ins": PUNCHES, "bricks": BRICKS, "scale": [SCALE_IN, FREEDOM, RESPECT, BALANCED],
                     "end_card": SPEECH_END}},
          open(f"{P}/assets/cue-sheet.json", "w"), indent=1)
print(f"duration {DUR}s, {len(VIS)} captions, {len(CUES)} sound cues, loudness in {m['input_i']} LUFS")
