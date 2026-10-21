"""Section 7 - Right to Information: sound effects, music/voice mix and the HyperFrames composition,
all anchored to words in the retimed transcript. Follows the user's asset board: black / white / red,
bold condensed type, torn paper, brush strokes, film grain.

Usage: build.py <project_dir>
"""
import json, random, subprocess, sys, wave
import numpy as np

P = sys.argv[1]
SR, FPS = 48000, 30
T = json.load(open(f"{P}/assets/transcript.json"))
W = T["words"]
SPEECH_END = T["audio_duration_secs"]          # 45.5
END_CARD = 3.0
DUR = round(SPEECH_END + END_CARD, 3)


def at(i, lead=0.0):
    return round(max(0.0, W[i]["start"] - lead), 3)


# ---------- beats (word indices from transcript.json) ----------
LOWER3_IN, LOWER3_OUT = at(2, 0.1), at(18)               # "Rogie" .. "Information."
SPLIT_IN = at(19, 0.25)                                  # "So basically"
DOC_IN = at(25, 0.1)                                     # "Filipino citizen"
RIGHT_TO_KNOW = at(29, 0.05)                             # "right to know"
WHAT_GOV = at(34, 0.05)                                  # "government is doing"
MAGNIFY = at(36)                                         # "doing"
ESPECIALLY = at(37, 0.05)
PUBLIC_MONEY = at(41, 0.05)                              # "public money"
TEAR3 = at(43, 0.3)                                      # "For example"
ALLOCATES = at(50, 0.05)                                 # "nag-allocate"
COUNT_A, COUNT_B = at(52, 0.05), round(W[54]["end"], 3)   # "10 million pesos"
ROAD = at(57, 0.05)                                      # "construction"
TEAR4 = at(60, 0.3)                                      # "Of course"
ASK = at(62, 0.05)                                       # "we have the right to ask"
CARDS = [at(68, 0.08), at(73, 0.08), at(78, 0.08)]       # "kung asa" / "giunsa" / "whether"
COMPLETED = at(84)
TEAR5 = at(85, 0.3)                                      # "But remember"
LIMITS = at(90, 0.05)                                    # "limitations"
SOME_INFO = at(92, 0.05)
STAMP = at(96, 0.05)                                     # "confidential"
LOCK = at(98, 0.05)                                      # "protected"
TEAR6 = at(101, 0.3)                                     # "So, why"
WHY = at(102, 0.05)
ICONS = [at(109, 0.08), at(110, 0.08), at(112, 0.08)]    # transparency / accountability / helps prevent
SPLIT_OUT = at(115, 0.25)                                # "At the end of the day"
SERVES = at(121, 0.05)                                   # "the government serves the people"
KNOW = at(126, 0.05)                                     # "and we have the right to know"
OPERATES = at(133, 0.05)                                 # "how it operates"
END_WIPE = round(SPEECH_END - 0.25, 3)

# ---------- captions ----------
# (first word, last word, style): "" = black box, "red" = red callout box
GROUPS = [(0, 0, ""), (1, 3, ""), (4, 5, ""), (6, 8, ""), (9, 11, "red"), (12, 13, "red"), (14, 17, ""),
          (18, 18, "red"), (19, 20, ""), (21, 23, ""), (24, 26, ""), (27, 29, ""), (30, 31, "red"), (32, 34, ""),
          (35, 36, ""), (37, 37, ""), (38, 40, ""), (41, 42, "red"), (43, 44, ""), (45, 47, ""), (48, 49, ""),
          (50, 51, ""), (52, 54, "red"), (55, 56, ""), (57, 59, ""), (60, 61, ""), (62, 64, ""), (65, 67, "red"),
          (68, 70, ""), (71, 72, ""), (73, 76, ""), (77, 78, ""), (79, 80, ""), (81, 82, ""), (83, 84, "red"),
          (85, 86, ""), (87, 89, ""), (90, 90, "red"), (91, 92, ""), (93, 94, ""), (95, 96, "red"), (97, 98, ""),
          (99, 100, "red"), (101, 102, ""), (103, 105, ""), (106, 106, ""), (107, 108, ""), (109, 109, "red"),
          (110, 110, "red"), (111, 113, ""), (114, 114, "red"), (115, 120, ""), (121, 123, ""), (124, 125, ""),
          (126, 128, ""), (129, 132, "red"), (133, 135, ""), (136, 137, "")]
assert [i for a, b, _ in GROUPS for i in range(a, b + 1)] == list(range(len(W))), "groups must cover every word once"
CAPS = [{"idx": list(range(a, b + 1)), "style": st, "start": round(max(0, W[a]["start"] - 2 / FPS), 3)}
        for a, b, st in GROUPS]
for k, c in enumerate(CAPS):
    c["end"] = CAPS[k + 1]["start"] if k + 1 < len(CAPS) else SPEECH_END
    c["end"] = round(min(c["end"], W[c["idx"][-1]]["end"] + 0.6), 3)
    c["text"] = " ".join(W[j]["text"] for j in c["idx"])

# ---------- sound effects ----------
rng = np.random.default_rng(11)


def env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay)


def bandnoise(n, lo, hi):
    x = rng.standard_normal(n); f = np.fft.rfftfreq(n, 1 / SR); X = np.fft.rfft(x)
    X[(f < lo) | (f > hi)] = 0
    y = np.fft.irfft(X, n); return y / (np.abs(y).max() + 1e-9)


def impact(f=70, d=0.5):         # low cinematic hit for slams (no pitch-drop plop: steady tone, fast decay)
    n = int(SR * d); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * env(n, 0.002, 0.12) + 0.5 * bandnoise(n, 60, 900) * env(n, 0.001, 0.04)
            + 0.25 * bandnoise(n, 2000, 8000) * env(n, 0.0005, 0.01))


def stamp():                     # rubber stamp: dry thump + paper slap
    n = int(SR * 0.3); t = np.arange(n) / SR
    return 0.9 * np.sin(2 * np.pi * 110 * t) * env(n, 0.001, 0.05) + 0.6 * bandnoise(n, 300, 3000) * env(n, 0.0005, 0.02)


def rip(d=0.42):                 # paper tear: crackly band noise with grainy amplitude
    n = int(SR * d); t = np.arange(n) / SR
    grit = np.repeat(rng.uniform(0.2, 1, n // 240 + 1), 240)[:n]
    return bandnoise(n, 1200, 7000) * grit * np.sin(np.pi * t / d) ** 0.6


def whoosh(d=0.45, lo=400, hi=3500):
    n = int(SR * d); t = np.arange(n) / SR
    return bandnoise(n, lo, hi) * np.sin(np.pi * t / d) ** 2


def tap(freq=1400):
    n = int(SR * 0.1); t = np.arange(n) / SR
    return 0.6 * bandnoise(n, 1500, 6000) * env(n, 0.001, 0.01) + 0.5 * np.sin(2 * np.pi * freq * t) * env(n, 0.002, 0.025)


def click():                     # padlock shackle: two quick metal clicks
    n = int(SR * 0.16); y = np.zeros(n)
    for off in (0, 0.07):
        k = int(off * SR); m = n - k; tt = np.arange(m) / SR
        y[k:] += (bandnoise(m, 2500, 9000) * env(m, 0.0003, 0.006) + 0.4 * np.sin(2 * np.pi * 3200 * tt) * env(m, 0.0005, 0.012))
    return y


def tone(freq):
    n = int(SR * 0.6); t = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * freq * m * t) for m, a in ((1, 1), (2, 0.3), (3, 0.1))) * env(n, 0.004, 0.15)


CUES = [(0.0, whoosh(0.3, 600, 5000), -26, "title ink swipe"), (0.22, impact(), -20, "title lands"),
        (LOWER3_IN, whoosh(0.3), -26, "lower third slides in"),
        (SPLIT_IN, whoosh(0.5, 300, 3000), -20, "split screen opens"),
        (DOC_IN + 0.05, whoosh(0.35, 1500, 6000), -26, "document slides in"),
        (RIGHT_TO_KNOW + 0.05, stamp(), -18, "RIGHT TO KNOW stamps"),
        (MAGNIFY + 0.35, whoosh(0.4, 800, 4000), -33, "magnifier sweep"),
        (PUBLIC_MONEY + 0.05, impact(80, 0.4), -18, "PUBLIC MONEY slams"),
        (TEAR3, rip(), -20, "paper tear to the example"),
        (ALLOCATES + 0.05, tap(), -22, "label lands")]
steps = int((COUNT_B - COUNT_A) / 0.045)
for k in range(steps):
    CUES.append((COUNT_A + k * 0.045, tap(1800 + 30 * k), -30 + 6 * k / steps, "counter tick"))
CUES += [(COUNT_B, impact(90, 0.35), -18, "counter locks on P10,000,000"),
         (ROAD + 0.05, whoosh(0.3, 700, 4000), -24, "road construction bar"),
         (TEAR4, rip(), -20, "paper tear to the questions")]
for t, f in zip(CARDS, (1200, 1350, 1500)):
    CUES.append((t + 0.08, tap(f), -18, "question card pops"))
CUES += [(COMPLETED, tone(660), -24, "COMPLETED? highlights"),
         (TEAR5, rip(), -20, "paper tear to limitations"),
         (LIMITS + 0.05, impact(), -18, "LIMITATIONS slams"),
         (STAMP + 0.05, stamp(), -15, "CONFIDENTIAL stamp"),
         (LOCK + 0.15, click(), -16, "lock snaps shut"),
         (TEAR6, rip(), -20, "paper tear to why it matters"),
         (WHY + 0.05, impact(75, 0.35), -22, "WHY IT'S IMPORTANT lands")]
for t, f in zip(ICONS, (523.3, 659.3, 784.0)):
    CUES.append((t + 0.08, tone(f), -25, "icon pops"))
CUES += [(SPLIT_OUT, whoosh(0.5, 300, 3000), -21, "split screen closes"),
         (SERVES, tap(1100), -27, "closing line 1"), (KNOW, tap(1300), -27, "closing line 2"),
         (OPERATES, tap(1500), -27, "closing line 3"),
         (round(W[-1]["end"], 3), rip(0.45), -21, "tear to the thank-you card (after the last word)"),
         (SPEECH_END + 0.15, whoosh(0.45, 900, 6000), -22, "brush stroke")]

# ---------- mix: voice + ducked music + sfx, -16 LUFS ----------
A = f"{P}/assets/audio"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{P}/assets/edited.mov", "-vn", "-af",
                f"highpass=f=80,acompressor=threshold=-22dB:ratio=2:attack=10:release=150:makeup=1,apad=whole_dur={DUR}",
                "-ar", str(SR), "-ac", "1", f"{A}/voice.wav"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{A}/music.wav", "-ar", str(SR), "-ac", "1", f"{A}/music48.wav"], check=True)


def readwav(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768


N = int(DUR * SR)
voice = np.pad(readwav(f"{A}/voice.wav"), (0, N))[:N]
music = np.pad(readwav(f"{A}/music48.wav"), (0, N))[:N]
rms = lambda x: np.sqrt(np.mean(x ** 2) + 1e-12)
speech = voice[np.abs(voice) > 0.01]
v_rms = rms(speech)
# voice envelope -> duck the bed 6 dB under speech (40 ms attack, 300 ms release)
blk = SR // 100
e = np.array([rms(voice[i:i + blk]) for i in range(0, N, blk)])
act = (e > v_rms * 0.25).astype(float)
sm = np.zeros_like(act)
for i in range(1, len(act)):
    k = 0.6 if act[i] > sm[i - 1] else 0.033
    sm[i] = sm[i - 1] + k * (act[i] - sm[i - 1])
duck = np.repeat(10 ** (-6 * sm / 20), blk)[:N]
BED_DB = -12
music = music / rms(music) * v_rms * 10 ** (BED_DB / 20) * duck
fade_in = np.minimum(1, np.arange(N) / (0.4 * SR))
music *= fade_in
vpk = np.percentile(np.abs(speech), 99.5)
sfx = np.zeros(N)
for t, y, db, _ in CUES:
    k = int(t * SR); y = y[: max(0, N - k)]
    sfx[k:k + len(y)] += y / (np.abs(y).max() + 1e-9) * vpk * 10 ** (db / 20) * 2.0
mix = voice + music + sfx
mix = mix / max(1.0, np.abs(mix).max() / 0.95)


def writewav(p, x, ch=1):
    with wave.open(p, "wb") as w:
        w.setnchannels(ch); w.setsampwidth(2); w.setframerate(SR)
        data = np.repeat(x[:, None], ch, axis=1) if ch == 2 else x
        w.writeframes((np.clip(data, -1, 1) * 32767).astype(np.int16).tobytes())


writewav(f"{A}/premix.wav", mix, 2)
writewav(f"{A}/sfx.wav", sfx)
writewav(f"{A}/bed.wav", music)
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{A}/premix.wav", "-af",
                    "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{A}/premix.wav", "-af",
                f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,"
                f"afade=t=out:st={DUR - 0.6}:d=0.6", "-ar", str(SR), f"{A}/mix.wav"], check=True)

# ---------- drawn assets ----------
rnd = random.Random(3)


def jagged(y0, amp, step=18):
    """Points (x%, y px) of a torn horizontal edge across 0..1080."""
    pts, x = [], 0
    while x <= 1080:
        pts.append((x, y0 + rnd.uniform(-amp, amp))); x += rnd.randint(step // 2, step)
    pts.append((1080, y0))
    return pts


edge = jagged(905, 14)
PANEL_CLIP = "polygon(0 0,1080px 0," + ",".join(f"{x:.0f}px {y:.0f}px" for x, y in reversed(edge)) + ")"
brush = jagged(915, 7, 26)
BRUSH_PATH = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in brush)


def tear_clip(w, h):
    """Paper sheet with torn left and right edges."""
    left = [(rnd.uniform(0, 30), y) for y in range(0, h + 1, 24)]
    right = [(w - rnd.uniform(0, 30), y) for y in range(h, -1, -24)]
    return "polygon(" + ",".join(f"{x:.0f}px {y:.0f}px" for x, y in left + right) + ")"


TEAR_CLIP = tear_clip(1300, 960)
TEAR_FULL_CLIP = tear_clip(1300, 1920)

ICON = {  # 64x64 line icons
    "bag": '<path d="M24 10h16l-4 8H28z"/><path d="M28 18C14 26 10 40 12 48a8 8 0 0 0 8 8h24a8 8 0 0 0 8-8c2-8-2-22-16-30"/>'
           '<path d="M36 30c-2-2-8-2-8 2s8 2 8 6-6 4-8 2M32 26v4M32 42v4"/>',
    "doc": '<path d="M16 6h22l12 12v40H16z"/><path d="M38 6v12h12M23 30h20M23 39h20M23 48h13"/>',
    "road": '<path d="M24 6L10 58M40 6l14 52"/><path d="M32 10v6M32 24v8M32 40v10"/>',
    "lens": '<circle cx="27" cy="27" r="15"/><path d="M38 38l16 16"/>',
    "people": '<circle cx="32" cy="20" r="7"/><circle cx="14" cy="26" r="6"/><circle cx="50" cy="26" r="6"/>'
              '<path d="M20 54v-8a12 12 0 0 1 24 0v8M4 54v-6a10 10 0 0 1 14-9M60 54v-6a10 10 0 0 0-14-9"/>',
    "shield": '<path d="M32 6l20 8v16c0 14-9 22-20 28C21 52 12 44 12 30V14z"/><path d="M23 32l7 7 12-14"/>',
}
svg = lambda k: f'<svg class="ico" viewBox="0 0 64 64">{ICON[k]}</svg>'

BUILDING = """<svg viewBox="0 0 520 470" class="building">
 <g fill="none" stroke="#e9e9e9" stroke-width="5" stroke-linejoin="round">
  <path d="M20 150 L260 40 L500 150 Z"/><path d="M70 140 L260 62 L450 140"/>
  <rect x="30" y="150" width="460" height="34"/><rect x="40" y="184" width="440" height="14"/>
  """ + "".join(f'<rect x="{62 + i * 72}" y="198" width="34" height="200"/><path d="M{66 + i * 72} 215v168M{79 + i * 72} 215v168M{92 + i * 72} 215v168" stroke-width="2"/>'
                for i in range(6)) + """
  <rect x="30" y="398" width="460" height="18"/><rect x="14" y="416" width="492" height="20"/><rect x="0" y="436" width="520" height="24"/>
 </g>
 <circle cx="260" cy="118" r="17" fill="none" stroke="#e9e9e9" stroke-width="4"/>
 <path d="M260 40 V-40" stroke="#e9e9e9" stroke-width="4"/>
 <g class="flag"><rect x="262" y="-40" width="90" height="26" fill="#0038A8"/><rect x="262" y="-14" width="90" height="26" fill="#CE1126"/>
  <path d="M262 -40 L300 -14 L262 12 Z" fill="#fff"/><circle cx="276" cy="-14" r="5" fill="#FCD116"/></g>
</svg>"""

EXCAVATOR = """<svg viewBox="0 0 300 200" class="excavator"><g fill="#cfcfcf" stroke="#1a1a1a" stroke-width="3">
 <rect x="20" y="150" width="170" height="34" rx="17"/><circle cx="40" cy="167" r="10"/><circle cx="170" cy="167" r="10"/>
 <rect x="40" y="96" width="120" height="54" rx="6"/><rect x="104" y="60" width="56" height="50" rx="6" fill="#9a9a9a"/>
 <g class="arm" style="transform-origin:155px 106px"><path d="M150 100 L230 40 L245 52 L170 112 Z"/><path d="M230 40 L280 110 L266 118 L222 56 Z"/>
 <path d="M266 110 l26 6 -4 30 -30 -10 z" fill="#e10600"/></g></g></svg>"""

FOLDERS = """<svg viewBox="0 0 440 380" class="folders"><g stroke="#1a1a1a" stroke-width="3">
 <path d="M30 70 h120 l20 22 h230 v250 H30z" fill="#8c8c8c"/>
 <path d="M14 96 h120 l20 22 h230 v250 H14z" fill="#b5b5b5"/>
 <path d="M0 124 h120 l20 22 h236 v234 H0z" fill="#dadada"/></g>
 <g stroke="#9a9a9a" stroke-width="5"><path d="M40 330h200M40 352h150"/></g></svg>"""

LOCK_SVG = """<svg viewBox="0 0 160 200" class="lock"><path id="shackle" d="M40 96 V58 a40 40 0 0 1 80 0 V96" fill="none" stroke="#e9e9e9" stroke-width="16"/>
 <rect x="16" y="92" width="128" height="104" rx="14" fill="#111" stroke="#e9e9e9" stroke-width="6"/>
 <circle cx="80" cy="134" r="12" fill="#e9e9e9"/><rect x="74" y="140" width="12" height="28" fill="#e9e9e9"/></svg>"""

SCALES = """<svg viewBox="0 0 240 200" class="scales"><g fill="none" stroke="#e9e9e9" stroke-width="6" stroke-linecap="round">
 <path d="M120 20v160M70 186h100M30 50h180"/><path d="M30 50 L8 110 M30 50 L52 110 M210 50 L188 110 M210 50 L232 110"/>
 <path d="M4 110 a26 16 0 0 0 52 0z M184 110 a26 16 0 0 0 52 0z" fill="#e9e9e9"/></g><circle cx="120" cy="20" r="9" fill="#e10600"/></svg>"""


def sun(size, color="#fff"):
    rays = []
    for k in range(8):
        for d, L, wdt in ((-14, 0.78, 0.05), (0, 1.0, 0.09), (14, 0.78, 0.05)):
            a = np.radians(k * 45 + d)
            tip = (50 + 48 * L * np.cos(a), 50 + 48 * L * np.sin(a))
            b1 = (50 + 20 * np.cos(a + wdt * 3), 50 + 20 * np.sin(a + wdt * 3))
            b2 = (50 + 20 * np.cos(a - wdt * 3), 50 + 20 * np.sin(a - wdt * 3))
            rays.append(f"M{b1[0]:.1f},{b1[1]:.1f} L{tip[0]:.1f},{tip[1]:.1f} L{b2[0]:.1f},{b2[1]:.1f}Z")
    return (f'<svg viewBox="0 0 100 100" width="{size}" height="{size}"><path d="{" ".join(rays)}" fill="{color}"/>'
            f'<circle cx="50" cy="50" r="18" fill="{color}"/></svg>')


# ---------- timeline ----------
js = []
add = js.append
add("const tl=gsap.timeline({paused:true});")
# film grain (cycles every 2 frames)
for k in range(int(DUR * FPS / 2)):
    add(f"tl.set('#grain',{{backgroundImage:'url(assets/grain/g{k % 6 + 1}.png)',backgroundPosition:'{(k * 37) % 300}px {(k * 53) % 300}px'}},{k * 2 / FPS:.3f});")
# intro title + lower third
add("tl.fromTo('#t-sec',{x:-80,opacity:0},{x:0,opacity:1,duration:.32,ease:'power3.out'},0);")
add("tl.fromTo('#t-rti',{x:80,opacity:0},{x:0,opacity:1,duration:.32,ease:'power3.out'},.12);")
add("tl.fromTo('#t-brush',{scaleX:0},{scaleX:1,duration:.4,ease:'power2.out'},.3);")
add("tl.fromTo('#title',{skewX:-8},{skewX:0,duration:.25,ease:'power2.out'},.22);")
add(f"tl.fromTo('#l3',{{x:-700}},{{x:0,duration:.45,ease:'power3.out'}},{LOWER3_IN});")
add(f"tl.fromTo('#l3-tag',{{scaleX:0}},{{scaleX:1,duration:.3,ease:'power2.out'}},{LOWER3_IN + 0.25});")
add(f"tl.to('#l3',{{x:-760,duration:.35,ease:'power2.in'}},{LOWER3_OUT});")
add(f"tl.to('#title',{{y:-360,duration:.4,ease:'power2.in'}},{SPLIT_IN});")
# split screen in/out
add(f"tl.fromTo('#panel',{{y:-960}},{{y:0,duration:.45,ease:'power3.out'}},{SPLIT_IN});")
add(f"tl.fromTo('#shift',{{y:0}},{{y:620,duration:.45,ease:'power3.out'}},{SPLIT_IN});")
add(f"tl.set('#capwrap',{{y:-468}},{SPLIT_IN + 0.3});")
add(f"tl.to('#panel',{{y:-960,duration:.45,ease:'power3.in'}},{SPLIT_OUT});")
add(f"tl.to('#shift',{{y:0,duration:.45,ease:'power3.inOut'}},{SPLIT_OUT});")
add(f"tl.set('#capwrap',{{y:0}},{SPLIT_OUT + 0.25});")
add(f"tl.set('#panel',{{y:-960}},{SPLIT_OUT + 0.45});")
# section swaps behind paper tears
SECS = [("s2", SPLIT_IN), ("s3", TEAR3 + 0.22), ("s4", TEAR4 + 0.22), ("s5", TEAR5 + 0.22), ("s6", TEAR6 + 0.22), (None, SPLIT_OUT + 0.45)]
for (sid, t0), (_, t1) in zip(SECS, SECS[1:]):
    add(f"tl.set('#{sid}',{{opacity:1}},{t0});tl.set('#{sid}',{{opacity:0}},{t1});")
for t in (TEAR3, TEAR4, TEAR5, TEAR6):
    add(f"tl.fromTo('#tear',{{x:-1340}},{{x:1120,duration:.5,ease:'power2.inOut'}},{t});")
    add(f"tl.set('#tear',{{x:-1340}},{t + 0.5});")
# 02 what it means
add(f"tl.from('#s2 .building',{{y:40,opacity:0,duration:.5,ease:'power2.out'}},{SPLIT_IN + 0.2});")
add(f"tl.fromTo('#s2 .flag',{{skewY:0}},{{skewY:6,duration:1.2,yoyo:true,repeat:5,ease:'sine.inOut'}},{SPLIT_IN});")
add(f"tl.fromTo('#doc',{{x:-500,rotation:-20}},{{x:0,rotation:-6,duration:.45,ease:'power3.out'}},{DOC_IN});")
add(f"tl.fromTo('#lens',{{x:-60,y:40,opacity:0}},{{x:0,y:0,opacity:1,duration:.3}},{MAGNIFY - 0.2});")
add(f"tl.to('#lens',{{x:150,y:-40,duration:1.4,ease:'sine.inOut'}},{MAGNIFY + 0.1});")
add(f"tl.fromTo('#rtk-1',{{scale:1.6,opacity:0}},{{scale:1,opacity:1,duration:.2,ease:'power3.in'}},{RIGHT_TO_KNOW - 0.15});")
add(f"tl.fromTo('#rtk-2',{{scale:1.6,opacity:0}},{{scale:1,opacity:1,duration:.2,ease:'power3.in'}},{RIGHT_TO_KNOW + 0.05});")
add(f"tl.fromTo('#what-gov',{{clipPath:'inset(0 100% 0 0)'}},{{clipPath:'inset(0 0% 0 0)',duration:.5,ease:'power2.out'}},{WHAT_GOV});")
add(f"tl.fromTo('#esp',{{x:60,opacity:0}},{{x:0,opacity:1,duration:.3,ease:'power2.out'}},{ESPECIALLY});")
add(f"tl.fromTo('#pm',{{scale:1.5,opacity:0,rotation:-4}},{{scale:1,opacity:1,rotation:-2,duration:.22,ease:'power3.in'}},{PUBLIC_MONEY - 0.12});")
# 03 example
add(f"tl.fromTo('#road-dash',{{strokeDashoffset:0}},{{strokeDashoffset:-900,duration:{TEAR4 - TEAR3 + 0.5:.2f},ease:'none'}},{TEAR3});")
add(f"tl.fromTo('.excavator',{{x:120,opacity:0}},{{x:0,opacity:1,duration:.6,ease:'power2.out'}},{TEAR3 + 0.3});")
add(f"tl.fromTo('.excavator .arm',{{rotation:0}},{{rotation:-8,duration:.8,yoyo:true,repeat:5,ease:'sine.inOut'}},{TEAR3 + 0.4});")
add(f"tl.fromTo('#alloc',{{y:-30,opacity:0}},{{y:0,opacity:1,duration:.3,ease:'power2.out'}},{ALLOCATES});")
add(f"tl.fromTo('#counter',{{opacity:0,scale:.9}},{{opacity:1,scale:1,duration:.2}},{COUNT_A - 0.1});")
STEPS = 24
for k in range(STEPS + 1):
    v = round(10_000_000 * (k / STEPS) ** 2 / 50_000) * 50_000
    add(f"tl.call(()=>{{cnum.textContent='{v:,}'}},null,{COUNT_A + (COUNT_B - COUNT_A) * k / STEPS:.3f});")
add(f"tl.call(()=>{{cnum.textContent='0'}},null,{TEAR3});")
add(f"tl.fromTo('#counter',{{scale:1.12}},{{scale:1,duration:.3,ease:'back.out(3)'}},{COUNT_B});")
add(f"tl.to('#counter .num',{{color:'#ffffff',duration:.1}},{COUNT_B});")
add(f"tl.fromTo('#for-road',{{scaleX:0}},{{scaleX:1,duration:.3,ease:'power3.out'}},{ROAD});")
add(f"tl.fromTo('#for-road span',{{opacity:0}},{{opacity:1,duration:.2}},{ROAD + 0.15});")
# 04 questions
add(f"tl.fromTo('#ask',{{opacity:0,y:-20}},{{opacity:1,y:0,duration:.3}},{ASK});")
for n, t in enumerate(CARDS):
    add(f"tl.fromTo('#card{n}',{{x:-1100}},{{x:0,duration:.4,ease:'power3.out'}},{t});")
    add(f"tl.fromTo('#card{n} .q-ico',{{scale:0}},{{scale:1,duration:.35,ease:'back.out(2.5)'}},{t + 0.2});")
add(f"tl.fromTo('#q-done',{{backgroundSize:'0% 100%'}},{{backgroundSize:'100% 100%',duration:.35}},{COMPLETED});")
# 05 limitations
add(f"tl.from('#s5 .folders',{{y:60,opacity:0,duration:.5,ease:'power2.out'}},{TEAR5 + 0.3});")
add(f"tl.from('#s5 .scales',{{opacity:0,y:-20,duration:.5}},{TEAR5 + 0.5});")
add(f"tl.fromTo('#s5 .scales g',{{rotation:-4}},{{rotation:4,duration:1.1,yoyo:true,repeat:5,ease:'sine.inOut',transformOrigin:'120px 50px'}},{TEAR5 + 0.5});")
add(f"tl.fromTo('#lim-1',{{opacity:0,x:40}},{{opacity:1,x:0,duration:.3}},{LIMITS - 0.6});")
add(f"tl.fromTo('#lim-2',{{scale:1.5,opacity:0}},{{scale:1,opacity:1,duration:.22,ease:'power3.in'}},{LIMITS - 0.12});")
add(f"tl.fromTo('#some-info',{{opacity:0,y:20}},{{opacity:1,y:0,duration:.35}},{SOME_INFO});")
add(f"tl.fromTo('#stamp',{{scale:2.2,opacity:0}},{{scale:1,opacity:1,duration:.16,ease:'power4.in'}},{STAMP - 0.11});")
add(f"tl.to('#s5 .folders',{{y:6,duration:.06,yoyo:true,repeat:1}},{STAMP + 0.05});")
add(f"tl.fromTo('#s5 .lock',{{opacity:0,y:30}},{{opacity:1,y:0,duration:.3}},{STAMP + 0.3});")
add(f"tl.fromTo('#shackle',{{y:-26}},{{y:0,duration:.18,ease:'power4.in'}},{LOCK});")
add(f"tl.to('#hl-conf',{{color:'#ff2a1f',duration:.15}},{STAMP});")
add(f"tl.to('#hl-law',{{color:'#ff2a1f',duration:.15}},{LOCK});")
# 06 why it matters
add(f"tl.fromTo('#why',{{y:-40,opacity:0}},{{y:0,opacity:1,duration:.35,ease:'power3.out'}},{WHY});")
for n, t in enumerate(ICONS):
    add(f"tl.fromTo('#ic{n}',{{scale:.4,opacity:0}},{{scale:1,opacity:1,duration:.4,ease:'back.out(2.2)'}},{t});")
    add(f"tl.fromTo('#ic{n} .ring',{{strokeDashoffset:760}},{{strokeDashoffset:0,duration:.5,ease:'power2.out'}},{t});")
    add(f"tl.fromTo('#ic{n}-label',{{opacity:0,y:20}},{{opacity:1,y:0,duration:.3}},{t + 0.12});")
# 07 closing
add(f"tl.fromTo('#punch',{{scale:1}},{{scale:1.08,duration:{SPEECH_END - SPLIT_OUT:.2f},ease:'none'}},{SPLIT_OUT});")
add(f"tl.fromTo('#cl-1',{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.3,ease:'power2.out'}},{SERVES});")
add(f"tl.fromTo('#cl-2',{{scaleX:0}},{{scaleX:1,duration:.3,ease:'power3.out'}},{KNOW});")
add(f"tl.fromTo('#cl-3',{{scaleX:0}},{{scaleX:1,duration:.3,ease:'power3.out'}},{OPERATES});")
add(f"tl.set('#closing',{{opacity:1}},{SERVES - 0.01});tl.set('#closing',{{opacity:0}},{SPEECH_END});")
# captions
for n, c in enumerate(CAPS):
    add(f"tl.set('#cap{n}',{{opacity:1}},{c['start']});tl.set('#cap{n}',{{opacity:0}},{c['end']});")
# end card
add(f"tl.fromTo('#tear-full',{{x:-1340}},{{x:1120,duration:.6,ease:'power2.inOut'}},{END_WIPE});")
add(f"tl.set('#tear-full',{{x:-1340}},{END_WIPE + 0.6});")
add(f"tl.fromTo('#ty-sun',{{rotation:-40,opacity:0,scale:.6}},{{rotation:0,opacity:1,scale:1,duration:.7,ease:'power3.out'}},{SPEECH_END + 0.05});")
add(f"tl.fromTo('#ty-text',{{clipPath:'inset(0 100% 0 0)'}},{{clipPath:'inset(0 0% 0 0)',duration:.7,ease:'power2.out'}},{SPEECH_END + 0.1});")
add(f"tl.fromTo('#ty-brush',{{scaleX:0}},{{scaleX:1,duration:.45,ease:'power2.out'}},{SPEECH_END + 0.55});")
add(f"tl.fromTo('#ty-sub',{{opacity:0}},{{opacity:1,duration:.4}},{SPEECH_END + 0.9});")
add(f"tl.to('#fade',{{opacity:1,duration:.5}},{DUR - 0.5});")
add(f"tl.set({{}},{{}},{DUR});")

cap_html = "\n".join(f'<div class="cap {c["style"]}" id="cap{n}"><span>{c["text"]}</span></div>' for n, c in enumerate(CAPS))
cards = [("bag", '<b>ASA PADULONG</b><br>ANG KWARTA?'), ("doc", '<b>GIUNSA</b><br>PAGGASTO?'),
         ("road", 'IS THE PROJECT<br>ACTUALLY <b id="q-done">COMPLETED?</b>')]
card_html = "".join(f'<div class="card" id="card{n}"><div class="q-ico">{svg(k)}</div><div class="q-txt">{txt}</div></div>'
                    for n, (k, txt) in enumerate(cards))
icons = [("lens", "TRANSPARENCY"), ("people", "ACCOUNTABILITY"), ("shield", "HELPS PREVENT<br>CORRUPTION")]
icon_html = "".join(f'<div class="why-col"><div class="why-ic" id="ic{n}"><svg class="ring" viewBox="0 0 250 250"><circle cx="125" cy="125" r="118"/></svg>'
                    f'{svg(k)}</div><div class="why-label" id="ic{n}-label">{label}</div></div>' for n, (k, label) in enumerate(icons))
road_svg = """<svg viewBox="0 0 1080 900" class="road"><defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#1c1c1c"/><stop offset="1" stop-color="#0d0d0d"/></linearGradient></defs>
 <path d="M500 440 L580 440 L1080 900 L0 900 Z" fill="#2b2b2b"/>
 <path d="M500 440 L0 900 M580 440 L1080 900" stroke="#d0d0d0" stroke-width="6"/>
 <path id="road-dash" d="M540 440 L540 900" stroke="#f2f2f2" stroke-width="14" stroke-dasharray="44 40" style="transform-origin:540px 440px;transform:perspective(400px)"/>
 <path d="M0 440 H1080" stroke="#444" stroke-width="3"/>
 <g fill="#3a3a3a">""" + "".join(f'<rect x="{x}" y="{440 - h}" width="{w}" height="{h}"/>' for x, w, h in
                                    ((20, 70, 60), (100, 40, 90), (150, 90, 40), (820, 60, 80), (890, 110, 50), (1010, 60, 70))) + """</g>
 <g fill="#e10600">""" + "".join(f'<path d="M{x} {y} l{s} 0 l-{s // 2} -{int(s * 1.6)} z"/>' for x, y, s in ((300, 700, 40), (360, 600, 28), (400, 530, 20))) + """</g>
</svg>"""

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1080, height=1920">
<title>Section 7 - Right to Information</title>
<script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:'Anton';src:url(assets/fonts/anton-400.woff2) format('woff2');font-display:block}}
@font-face{{font-family:'Oswald';src:url(assets/fonts/oswald-700.woff2) format('woff2');font-weight:200 700;font-display:block}}
@font-face{{font-family:'Kaushan Script';src:url(assets/fonts/kaushan-script-400.woff2) format('woff2');font-display:block}}
:root{{--red:#e10600;--ink:#0b0b0b;--paper:#e9e9e9}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000;color:#fff;font-family:'Oswald',sans-serif}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}}
.layer{{position:absolute;left:0;top:0;width:1080px;height:1920px}}
#shift,#punch{{position:absolute;left:0;top:0;width:1080px;height:1920px;transform-origin:540px 560px}}
#face{{display:block;width:1080px;height:1920px;object-fit:cover}}
.vignette{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 42%,transparent 55%,rgba(0,0,0,.45) 100%)}}
/* intro */
#title{{position:absolute;left:64px;top:70px;transform-origin:0 100%}}
#t-sec{{font-family:'Anton';font-size:178px;line-height:.95;letter-spacing:1px;color:#fff;text-shadow:0 6px 0 rgba(0,0,0,.55),0 0 30px rgba(0,0,0,.35)}}
#t-rti{{font-family:'Anton';font-size:98px;line-height:1.05;margin-top:4px;text-shadow:0 5px 0 rgba(0,0,0,.55)}}
#t-rti .r{{color:var(--red)}}
#t-brush{{width:760px;height:26px;margin-top:6px;transform-origin:0 50%}}
#l3{{position:absolute;left:0;top:1150px}}
#l3-name{{background:#fff;color:#000;font-family:'Anton';font-size:64px;line-height:1;padding:12px 40px 12px 64px;display:inline-block}}
#l3-tag{{display:block;width:max-content;margin-left:64px;background:var(--red);border:3px solid #000;color:#fff;font-weight:700;font-size:28px;letter-spacing:4px;padding:4px 16px;transform-origin:0 50%}}
/* split panel */
#panel{{position:absolute;left:0;top:0;width:1080px;height:960px}}
#panel-bg{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 30%,#232323,#0c0c0c 75%);clip-path:{PANEL_CLIP}}}
#seam{{position:absolute;left:0;top:0;width:1080px;height:960px;overflow:visible}}
.sec{{position:absolute;left:0;top:0;width:1080px;height:900px;opacity:0;overflow:hidden;clip-path:{PANEL_CLIP}}}
#tear{{position:absolute;left:0;top:0;width:1300px;height:960px;background:#dcdcdc;clip-path:{TEAR_CLIP};
  box-shadow:inset 0 0 80px rgba(0,0,0,.25)}}
.h-anton{{font-family:'Anton';line-height:.95}}
.callout{{display:inline-block;background:var(--red);color:#fff;font-family:'Anton';padding:6px 18px 10px}}
.callout.white{{background:#fff;color:#000}}
/* 02 */
#s2 .building{{position:absolute;left:30px;top:150px;width:520px;height:470px;overflow:visible}}
#s2 .building svg,#s2 svg.building{{overflow:visible}}
#doc{{position:absolute;left:90px;top:560px;width:380px;height:300px;background:#efefef;border-radius:4px;box-shadow:0 18px 40px rgba(0,0,0,.6);padding:34px 36px}}
#doc i{{display:block;height:12px;background:#b9b9b9;margin-bottom:18px;border-radius:6px}}
#doc i:nth-child(1){{width:60%;background:#7b7b7b;height:16px}}#doc i:nth-child(4){{width:80%}}#doc i:nth-child(6){{width:50%}}
#lens{{position:absolute;left:200px;top:600px;width:170px;height:170px;color:#fff}}
#lens svg{{width:170px;height:170px;fill:rgba(255,255,255,.08);stroke:#fff;stroke-width:5}}
#rtk{{position:absolute;left:580px;top:90px;width:470px}}
#rtk-1{{font-size:190px;color:#fff;transform-origin:0 50%}}#rtk-2{{font-size:150px;color:var(--red);transform-origin:0 50%;white-space:nowrap}}
#what-gov{{position:absolute;left:584px;top:470px;font-weight:700;font-size:44px;line-height:1.15;letter-spacing:1px;width:460px}}
#esp{{position:absolute;left:584px;top:632px;font-weight:700;font-size:34px;letter-spacing:2px;color:#cfcfcf}}
#pm{{position:absolute;left:566px;top:688px;font-size:78px;white-space:nowrap;transform-origin:30% 50%}}
/* 03 */
#s3 .road{{position:absolute;inset:0;width:1080px;height:900px}}
#s3 .excavator{{position:absolute;left:700px;top:500px;width:340px;height:230px}}
#alloc{{position:absolute;left:0;width:1080px;top:90px;text-align:center}}
#alloc span{{font-size:46px;padding:4px 22px 8px}}
#counter{{position:absolute;left:0;width:1080px;top:160px;text-align:center;font-family:'Anton';font-size:176px;line-height:1;
  color:var(--red);text-shadow:0 8px 0 rgba(0,0,0,.6);white-space:nowrap}}
#counter .num{{color:var(--red)}}
.peso{{position:relative;display:inline-block;margin-right:8px}}
.peso::before,.peso::after{{content:'';position:absolute;left:-10px;width:86px;height:12px;background:currentColor}}
.peso::before{{top:52px}}.peso::after{{top:80px}}
#for-road{{position:absolute;left:170px;top:370px;width:740px;height:84px;background:var(--red);transform-origin:0 50%;text-align:center}}
#for-road span{{font-family:'Anton';font-size:58px;line-height:84px;letter-spacing:1px}}
/* 04 */
#ask{{position:absolute;left:70px;top:34px;font-family:'Anton';font-size:76px;line-height:1;color:#fff}}
#ask b{{font-weight:400;color:var(--red)}}
.card{{position:absolute;left:70px;width:940px;height:200px;background:linear-gradient(90deg,#1d1d1d,#141414);border:2px solid #333;
  border-left:12px solid var(--red);display:flex;align-items:center;gap:36px;padding-left:34px;box-shadow:0 14px 30px rgba(0,0,0,.5)}}
#card0{{top:150px}}#card1{{top:385px}}#card2{{top:620px}}
.q-ico{{width:140px;height:140px;border-radius:50%;background:#fff;color:#000;display:flex;align-items:center;justify-content:center;flex:none}}
.q-ico .ico{{width:84px;height:84px}}
.q-txt{{font-family:'Anton';font-size:66px;line-height:1.05}}
.q-txt b{{font-weight:400;color:var(--red)}}
#q-done{{background:linear-gradient(var(--red),var(--red)) no-repeat 0 0/0% 100%;color:#fff;padding:0 8px}}
.ico{{fill:none;stroke:currentColor;stroke-width:5;stroke-linecap:round;stroke-linejoin:round}}
/* 05 */
#s5 .folders{{position:absolute;left:50px;top:110px;width:440px;height:380px}}
#stamp{{position:absolute;left:84px;top:300px;border:8px solid var(--red);color:var(--red);font-family:'Anton';font-size:64px;
  padding:0 18px 4px;transform:rotate(-12deg);letter-spacing:2px;background:rgba(225,6,0,.06)}}
#stamp-wrap{{position:absolute;left:0;top:0;transform:rotate(-12deg)}}
#s5 .lock{{position:absolute;left:330px;top:350px;width:160px;height:200px}}
#s5 .scales{{position:absolute;left:770px;top:80px;width:240px;height:200px}}
#lim-1{{position:absolute;left:560px;top:300px;font-family:'Anton';font-size:66px}}
#lim-2{{position:absolute;left:550px;top:385px;font-size:96px;transform-origin:20% 50%}}
#some-info{{position:absolute;left:70px;top:620px;width:940px;font-family:'Anton';font-size:58px;line-height:1.12;text-align:center}}
#some-info span{{transition:none}}
/* 06 */
#why{{position:absolute;left:0;width:1080px;top:70px;text-align:center;font-family:'Anton';font-size:118px;line-height:1}}
#why b{{font-weight:400;color:var(--red)}}
.why-row{{position:absolute;left:30px;width:1020px;top:290px;display:flex;justify-content:space-between}}
.why-col{{width:330px;display:flex;flex-direction:column;align-items:center}}
.why-ic{{position:relative;width:250px;height:250px;display:flex;align-items:center;justify-content:center;color:#fff}}
.why-ic .ring{{position:absolute;inset:0;width:250px;height:250px;fill:#161616;stroke:#fff;stroke-width:6;stroke-dasharray:760}}
.why-ic .ico{{position:relative;width:130px;height:130px}}
.why-label{{margin-top:26px;font-family:'Anton';font-size:50px;line-height:1.05;text-align:center}}
/* closing */
#closing{{position:absolute;left:60px;top:80px;opacity:0}}
#cl-1{{font-family:'Anton';font-size:66px;text-shadow:0 5px 0 rgba(0,0,0,.6);line-height:1.1}}
#cl-2,#cl-3{{display:block;width:max-content;margin-top:12px;font-size:60px;transform-origin:0 50%}}
/* captions */
#capwrap{{position:absolute;left:0;top:1330px;width:1080px;height:120px}}
.cap{{position:absolute;left:0;top:0;width:1080px;display:flex;justify-content:center;opacity:0}}
.cap span{{display:inline-block;max-width:960px;text-align:center;font-family:'Anton';font-size:76px;line-height:1.08;text-transform:uppercase;
  letter-spacing:1px;padding:6px 26px 12px;background:rgba(8,8,8,.9);border:2px solid rgba(255,255,255,.22);transform:rotate(-1deg)}}
.cap.red span{{background:var(--red);border-color:#000;transform:rotate(1deg)}}
/* end card */
#end-bg{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,#1d1d1d,#050505 70%)}}
#ty-sun{{position:absolute;left:730px;top:430px;opacity:.9}}
#ty-text{{position:absolute;left:0;top:700px;width:1080px;text-align:center;font-family:'Kaushan Script';font-size:200px;line-height:1.1;transform:rotate(-7deg)}}
#ty-brush{{position:absolute;left:180px;top:1000px;width:720px;height:60px;transform-origin:0 50%;transform:rotate(-7deg)}}
#ty-sub{{position:absolute;left:0;top:1220px;width:1080px;text-align:center;font-weight:700;font-size:34px;letter-spacing:8px;color:#bdbdbd}}
#tear-full{{position:absolute;left:0;top:0;width:1300px;height:1920px;background:#dcdcdc;clip-path:{TEAR_FULL_CLIP};
  box-shadow:inset 0 0 80px rgba(0,0,0,.25)}}
#grain{{position:absolute;inset:0;background-size:540px 960px;mix-blend-mode:overlay;opacity:.16;pointer-events:none}}
#fade{{position:absolute;inset:0;background:#000;opacity:0}}
</style></head><body>
<div id="root" data-composition-id="main" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="shift"><div id="punch">
    <video id="face" src="assets/edited.mov" muted playsinline data-start="0" data-duration="{SPEECH_END}" data-track-index="0"></video>
  </div></div>
  <audio id="mix" src="assets/audio/mix.wav" data-start="0" data-duration="{DUR}" data-track-index="1" data-volume="1"></audio>
  <div id="gfx" class="layer clip" data-start="0" data-duration="{SPEECH_END}" data-track-index="2">
    <div class="vignette"></div>
    <div id="title">
      <div id="t-sec">SECTION 7</div>
      <div id="t-rti"><span class="r">RIGHT TO</span> INFORMATION</div>
      <svg id="t-brush" viewBox="0 0 640 26" preserveAspectRatio="none"><path d="M4 18 C120 6 300 4 636 8 L628 16 C420 14 200 18 10 24 Z" fill="#e10600"/></svg>
    </div>
    <div id="l3"><div id="l3-name">ROGIE DOMIN</div><div id="l3-tag">PRESENTER</div></div>
    <div id="closing">
      <div id="cl-1">THE GOVERNMENT SERVES THE PEOPLE,</div>
      <div class="callout" id="cl-2">AND WE HAVE THE RIGHT TO KNOW</div>
      <div class="callout white" id="cl-3">HOW IT OPERATES.</div>
    </div>
    <div id="panel">
      <div id="panel-bg"></div>
      <div class="sec" id="s2">
        {BUILDING}
        <div id="doc"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
        <div id="lens">{svg('lens')}</div>
        <div id="rtk"><div class="h-anton" id="rtk-1">RIGHT</div><div class="h-anton" id="rtk-2">TO KNOW</div></div>
        <div id="what-gov">WHAT OUR GOVERNMENT IS DOING</div>
        <div id="esp">ESPECIALLY WHEN IT INVOLVES</div>
        <div class="callout" id="pm">PUBLIC MONEY.</div>
      </div>
      <div class="sec" id="s3">
        {road_svg}
        {EXCAVATOR}
        <div id="alloc"><span class="callout white">GOVERNMENT ALLOCATES</span></div>
        <div id="counter"><span class="peso">P</span><span class="num" id="cnum">0</span></div>
        <div id="for-road"><span>FOR ROAD CONSTRUCTION</span></div>
      </div>
      <div class="sec" id="s4"><div id="ask">WE HAVE THE RIGHT TO <b>ASK:</b></div>{card_html}</div>
      <div class="sec" id="s5">
        {FOLDERS}
        <div id="stamp">CONFIDENTIAL</div>
        {LOCK_SVG}
        {SCALES}
        <div id="lim-1">THIS RIGHT HAS</div>
        <div class="callout" id="lim-2">LIMITATIONS.</div>
        <div id="some-info">SOME GOVERNMENT INFORMATION IS <span id="hl-conf">CONFIDENTIAL</span> AND <span id="hl-law">PROTECTED BY LAW.</span></div>
      </div>
      <div class="sec" id="s6"><div id="why">WHY IT'S <b>IMPORTANT</b></div><div class="why-row">{icon_html}</div></div>
      <svg id="seam" viewBox="0 0 1080 960"><path d="{BRUSH_PATH}" fill="none" stroke="#e10600" stroke-width="12" stroke-linecap="round"/></svg>
      <div id="tear"></div>
    </div>
    <div id="capwrap">
{cap_html}
    </div>
  </div>
  <div id="end" class="layer clip" data-start="{SPEECH_END}" data-duration="{END_CARD}" data-track-index="3">
    <div id="end-bg"></div>
    <div id="ty-sun">{sun(210, '#ffffff')}</div>
    <div id="ty-text">Thank You!</div>
    <svg id="ty-brush" viewBox="0 0 720 60" preserveAspectRatio="none"><path d="M6 40 C160 14 420 8 714 18 L700 34 C470 30 240 40 14 56 Z" fill="#e10600"/></svg>
    <div id="ty-sub">SECTION 7 &middot; RIGHT TO INFORMATION</div>
  </div>
  <div id="fx" class="layer clip" data-start="0" data-duration="{DUR}" data-track-index="4">
    <div id="tear-full"></div>
    <div id="grain"></div>
    <div id="fade"></div>
  </div>
</div>
<script>
const cnum=document.getElementById('cnum');
{chr(10).join(js)}
window.__timelines=window.__timelines||{{}};window.__timelines['main']=tl;
</script>
</body></html>
"""
open(f"{P}/index.html", "w").write(html)
json.dump({"id": "main", "name": "section-7-right-to-information", "width": 1080, "height": 1920, "fps": FPS},
          open(f"{P}/meta.json", "w"), indent=2)
json.dump({"duration": DUR, "captions": [{k: c[k] for k in ("text", "start", "end", "style")} for c in CAPS],
           "sound_cues": [{"time": round(t, 3), "level_db": round(db, 1), "purpose": why} for t, _, db, why in CUES if why != "counter tick"],
           "beats": {"split_in": SPLIT_IN, "tears": [TEAR3, TEAR4, TEAR5, TEAR6], "split_out": SPLIT_OUT,
                     "counter": [COUNT_A, COUNT_B], "cards": CARDS, "stamp": STAMP, "lock": LOCK, "icons": ICONS,
                     "end_card": SPEECH_END}}, open(f"{P}/assets/cue-sheet.json", "w"), indent=1)
print(f"duration {DUR}s, {len(CAPS)} captions, {len(CUES)} sound cues, premix {m['input_i']} LUFS")
