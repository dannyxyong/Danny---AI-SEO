"""Original score + sound design for the Marvant AI SEO reel.

Everything is synthesised from scratch (no samples, no licensing), at 120 BPM so
scene cuts land on beats (2.0, 4.5, 7.5, 12.5 s). SFX times mirror reel.html.
Output: audio/bgm.wav (48 kHz stereo, unmastered; loudness is set in ffmpeg).
"""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 48000
DUR = 15.0
N = int(SR * DUR)
rng = np.random.default_rng(42)
BEAT = 0.5

def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def tt(d): return np.arange(int(SR * d)) / SR
def lp(x, f, o=2): return sosfilt(butter(o, min(f, SR / 2 - 100), 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
def saw(f, t, ph=0.0): return 2 * ((f * t + ph) % 1.0) - 1

class Bus:
    def __init__(self): self.L = np.zeros(N); self.R = np.zeros(N)
    def add(self, x, at, gain=1.0, pan=0.0):
        i = int(at * SR)
        if i >= N: return
        x = x[: N - i]
        gl, gr = np.sqrt((1 - pan) / 2) * gain, np.sqrt((1 + pan) / 2) * gain
        self.L[i:i + len(x)] += x * gl; self.R[i:i + len(x)] += x * gr
    def add_st(self, l, r, at, gain=1.0):
        i = int(at * SR); n = min(len(l), N - i)
        if n <= 0: return
        self.L[i:i + n] += l[:n] * gain; self.R[i:i + n] += r[:n] * gain

def reverb(bus, seconds=1.8, mix=0.25, tone=5000):
    n = int(SR * seconds); t = np.arange(n) / SR
    env = np.exp(-t * 6.9 / seconds)
    irl = lp(rng.standard_normal(n), tone) * env; irr = lp(rng.standard_normal(n), tone) * env
    irl[: int(.012 * SR)] = 0; irr[: int(.017 * SR)] = 0
    irl /= np.sqrt((irl ** 2).sum()); irr /= np.sqrt((irr ** 2).sum())
    wl = fftconvolve(bus.L, irl)[:N]; wr = fftconvolve(bus.R, irr)[:N]
    out = Bus(); out.L = bus.L + wl * mix; out.R = bus.R + wr * mix
    return out

def delay(bus, d=0.375, fb=0.35, mix=0.3):
    k = int(d * SR); L, R = bus.L.copy(), bus.R.copy(); wl, wr = np.zeros(N), np.zeros(N)
    srcL, srcR = bus.L, bus.R
    for rep in range(6):  # ping-pong
        g = mix * fb ** rep; s = k * (rep + 1)
        if s >= N: break
        if rep % 2 == 0: wr[s:] += srcL[:N - s] * g; wl[s:] += srcR[:N - s] * g
        else: wl[s:] += srcL[:N - s] * g; wr[s:] += srcR[:N - s] * g
    out = Bus(); out.L = L + lp(wl, 4000); out.R = R + lp(wr, 4000); return out

# ---------------------------------------------------------------- harmony
CH = {
    'Fmaj9': [53, 57, 60, 64, 67], 'Am7': [57, 60, 64, 67], 'Em7': [52, 55, 59, 62],
    'G6': [55, 59, 62, 64], 'G': [55, 59, 62, 67], 'Cmaj7': [60, 64, 67, 71], 'Cmaj9': [60, 64, 67, 71, 74],
}
ROOT = {'Fmaj9': 41, 'Am7': 45, 'Em7': 40, 'G6': 43, 'G': 43, 'Cmaj7': 36, 'Cmaj9': 36}
PROG = [(0, 'Fmaj9'), (2, 'Am7'), (3.5, 'Em7'), (4.5, 'Fmaj9'), (6, 'G6'), (7.5, 'Am7'), (8.5, 'Fmaj9'),
        (9.5, 'G'), (10.5, 'Cmaj7'), (12.5, 'Fmaj9'), (13.5, 'Cmaj9'), (15, None)]
def chord_at(t):
    for (a, c), (b, _) in zip(PROG, PROG[1:]):
        if a <= t < b: return c
    return 'Cmaj9'

# ---------------------------------------------------------------- drums
KICKS = [2 + i * BEAT for i in range(5)] + [4.5 + i * BEAT for i in range(5)] + \
        [7.5 + i * BEAT for i in range(9)] + [12.5, 13.0, 13.5, 14.0, 14.5]
def kick(gain=1.0):
    t = tt(.55); f = 44 + 120 * np.exp(-t * 28); ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 5.5); click = hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 300) * .25
    return np.tanh((body + click) * 1.6) * gain
def clap():
    t = tt(.3); n = bp(rng.standard_normal(len(t)), 900, 3500)
    env = np.zeros(len(t))
    for o in (0, .011, .022): env += (t >= o) * np.exp(-np.clip(t - o, 0, None) * 120) * .6
    env += (t >= .03) * np.exp(-np.clip(t - .03, 0, None) * 16)
    return n * env * .55
def hat(open_=False):
    t = tt(.25 if open_ else .06); return lp(hp(rng.standard_normal(len(t)), 7500, 4), 14000) * np.exp(-t * (14 if open_ else 70)) * .3

# sidechain envelope from kicks (pumps pad + bass)
sc = np.ones(N)
for k in KICKS:
    t = tt(.32); g = 1 - .62 * np.exp(-t * 14); i = int(k * SR); n = min(len(g), N - i); sc[i:i + n] = np.minimum(sc[i:i + n], g[:n])

drums = Bus()
for k in KICKS: drums.add(kick(1.0 if k >= 4.5 else .7), k, .9)
for b in np.arange(4.5, 12.0, BEAT):
    if round(b / BEAT) % 2 == 1: drums.add(clap(), b, .55, .05)
drums.add(clap(), 13.5, .55); drums.add(clap(), 14.5, .4)
for b in np.arange(2.0, 7.0, BEAT): drums.add(hat(), b + .25, .5 if b < 4.5 else .65, .3)
for b in np.arange(7.5, 12.0, .125): drums.add(hat(), b, .45 if (b * 8) % 2 else .3, .3 if (b * 8) % 2 else -.25)
for b in np.arange(12.5, 14.5, BEAT): drums.add(hat(True), b + .25, .35, .25)
# snare roll build 6.0 -> 7.3
t0 = 6.0; step = .25
while t0 < 7.3:
    drums.add(clap(), t0, .18 + .5 * (t0 - 6) / 1.3, rng.uniform(-.2, .2)); step = max(.0625, step * .82); t0 += step

# ---------------------------------------------------------------- bass
bass = np.zeros(N)
for b in np.arange(2.0, 14.75, .25):
    if 7.0 <= b < 7.5 or 12.0 <= b < 12.5: continue
    if b < 4.5 and (b * 4) % 2 == 0: continue        # sparse in the problem section
    c = chord_at(b + .01); f = hz(ROOT[c]); t = tt(.24)
    x = (saw(f, t) * .6 + np.sin(2 * np.pi * f * t)) * np.minimum(1, t * 200) * np.exp(-t * 6)
    i = int(b * SR); n = min(len(x), N - i); bass[i:i + n] += x[:n]
bass = lp(bass, 420, 4) * sc * .5
sub = np.zeros(N)  # impact + brand hit subs
for at, f0, d in ((7.5, 55, 1.6), (12.5, 49, 1.2), (14.5, 41, .5)):
    t = tt(d); f = f0 * (1 + .6 * np.exp(-t * 9)); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.4)
    i = int(at * SR); n = min(len(x), N - i); sub[i:i + n] += x[:n]

# ---------------------------------------------------------------- pad
pad = Bus()
for (a, c), (b, _) in zip(PROG, PROG[1:]):
    if c is None: continue
    d = b - a + .5; t = tt(d); env = np.minimum(1, t / .35) * np.clip((d - t) / .5, 0, 1)
    l = np.zeros(len(t)); r = np.zeros(len(t))
    for m in CH[c]:
        f = hz(m)
        for det, side in ((-7, 'l'), (0, 'b'), (7, 'r')):
            v = saw(f * 2 ** (det / 1200), t, rng.random())
            if side in 'lb': l += v
            if side in 'rb': r += v
    cut = 900 if a < 2 else 1800 if a < 7.5 else 2600
    pad.add_st(lp(l * env, cut, 2) * .045, lp(r * env, cut, 2) * .045, a)
pad.L *= sc * .9 + .1; pad.R *= sc * .9 + .1
pad = reverb(pad, 2.2, .35)

# ---------------------------------------------------------------- arp (16ths)
arp = Bus(); idx = 0
for b in np.arange(0, 14.5, .125):
    if 7.05 <= b < 7.5: continue
    c = chord_at(b + .01); notes = CH[c] + [n + 12 for n in CH[c]]; pat = [0, 2, 1, 3, 2, 4, 3, 5]
    m = notes[pat[idx % 8] % len(notes)] + 12; idx += 1
    f = hz(m); t = tt(.3)
    x = (saw(f, t) * .5 + np.sin(2 * np.pi * f * t)) * np.exp(-t * 16) * np.minimum(1, t * 400)
    cut = 700 + 2600 * min(1, b / 2.0) if b < 2 else (2400 if b < 7.5 else 3600)
    x = lp(x, cut, 2)
    acc = 1.0 if (b * 8) % 4 == 0 else .7
    g = (.22 if b < 2 else .13 if b < 7.5 else .15) * acc
    arp.add(x, b, g, .35 * np.sin(idx * 1.3))
arp = delay(arp, .375, .4, .28)
arp = reverb(arp, 1.4, .2)

# ---------------------------------------------------------------- brand stab (12.5) + final chord (14.5)
stab = Bus()
for at, c, d, g in ((12.5, 'Fmaj9', 1.0, .07), (13.0, 'Cmaj9', 1.4, .05), (14.5, 'Cmaj9', .5, .06)):
    t = tt(d)
    for m in CH[c] + [CH[c][0] + 12]:
        f = hz(m); x = (saw(f, t, rng.random()) * .4 + np.sin(2 * np.pi * f * t)) * np.exp(-t * 2.2) * np.minimum(1, t * 300)
        stab.add(lp(x, 3200), at, g, rng.uniform(-.4, .4))
stab = reverb(stab, 2.5, .45)

# ---------------------------------------------------------------- SFX
fx = Bus()
def noise(d): return rng.standard_normal(int(SR * d))
def whoosh(d=.5, lo=300, hi=5000, rev=False):
    n = noise(d); t = tt(d); k = t / d
    if rev: k = k[::-1]
    out = np.zeros(len(t)); seg = 512
    for s in range(0, len(t), seg):
        fc = lo * (hi / lo) ** (np.sin(np.pi * min(1, k[s] * 1.0)) if not rev else k[s])
        out[s:s + seg] = bp(n[max(0, s - 2048):s + seg], fc * .6, min(fc * 1.6, 20000), 2)[-len(n[s:s + seg]):]
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5 if not rev else (t / d) ** 2.5
    return out * env
def blip(f, d=.12, g=1.0):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + .25 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 32) * np.minimum(1, t * 800) * g
def click(f=2500, d=.02):
    t = tt(d); return lp((hp(noise(d), 1800) * .6 + np.sin(2 * np.pi * f * t)) * np.exp(-t * 260), 8500)
def bell(f, d=.9):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + .45 * np.sin(2 * np.pi * f * 2.01 * t) + .2 * np.sin(2 * np.pi * f * 3.02 * t)) * np.exp(-t * 6) * np.minimum(1, t * 600)

# hook: typing (mirrors nType = round(29 * P(t,.5,1.4)))
Q = 'Best interior designer in KL?'
for i, ch in enumerate(Q):
    at = .5 + (i + .5) / len(Q) * .9
    fx.add(click(rng.uniform(1800, 3200)), at, .16 if ch != ' ' else .09, rng.uniform(-.3, .3))
fx.add(click(1400, .04), 1.6, .45); fx.add(blip(hz(84), .2), 1.6, .35)                    # send tap
fx.add(whoosh(.55, 250, 5000), 1.85, .42, -.2)                                                 # bar -> card
fx.add(blip(hz(79)), 0.08, .25)                                                                # dot pop
for i, at in enumerate((2.55, 2.7, 2.85)): fx.add(blip(hz(76 + i * 3), .12), at, .28, -.2 + i * .2)  # answers stream
fx.add(whoosh(.35, 800, 6000), 3.15, .3, .5)                                                   # your brand slides in
for at in (3.65, 3.8):                                                                          # 'Not mentioned' error
    t = tt(.11); x = (np.sign(np.sin(2 * np.pi * 196 * t)) + np.sign(np.sin(2 * np.pi * 208 * t))) * .5 * np.exp(-t * 14)
    fx.add(lp(x, 1800), at, .28)
fx.add(whoosh(.5, 5000, 300, rev=True), 4.05, .35)                                             # collapse into core
for i in range(6): fx.add(blip(hz(72 + [0, 4, 7, 11, 14, 19][i]), .14), 4.82 + i * .08, .16, -.4 + i * .16)  # M draws
for i in range(8): fx.add(blip(hz([67, 71, 74, 79, 72, 76, 79, 84][i]), .1), 5.02 + i * .07, .18, -.6 + i * .17)  # pills pop
# build: riser + reverse cymbal into impact at 7.5
d = 1.4; t = tt(d); n = noise(d); out = np.zeros(len(t))
for s in range(0, len(t), 512):
    fc = 300 * (9000 / 300) ** ((s / len(t)) ** 1.4); out[s:s + 512] = bp(n[max(0, s - 2048):s + 512], fc * .7, min(fc * 1.4, 20000))[-len(n[s:s + 512]):]
fx.add(out * (t / d) ** 2 * .9 + saw(110 * 2 ** (t * 2 / d), t) * (t / d) ** 3 * .06, 6.1, .5)
fx.add(hp(noise(.6), 5000) * (tt(.6) / .6) ** 3, 6.9, .3)
t = tt(1.5); fx.add(lp(noise(1.5), 1200) * np.exp(-t * 4), 7.5, .5)                            # impact noise
# how it works: checks
for i, at in enumerate((8.2, 8.9, 9.4)):
    fx.add(bell(hz([84, 88, 91][i])), at, .16, -.15 + i * .15)
for i, at in enumerate((8.45, 8.95)): fx.add(whoosh(.4, 600, 3000), at, .12)                  # dot travels
for i in range(4): fx.add(blip(hz([79, 83, 86, 91][i]), .1), 9.47 + i * .08, .15, -.45 + i * .3)  # engine chips
fx.add(whoosh(.6, 300, 4500), 9.95, .38, .2)                                                    # dot -> answer card
fx.add(blip(hz(88), .3), 10.78, .3); fx.add(bell(hz(96), 1.2), 10.8, .12)                      # top pick
for i in range(14):                                                                              # sparkle burst
    fx.add(blip(rng.uniform(2500, 5200), .09), 11.05 + i * .025, .07, rng.uniform(-.8, .8))
fx.add(whoosh(.55, 5000, 300, rev=True), 12.0, .35)                                             # fold into logo
for i in range(7): fx.add(click(rng.uniform(3000, 4200), .015), 13.05 + i * .045, .12, -.5 + i * .16)  # letters
fx.add(whoosh(.5, 2000, 9000), 13.3, .14)                                                       # EVOLUTIONS tracks in
fx.add(blip(hz(79), .25), 13.75, .26); fx.add(blip(hz(86), .25), 13.83, .2)                    # CTA pops
fx.add(hp(whoosh(.45, 3000, 12000), 2500), 14.05, .16, .4)                                      # shimmer
fx.add(click(1100, .05), 14.45, .55); t = tt(.15); fx.add(np.sin(2 * np.pi * 90 * t) * np.exp(-t * 30), 14.45, .35)  # tap
fx = reverb(fx, 1.2, .18, 7000)

# ---------------------------------------------------------------- mix
L = drums.L * .8 + bass + sub * .7 + pad.L + arp.L * 2.6 + stab.L * 1.3 + fx.L * 1.6
R = drums.R * .8 + bass + sub * .7 + pad.R + arp.R * 2.6 + stab.R * 1.3 + fx.R * 1.6
mixd = np.stack([L, R], 1)
mixd = sosfilt(butter(2, 28, 'high', fs=SR, output='sos'), mixd, axis=0)
fade = np.ones(N); a = int(14.55 * SR); fade[a:] = np.linspace(1, 0, N - a) ** 1.5
fi = int(.01 * SR); fade[:fi] = np.linspace(0, 1, fi)
mixd *= fade[:, None]
mixd = np.tanh(mixd / np.abs(mixd).max() * 1.4) / np.tanh(1.4) * .89
wavfile.write('audio/bgm.wav', SR, (mixd * 32767).astype(np.int16))
print('peak', np.abs(mixd).max(), 'rms', np.sqrt((mixd ** 2).mean()))
