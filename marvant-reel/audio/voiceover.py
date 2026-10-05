"""Voiceover for the Marvant AI SEO reel, generated with Kokoro-82M (Apache-2.0).

Model: Kokoro-82M fp16 ONNX (npm kokoro-fp16-shards, concatenated); voice styles from
the official kokoro-js package (hexgrad). Each line is fitted to its scene window.
Usage: python3 audio/voiceover.py <kokoro-fp16.onnx> <kokoro-js voices dir> [voice]
"""
import sys, glob, os, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

MODEL, VDIR = sys.argv[1], sys.argv[2]
VOICE = sys.argv[3] if len(sys.argv) > 3 else 'af_heart'
SR = 24000
# (start, latest end, text) — windows follow the on-screen headlines in reel.html
LINES = [
    (0.15, 1.90, "Your customers now ask AI."),
    (2.15, 4.35, "But is your brand in the answer?"),
    (4.50, 7.62, "With Marvant AI SEO, every AI finds you."),
    (7.75, 10.05, "We engineer your brand to be cited."),
    (10.35, 12.35, "Now, AI recommends you."),
    (12.50, 14.90, "Marvant. Get your free AI SEO audit."),
]
vp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vo', 'voices.npz')
if not os.path.exists(vp):
    np.savez(vp, **{os.path.basename(f)[:-4]: np.fromfile(f, dtype=np.float32).reshape(-1, 1, 256)
                    for f in glob.glob(os.path.join(VDIR, '*.bin')) if os.path.basename(f)[:2] in ('af', 'am', 'bf', 'bm')})
k = Kokoro(MODEL, vp)

def trim(x, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    if not len(idx): return x
    a, b = max(0, idx[0] - int(.02 * SR)), min(len(x), idx[-1] + int(.06 * SR))
    return x[a:b]

out = np.zeros(int(15 * SR), np.float32); cues = []
for st, en, text in LINES:
    speed = 1.0
    for _ in range(8):
        for nudge in range(6):   # the fp16 export occasionally returns silence; nudge speed and retry
            a, sr = k.create(text, voice=VOICE, speed=speed + nudge * .007, lang='en-us')
            if len(a) and np.abs(a).max() > .05: break
        a = trim(a)
        d = len(a) / sr
        if d <= en - st or speed >= 1.3: break
        speed = min(1.3, speed * d / (en - st) * 1.02)
    i = int(st * SR); out[i:i + len(a)] += a[:len(out) - i]
    cues.append((st, st + d, speed, text)); print(f'{st:5.2f}-{st+d:5.2f}  speed {speed:.2f}  {text}')
sf.write(os.path.join(os.path.dirname(vp), f'vo_{VOICE}.wav'), out, SR)
with open(os.path.join(os.path.dirname(vp), 'cues.txt'), 'w') as f:
    for c in cues: f.write('%.2f\t%.2f\t%.2f\t%s\n' % c)
