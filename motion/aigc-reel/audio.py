# Synthesized BGM + SFX + VO mix for the Marvant AIGC reel.
import json, sys, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly

P = sys.argv[1]
TL = json.load(open(f"{P}/timeline.json"))
SR = 48000
DUR = TL["dur"]
N = int(SR * DUR)
rng = np.random.default_rng(7)

def t_(n): return np.arange(n) / SR
def at(buf, x, t0, gain=1.0):
    i = int(round(t0 * SR))
    if i >= len(buf): return
    if x.ndim == 1: x = np.stack([x, x], 1)
    j = min(len(buf), i + len(x))
    if i < 0: x = x[-i:]; i = 0
    buf[i:j] += x[: j - i] * gain
def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x, axis=0)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x, axis=0)
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x, axis=0)
def env(n, a, d, curve=4.0):
    t = t_(n); e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) * curve / max(d, 1e-4))
    return e
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def saw(f, n, ph=0.0):
    # band-limited-ish saw via polyBLEP
    t = (ph + np.cumsum(np.full(n, f / SR))) % 1.0 if np.isscalar(f) else (ph + np.cumsum(f / SR)) % 1.0
    dt = (f / SR) if np.isscalar(f) else f / SR
    y = 2 * t - 1
    m1 = t < dt; y[m1] -= (lambda u: u + u - u * u - 1)(t[m1] / (dt if np.isscalar(dt) else dt[m1]))
    m2 = t > 1 - (dt if np.isscalar(dt) else dt)
    u = (t[m2] - 1) / (dt if np.isscalar(dt) else dt[m2]); y[m2] -= u * u + u + u + 1
    return y
def pan(x, p):  # p -1..1
    l = np.cos((p + 1) * np.pi / 4); r = np.sin((p + 1) * np.pi / 4)
    return np.stack([x * l, x * r], 1)

def reverb_ir(sec=2.2, decay=3.0):
    n = int(SR * sec); t = t_(n)
    ir = rng.standard_normal((n, 2)) * np.exp(-t * decay)[:, None]
    ir = lp(ir, 7000); ir[:200] *= np.linspace(0, 1, 200)[:, None]
    return ir / np.sqrt((ir ** 2).sum(0))

# ---------- instruments ----------
def kick(big=False):
    n = int(SR * (0.9 if big else 0.45)); t = t_(n)
    f = 48 + 180 * np.exp(-t * 32) + (25 * np.exp(-t * 4) if big else 0)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t * (3.2 if big else 7.5))
    y += 0.5 * rng.standard_normal(n) * np.exp(-t * 300)  # click
    return np.tanh(y * 1.6) * 0.9
def clap():
    n = int(SR * 0.35); t = t_(n); nz = rng.standard_normal(n)
    e = np.zeros(n)
    for o in (0, 0.011, 0.022): e += (t >= o) * np.exp(-np.maximum(0, t - o) * 90)
    e += (t >= 0.03) * np.exp(-np.maximum(0, t - 0.03) * 14) * 0.6
    return bp(nz * e, 900, 5200) * 1.6
def hat(open_=False):
    n = int(SR * (0.22 if open_ else 0.05)); t = t_(n)
    y = hp(rng.standard_normal(n), 7500) * np.exp(-t * (14 if open_ else 80))
    return y * 0.5
def snare():
    n = int(SR * 0.25); t = t_(n)
    y = bp(rng.standard_normal(n), 1500, 8000) * np.exp(-t * 22) + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    return y * 0.8
def pluck(m, dur=0.22, bright=4000):
    n = int(SR * dur); t = t_(n)
    y = saw(mtof(m), n) * 0.6 + saw(mtof(m) * 1.005, n) * 0.4
    y = lp(y * np.exp(-t * 14), bright)
    return y * 0.35
def pad(notes, dur, cutoff=1800, det=0.006):
    n = int(SR * dur); t = t_(n); L = np.zeros(n); R = np.zeros(n)
    for m in notes:
        for k, d in enumerate((-det, 0, det)):
            v = saw(mtof(m) * (1 + d), n, rng.random())
            if k == 0: L += v
            elif k == 2: R += v
            else: L += v * .5; R += v * .5
    st = np.stack([L, R], 1) / (len(notes) * 1.5)
    st = lp(st, cutoff, 2)
    e = np.minimum(1, t / 0.25) * np.minimum(1, (dur - t) / 0.3).clip(0)
    return st * e[:, None]
def stab(notes, dur=0.3):
    n = int(SR * dur); t = t_(n); y = np.zeros(n)
    for m in notes:
        y += saw(mtof(m), n) + saw(mtof(m) * 1.008, n)
    fc = 1200 + 5000 * np.exp(-t * 18)
    # time-varying LP approx: blend two filters
    a = lp(y, 6500); b = lp(y, 1200); w = np.exp(-t * 14)
    return (a * w + b * (1 - w)) * np.exp(-t * 6) * 0.16 / len(notes) * 3
def bass(m, dur):
    n = int(SR * dur); t = t_(n); f = mtof(m)
    y = np.sin(2 * np.pi * f * t) + 0.35 * lp(saw(f, n), 600)
    e = np.minimum(1, t / 0.005) * np.minimum(1, (dur - t) / 0.02).clip(0)
    return np.tanh(y * 1.4 * e) * 0.5
def whoosh(dur=0.5, up=True, lo=300, hi=9000):
    n = int(SR * dur); t = t_(n); x = rng.standard_normal(n)
    k = t / dur
    sweep = k if up else 1 - k
    # chunked band sweep
    out = np.zeros(n); C = 24
    for c in range(C):
        s, e = c * n // C, (c + 1) * n // C
        fc = lo * (hi / lo) ** sweep[(s + e) // 2]
        out[s:e] = bp(x[max(0, s - 2000):e], fc * .6, min(fc * 1.6, 20000))[-(e - s):]
    amp = np.sin(np.pi * k) ** 1.5 if True else 1
    return pan(out * amp * 0.9, 0)
def riser(dur):
    n = int(SR * dur); t = t_(n); k = t / dur
    f = 200 * (12) ** k
    y = saw(f, n) * 0.25 + saw(f * 1.5, n) * 0.12
    nz = hp(rng.standard_normal(n), 2000) * 0.35
    y = lp(y, 5000) + nz * k
    return y * k ** 2.2 * 0.7
def impact():
    n = int(SR * 2.5); t = t_(n)
    sub = np.sin(2 * np.pi * np.cumsum(30 + 70 * np.exp(-t * 6)) / SR) * np.exp(-t * 1.6)
    nz = lp(rng.standard_normal(n), 2500) * np.exp(-t * 5)
    return np.tanh((sub * 1.3 + nz * 0.6) * 1.5) * 0.8
def blip(f, dur=0.06, g=0.25):
    n = int(SR * dur); t = t_(n)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 60) * g
def click():
    n = int(SR * 0.03); t = t_(n)
    return hp(rng.standard_normal(n), 3000) * np.exp(-t * 400) * 0.35 + np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 300) * 0.12
def glitch(dur=0.18):
    n = int(SR * dur); y = np.zeros(n); i = 0
    while i < n:
        L = int(rng.integers(150, 1400)); f = rng.choice([220, 440, 880, 1760, 3520]) * (1 + rng.random() * .1)
        seg = np.sign(np.sin(2 * np.pi * f * t_(L))) * 0.18 if rng.random() < .6 else rng.standard_normal(L) * .2
        y[i:i + L] = seg[: n - i]; i += L
    return y * np.exp(-t_(n) * 12)
def revswell(dur):
    x = hp(rng.standard_normal(int(SR * dur)), 3000) * np.linspace(0, 1, int(SR * dur)) ** 3
    return x * 0.5
def shimmer(dur=1.4):
    n = int(SR * dur); t = t_(n); y = np.zeros(n)
    for m in (81, 84, 88, 93, 96):
        y += np.sin(2 * np.pi * mtof(m) * t + rng.random() * 6) * np.exp(-t * 2.5) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t + m))
    return y * 0.06 * np.minimum(1, t / 0.08)

# ---------- arrangement ----------
music = np.zeros((N, 2)); drums = np.zeros((N, 2)); sfx = np.zeros((N, 2)); verb_send = np.zeros((N, 2))
B = 0.5; G0 = 2.25
beat = lambda k: G0 + k * B
CH = {"Am": [57, 60, 64], "F": [53, 57, 60], "C": [52, 55, 60], "G": [55, 59, 62]}
ROOT = {"Am": 33, "F": 29, "C": 36, "G": 31}
prog = [("Am", 2.25), ("F", 4.25), ("C", 6.25), ("G", 8.25), ("Am", 10.25), ("F", 11.25)]

# intro pad + arp (0 - 2.25)
at(music, pad([57, 64, 69, 71], 2.6, 900), 0.0, 0.8)
arp = [69, 72, 76, 79, 76, 72]
for i in range(int(2.0 / 0.125)):
    tt = 0.25 + i * 0.125
    if tt < 2.1: at(verb_send, pan(pluck(arp[i % 6], 0.2, 1500 + i * 220), (-0.5 if i % 2 else 0.5)), tt, 0.45 + 0.4 * i / 16)
for i in range(8):
    at(drums, hat(), 0.25 + i * 0.25, 0.25)
# typing clicks
txt_n = 23
for i in range(txt_n):
    at(sfx, pan(click(), rng.uniform(-.3, .3)), 0.42 + i * 0.05 + rng.uniform(-.006, .006), 0.55)
at(sfx, blip(1200, 0.08, 0.3), 1.88); at(sfx, blip(1800, 0.08, 0.25), 1.94)
at(sfx, pan(riser(1.15), 0), 1.08, 0.9)
at(sfx, revswell(0.9), 1.35, 0.8)

# groove 2.25 - 12.25
for k in range(0, 20):
    tt = beat(k)
    if tt >= 12.24: break
    at(drums, kick(), tt, 0.95)
    if k % 2 == 1: at(drums, clap(), tt, 0.55)
    at(drums, pan(hat(True), 0.2), tt + B / 2, 0.28)
    for s in (0, 1, 2, 3):
        if s != 2: at(drums, pan(hat(), -0.25), tt + s * B / 4, 0.18 + 0.06 * (s == 1))
for name, t0 in prog:
    t1 = min(t0 + 2.0, 12.25)
    for j in range(int(round((t1 - t0) / 0.25))):
        tt = t0 + j * 0.25
        at(music, bass(ROOT[name] + (12 if j % 4 == 3 else 0), 0.22), tt, 0.85)
    for j in (0, 0.75, 1.5):
        if t0 + j < t1: at(verb_send, pan(stab([m + 12 for m in CH[name]], 0.32), 0), t0 + j, 0.75)
    at(music, pad([m + 12 for m in CH[name]], t1 - t0 + 0.3, 2400), t0, 0.32)
    # arp over groove
    for j in range(int((t1 - t0) / 0.125)):
        m = CH[name][j % 3] + 24 + (12 if j % 8 == 7 else 0)
        at(verb_send, pan(pluck(m, 0.15, 3500), np.sin(j)), t0 + j * 0.125, 0.18)

# drop 2.25
at(sfx, impact(), 2.25, 1.0); at(drums, kick(True), 2.25, 1.0)
at(sfx, whoosh(0.35, False, 400, 9000), 2.2, 0.6)
# AIGC letter slams
for i, tt in enumerate((2.64, 2.89, 3.13, 3.36)):
    at(sfx, glitch(0.16), tt, 0.7); at(sfx, kick(), tt, 0.35)
at(sfx, whoosh(0.5, True), 3.4, 0.5)       # unfold
# montage
for i, tt in enumerate((5.25, 6.0, 6.75, 7.5)):
    at(sfx, whoosh(0.32, True, 600, 12000), tt - 0.22, 0.55)
    at(sfx, blip([880, 988, 1175, 1319][i], 0.12, 0.3), tt, 1.0)
for i in range(18):  # "generating" data ticks
    at(sfx, pan(blip(2400 + 300 * (i % 4), 0.03, 0.08), rng.uniform(-.6, .6)), 5.3 + i * 0.16)
# minutes scene
at(sfx, whoosh(0.4, False, 300, 8000), 8.05, 0.6); at(sfx, impact(), 8.25, 0.45)
for i in range(12): at(sfx, pan(click(), (-1) ** i * .4), 8.35 + i * 0.1, 0.35)
at(sfx, whoosh(0.3, True, 1500, 14000), 9.08, 0.6)      # strike
# 10x scene
at(sfx, whoosh(0.35, False, 300, 8000), 9.55, 0.6); at(sfx, impact(), 9.75, 0.5)
for i in range(10): at(sfx, blip(600 * 2 ** (i / 12 * 1.6), 0.07, 0.22), 9.9 + i * 0.075)
at(sfx, glitch(0.2), 10.7, 0.6)
at(sfx, whoosh(0.6, False, 200, 6000), 11.05, 0.55)    # cost drops
for i in range(16):
    at(drums, snare(), 11.25 + i * 0.0625, 0.15 + 0.5 * i / 16)
at(sfx, riser(1.25), 11.0, 1.0)
at(sfx, revswell(0.5), 12.0, 1.0)
# final drop 12.5
at(sfx, impact(), 12.5, 1.15); at(drums, kick(True), 12.5, 1.1)
at(verb_send, pan(stab([57, 60, 64, 69, 71], 0.9), 0), 12.5, 1.2)
at(music, pad([45, 57, 64, 69, 71, 76], 2.6, 3000, 0.008), 12.5, 0.55)
at(music, bass(33, 1.6), 12.5, 0.9)
at(sfx, shimmer(1.8), 12.62, 1.0)
for k in range(4):
    tt = 12.5 + k * 0.5
    if k: at(drums, kick(), tt, 0.7)
    at(drums, pan(hat(True), .2), tt + 0.25, 0.22)
    if k % 2 == 1: at(drums, clap(), tt, 0.45)
for i in range(16):
    at(verb_send, pan(pluck([69, 72, 76, 81][i % 4] + 12, 0.18, 4500), (-.6, .6)[i % 2]), 12.5 + i * 0.125, 0.2)
at(sfx, whoosh(0.4, True, 800, 12000), 13.75, 0.4)
at(sfx, blip(1568, 0.15, 0.3), 14.05)  # CTA pop
at(drums, kick(True), 14.5, 0.6); at(sfx, impact(), 14.5, 0.35)
at(verb_send, pan(stab([57, 64, 69, 72, 76], 0.6), 0), 14.5, 0.8)

# reverb bus
ir = reverb_ir()
wet = np.stack([fftconvolve(verb_send[:, c], ir[:, c])[:N] for c in range(2)], 1)
wet2 = np.stack([fftconvolve(sfx[:, c] * 0.25, ir[:, c])[:N] for c in range(2)], 1)
music = music + verb_send * 0.8 + wet * 0.45
# sidechain pump from kicks on groove
pump = np.ones(N)
for k in range(0, 20):
    tt = beat(k)
    if tt >= 12.24: break
    i = int(tt * SR); L = int(0.3 * SR); j = min(N, i + L)
    pump[i:j] = np.minimum(pump[i:j], 0.45 + 0.55 * (np.arange(j - i) / L) ** 0.6)
music *= pump[:, None]
bgm = music * 0.8 + drums * 0.9 + sfx * 0.85 + wet2 * 0.5

# ---------- VO ----------
vo = np.zeros((N, 2))
for key, t0 in TL["vo"]:
    x, sr = sf.read(f"{P}/vo/{TL['voice']}_{key}.wav")
    if x.ndim > 1: x = x.mean(1)
    x = resample_poly(x, SR, sr)
    x = x / (np.abs(x).max() + 1e-9) * 0.9
    # presence lift + gentle low cut
    x = hp(x, 90) + 0.25 * bp(x, 2500, 6000)
    end = t0 + len(x) / SR
    if end > DUR: print("WARN VO overruns", key, end)
    at(vo, x, t0)
# compress VO lightly
a = np.abs(vo).max(1); e = np.convolve(a, np.ones(480) / 480, 'same')
g = np.where(e > 0.3, (0.3 + (e - 0.3) * 0.4) / np.maximum(e, 1e-9), 1)
vo *= g[:, None]; vo /= np.abs(vo).max() / 0.9
vo_rev = np.stack([fftconvolve(vo[:, c], reverb_ir(0.8, 7)[:, c])[:N] for c in range(2)], 1)
vo = vo + vo_rev * 0.08
# duck music under VO
ve = np.convolve(np.abs(vo).max(1), np.ones(4800) / 4800, 'same')
duck = 1 - 0.5 * np.clip(ve / 0.08, 0, 1)
bgm *= duck[:, None]

mix = bgm * 0.55 + vo * 1.0
# fade out tail
fo = int(0.35 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix /= np.abs(mix).max() / 0.95
sf.write(f"{P}/out_mix.wav", mix.astype(np.float32), SR)
sf.write(f"{P}/out_bgm.wav", (bgm / np.abs(bgm).max() * 0.9).astype(np.float32), SR)
sf.write(f"{P}/out_vo.wav", (vo / np.abs(vo).max() * 0.9).astype(np.float32), SR)
print("ok")
