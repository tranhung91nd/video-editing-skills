"""Transcribe every take with Whisper and rank, per sentence, the takes that read the text most exactly.
Run: <venv with mlx_whisper>/bin/python voice_analyze.py <job>/voice [ids...]"""
import difflib, json, re, sys, unicodedata
from pathlib import Path
import mlx_whisper, soundfile as sf

VOICE = Path(sys.argv[1])
WHISPER = "mlx-community/whisper-large-v3-turbo"


def tokens(text):
    text = unicodedata.normalize("NFC", text.lower())
    return re.sub(r"[^\w\s]", " ", text).split()


def northern(tok):
    # Whisper hears gi/d, r/d, tr/ch, s/x the same in a northern voice; don't count those as misreads.
    for a, b in (("gi", "d"), ("r", "d"), ("tr", "ch"), ("s", "x")):
        if tok.startswith(a):
            return b + tok[len(a):]
    return tok


only = set(sys.argv[2:])
script = json.loads((VOICE / "script.json").read_text(encoding="utf-8"))
out = json.loads((VOICE / "analysis.json").read_text(encoding="utf-8")) if only and (VOICE / "analysis.json").exists() else {}
for s in script["sentences"]:
    if only and s["id"] not in only:
        continue
    expected = [northern(t) for t in tokens(s["tts"])]
    rows = []
    for path in sorted((VOICE / "takes").glob(f"{s['id']}_t*.wav")):
        r = mlx_whisper.transcribe(str(path), path_or_hf_repo=WHISPER, language="vi", word_timestamps=True, verbose=None)
        words = [{"w": w["word"].strip(), "start": round(float(w["start"]), 3), "end": round(float(w["end"]), 3)}
                 for seg in r["segments"] for w in seg.get("words", [])]
        heard = tokens(" ".join(w["w"] for w in words))
        ratio = difflib.SequenceMatcher(a=expected, b=[northern(t) for t in heard], autojunk=False).ratio()
        info = sf.info(str(path))
        rows.append({"file": path.name, "match": round(ratio, 3), "duration": round(info.frames / info.samplerate, 3),
                     "heard": " ".join(heard), "words": words})
    rows.sort(key=lambda x: -x["match"])
    out[s["id"]] = rows
    print(s["id"], "|", s["tts"])
    for x in rows:
        print("   ", x["file"], x["match"], x["duration"], "|", x["heard"])
(VOICE / "analysis.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
