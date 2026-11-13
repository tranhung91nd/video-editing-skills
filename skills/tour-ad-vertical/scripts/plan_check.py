"""Check the shot list and write the Remotion inputs.
<job>/shots.json: {"total": 92.4, "shots": [[at, "clip-name", in_point], ...], "tags": [...], "cards": {...}, "brand": {...}}
  at = second on the final timeline, clip-name = file in source/raw without .mp4, in_point = second in the clip.
Each shot runs until the next shot's `at`. The check fails a shot that leaves the clip's clean_range
(caption/sticker area) or crosses a cut inside the source clip (montage clips cut about every second).
Writes <job>/remotion/src/plan.json, dims.ts and hard-links the clips into remotion/public/v (Remotion
does not follow symlinks). Also writes work/plan_sheet.jpg (middle frame of every shot) when Pillow exists.
Run: <python with Pillow> plan_check.py <job>"""
import json, os, subprocess, sys
from pathlib import Path

job = Path(sys.argv[1])
cfg = json.loads((job / "shots.json").read_text(encoding="utf-8"))
r = json.loads((job / "work/screen/report.json").read_text())
S, total = cfg["shots"], cfg["total"]
shots, dims, bad = [], {}, 0
for i, (at, v, t) in enumerate(S):
    end = S[i + 1][0] if i + 1 < len(S) else total
    d = end - at + 0.25
    ok = any(a <= t and t + d <= b for a, b in r[v]["clean_ranges"])
    err = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-t", str(d), "-i", str(job / f"source/raw/{v}.mp4"),
                          "-vf", "select='gt(scene,0.3)',metadata=print", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    cuts = [round(float(l.split("pts_time:")[1]), 2) for l in err.splitlines() if "pts_time" in l]
    if not ok or cuts:
        bad += 1
        near = [x for x in r[v]["clean_ranges"] if x[1] > t - 3 and x[0] < t + d + 3]
        print(f"FIX {at:6} {v} in={t} len={d:.2f} clean={ok} cuts_inside={cuts} clean_ranges_near={near}")
    shots.append({"v": v, "t": t, "at": at})
    w, h = r[v]["size"].split("x"); dims[v] = [int(w), int(h)]
src = job / "remotion/src"; pub = job / "remotion/public/v"; pub.mkdir(parents=True, exist_ok=True)
plan = {k: v for k, v in cfg.items() if k != "shots"}; plan["shots"] = shots
(src / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
(src / "dims.ts").write_text("export const DIMS: Record<string, [number, number]> = " + json.dumps(dims) + ";\n")
for v in dims:
    dst = pub / f"{v}.mp4"
    if dst.exists():
        dst.unlink()
    os.link(job / f"source/raw/{v}.mp4", dst)
print(f"{len(shots)} shots, {bad} to fix")
try:
    from PIL import Image, ImageDraw
    cols = 14; im = Image.new("RGB", (cols * 108, ((len(shots) - 1) // cols + 1) * 210), "black"); dr = ImageDraw.Draw(im)
    tmp = job / "work/_f.jpg"
    for i, s in enumerate(shots):
        nxt = shots[i + 1]["at"] if i + 1 < len(shots) else total
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s["t"] + (nxt - s["at"]) / 2), "-i", str(job / f"source/raw/{s['v']}.mp4"),
                        "-frames:v", "1", "-vf", "scale=108:192", str(tmp)])
        x, y = (i % cols) * 108, (i // cols) * 210
        im.paste(Image.open(tmp), (x, y + 18)); dr.text((x + 2, y + 2), str(s["at"]), fill="yellow")
    im.save(job / "work/plan_sheet.jpg"); tmp.unlink()
    print("sheet:", job / "work/plan_sheet.jpg")
except ImportError:
    pass
