import sys, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
S=sys.argv[1]; voice=sys.argv[2]; speed=float(sys.argv[3])
k=Kokoro(f"{S}/tts/kokoro.onnx", f"{S}/tts/voices.bin")
lines={
 "p1":"What if your content… created itself?",
 "p2":"Meet A. I. G. C.",
 "p2b":"A.I. generated content.",
 "p3a":"Images.","p3b":"Videos.","p3c":"Copy.","p3d":"Voice.",
 "p4":"Made in minutes, not months.",
 "p5":"Ten times the output. A fraction of the cost.",
 "p6":"Marvant Evolutions.",
 "p7":"Create what's next.",
}
for key,txt in lines.items():
    a,sr=k.create(txt, voice=voice, speed=speed, lang="en-us")
    # trim silence
    idx=np.where(np.abs(a)>0.01)[0]; a=a[max(0,idx[0]-240):idx[-1]+800]
    sf.write(f"{S}/proj/vo/{voice}_{key}.wav", a, sr)
    print(voice,key,round(len(a)/sr,2))
