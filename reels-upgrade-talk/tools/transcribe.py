import sys, json, wave, numpy as np
from faster_whisper import WhisperModel
w = wave.open(sys.argv[1]); assert w.getframerate()==16000 and w.getnchannels()==1
audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)/32768.0
model = WhisperModel("/tmp/claude-0/-home-user-Video-Editing-/340d1117-3082-5632-86b7-bfc284cb0d6e/scratchpad/whisper-small", device="cpu", compute_type="int8")
segments, info = model.transcribe(audio, beam_size=5, vad_filter=True)
print("lang", info.language, info.language_probability, file=sys.stderr)
out=[]
with open(sys.argv[2],"w") as f:
    for s in segments:
        out.append({"start":round(s.start,2),"end":round(s.end,2),"text":s.text.strip()})
        f.write(f"[{s.start:7.2f} - {s.end:7.2f}] {s.text.strip()}\n"); f.flush()
json.dump(out, open(sys.argv[2]+".json","w"), ensure_ascii=False, indent=1)
