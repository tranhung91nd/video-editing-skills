"""Generate several takes per narration sentence with VieNeu (voice in script.json).
Run: <VieNeu venv>/bin/python voice_generate.py <job>/voice [takes] [ids...]"""
import json, sys
from pathlib import Path
import soundfile as sf
from vieneu import Vieneu

VOICE = Path(sys.argv[1])
takes = int(sys.argv[2]) if len(sys.argv) > 2 else 4
only = set(sys.argv[3:])
script = json.loads((VOICE / "script.json").read_text(encoding="utf-8"))
(VOICE / "takes").mkdir(exist_ok=True)
tts = Vieneu()
for s in script["sentences"]:
    if only and s["id"] not in only:
        continue
    for t in range(1, takes + 1):
        out = VOICE / "takes" / f"{s['id']}_t{t}.wav"
        if out.exists():
            continue
        audio = tts.infer(s["tts"], voice=script["voice"], temperature=0.8)
        sf.write(str(out), audio, tts.sample_rate)
        print(s["id"], t, round(len(audio) / tts.sample_rate, 2), flush=True)
