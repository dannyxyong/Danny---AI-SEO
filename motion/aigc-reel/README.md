# Marvant Evolutions · AIGC reel (9:16, 15s)

`out/marvant_aigc_reel.mp4` is 1080×1920, 30 fps, 15.0 s, H.264 + AAC, loudness-normalized to −14 LUFS for Instagram.

| Time | Scene | Voiceover |
|---|---|---|
| 0:00–2.25 | AI prompt types "Create my next campaign", then the camera zooms through the send button | "What if your content… created itself?" |
| 2.25–5.25 | A·I·G·C letters slam in, then unfold into Artificial / Intelligence / Generated / Content | "Meet A-I-G-C. AI-generated content." |
| 5.25–8.25 | One card morphs between formats: Images, Videos, Copy, Voice (the voice waveform follows the real VO) | "Images. Videos. Copy. Voice." |
| 8.25–9.75 | A clock dial spins, "MINUTES" slams in, "not months" gets struck through | "Made in minutes, not months." |
| 9.75–12.5 | A 10× counter and content tiles multiply, then the cost bar shrinks | "Ten times the output. A fraction of the cost." |
| 12.5–15 | Marvant logo reveal, tagline and CTA pill | "Marvant Evolutions. Create what's next." |

All text stays inside the Instagram Reels safe zone (y 250–1500, clear of the right-hand button column).

## Rebuild
- VO: `python vo.py <dir> af_heart 1.1`, which runs Kokoro-82M offline neural TTS
- Music, SFX and mix: `python audio.py .` (fully synthesized, 120 BPM, no samples or licensing needed)
- Video: `node render.js video silent.mp4 6`, which renders the canvas in Playwright with 6-subframe motion blur. Then mux with `out_mix.wav`.
- Safe-zone check: `node render.js stills st 1.0 3.5 ...` draws the IG UI guides over each still.

The logo mark is vectorized from the supplied PNG. The "MARVANT / DIGITAL MARKETING" wordmark is set in Poppins and fitted to the mark width so it stays sharp at full size.
