"""Lay the chosen takes end to end and write narration.wav + timeline.json (sentence and word
times on the final clock, plus the subtitle text from script.json "display").
Takes come from pick.json ({"s01": 2, ...}) when present, else the best Whisper match.
Run: <venv with numpy + soundfile>/bin/python voice_assemble.py <job>/voice [--tempo 1.15] [--pause-scale 0.75] [--lead 0.6] [--tail 3.5]
--tempo > 1 speeds the voice up (ffmpeg atempo) when the read is longer than the target length."""
import argparse, json, subprocess, tempfile
from pathlib import Path
import numpy as np, soundfile as sf

p = argparse.ArgumentParser()
p.add_argument("voice", type=Path)
p.add_argument("--tempo", type=float, default=1.0)
p.add_argument("--pause-scale", type=float, default=1.0)
p.add_argument("--lead", type=float, default=0.6, help="silence before the first word")
p.add_argument("--tail", type=float, default=3.5, help="silence after the last word (end card)")
a = p.parse_args()
VOICE = a.voice


def load(path):
    if a.tempo == 1.0:
        return sf.read(str(path))
    tmp = tempfile.mktemp(suffix=".wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-af", f"atempo={a.tempo}", tmp], check=True)
    return sf.read(tmp)


script = json.loads((VOICE / "script.json").read_text(encoding="utf-8"))
analysis = json.loads((VOICE / "analysis.json").read_text(encoding="utf-8"))
pick_file = VOICE / "pick.json"
pick = json.loads(pick_file.read_text()) if pick_file.exists() else {}
sents = script["sentences"]
parts, timeline, t, sr = [], [], a.lead, None
for i, s in enumerate(sents):
    name = f"{s['id']}_t{pick[s['id']]}.wav" if s["id"] in pick else analysis[s["id"]][0]["file"]
    audio, sr = load(VOICE / "takes" / name)
    loud = np.where(np.abs(audio) > 10 ** (-42 / 20) * np.abs(audio).max())[0]
    lo, hi = max(0, loud[0] - int(0.02 * sr)), min(len(audio), loud[-1] + int(0.06 * sr))
    clip = audio[lo:hi].copy()
    fade = int(0.01 * sr)
    clip[:fade] *= np.linspace(0, 1, fade); clip[-fade:] *= np.linspace(1, 0, fade)
    words = next(x for x in analysis[s["id"]] if x["file"] == name)["words"]
    off = t - lo / sr
    timeline.append({"id": s["id"], "take": name, "display": s.get("display", ""), "start": round(t, 3), "end": round(t + len(clip) / sr, 3),
                     "words": [{"w": w["w"], "start": round(w["start"] / a.tempo + off, 3), "end": round(w["end"] / a.tempo + off, 3)} for w in words]})
    pause = a.tail if i == len(sents) - 1 else s.get("pause", 0.3) * a.pause_scale
    parts += [clip, np.zeros(int(pause * sr))]
    t += len(clip) / sr + pause
out = np.concatenate([np.zeros(int(a.lead * sr))] + parts)
sf.write(str(VOICE / "narration.wav"), out, sr)
(VOICE / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding="utf-8")
for x in timeline:
    print(x["id"], x["take"], x["start"], x["end"], x["display"])
print("total", round(len(out) / sr, 3), "sr", sr)
