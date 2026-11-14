"""Word timestamps + a clause draft. Usage: transcribe.py audio.wav <plan_dir> [lang]
Writes plan/words.json and plan/clauses_draft.json ([[clause, true], ...], split at , . ? !)."""
import json
import sys
from pathlib import Path
import mlx_whisper

audio, out = sys.argv[1], Path(sys.argv[2])
lang = sys.argv[3] if len(sys.argv) > 3 else "en"
res = mlx_whisper.transcribe(audio, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language=lang,
                             word_timestamps=True, condition_on_previous_text=False)
words = [{"w": x["word"].strip(), "s": round(x["start"], 2), "e": round(x["end"], 2)} for s in res["segments"] for x in s["words"]]
(out / "words.json").write_text(json.dumps(words, ensure_ascii=False, indent=0))
clauses, cur = [], []
for w in words:
    if w["w"].startswith("-") and cur:
        cur[-1] += w["w"]
        continue
    cur.append(w["w"])
    if w["w"][-1] in ",.?!" and len(" ".join(cur)) >= 14:
        clauses.append([" ".join(cur), True])
        cur = []
if cur:
    clauses.append([" ".join(cur), True])
(out / "clauses_draft.json").write_text(json.dumps(clauses, ensure_ascii=False, indent=1))
print(f"{len(words)} words, {len(clauses)} clauses -> {out}")
for c, _ in clauses:
    print("  ", c)
