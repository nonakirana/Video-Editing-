import sys, json, wave, numpy as np
from faster_whisper import WhisperModel
w = wave.open(sys.argv[1]); audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)/32768.0
model = WhisperModel("/tmp/claude-0/-home-user-Video-Editing-/340d1117-3082-5632-86b7-bfc284cb0d6e/scratchpad/whisper-small", device="cpu", compute_type="int8")
segments, info = model.transcribe(audio, language="ms", beam_size=5, vad_filter=True, word_timestamps=True)
out=[]
for s in segments:
    for wd in (s.words or []):
        out.append({"start":round(wd.start,3),"end":round(wd.end,3),"word":wd.word.strip(),"p":round(wd.probability,2)})
json.dump(out, open(sys.argv[2],"w"), ensure_ascii=False)
print(len(out),"words")
