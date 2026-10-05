#!/usr/bin/env bash
# Final mix: voiceover over the score, music ducked under speech (sidechain), loudness -14 LUFS.
set -e; cd "$(dirname "$0")"
ffmpeg -loglevel error -y -i bgm.wav -i vo/vo_af_heart.wav -filter_complex "
[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0,highpass=f=90,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3500:t=q:w=1.0:g=3,
 acompressor=threshold=-22dB:ratio=3:attack=4:release=90:makeup=4,volume=1.0,asplit=2[vo][key];
[0:a]volume=0.75[bg];
[bg][key]sidechaincompress=threshold=0.06:ratio=3:attack=20:release=300:makeup=1[duck];
[duck][vo]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89,loudnorm=I=-14:TP=-1.5:LRA=11[out]" \
 -map "[out]" -ar 48000 -c:a pcm_s16le final_mix.wav
