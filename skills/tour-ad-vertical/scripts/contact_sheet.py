"""Contact sheets of the text-free ranges of every screened clip, one sheet per scene group.
Run: <python with Pillow> contact_sheet.py <job>   (needs <job>/work/screen/report.json from screen_text.py)
Writes <job>/work/sheets/<cat>_<n>.jpg; each row = one clip, numbers = second in the source."""
import json, os, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw

job = Path(sys.argv[1])
r = json.loads((job / "work/screen/report.json").read_text())
out = job / "work/sheets"; out.mkdir(parents=True, exist_ok=True)
cats = {}
for k, x in sorted(r.items()):
    cl = [(a, b) for a, b in x["clean_ranges"] if b - a >= 2]
    if sum(b - a for a, b in cl) >= 4:
        cats.setdefault(k.split("-")[0], []).append((k, cl))
tmp = Path(tempfile.mkdtemp()) / "f.jpg"
for c, items in cats.items():
    for page in range(0, len(items), 6):
        rows = items[page:page + 6]
        sheet = Image.new("RGB", (10 * 144, len(rows) * 280), "black"); d = ImageDraw.Draw(sheet)
        for ri, (k, cl) in enumerate(rows):
            ts = []
            for a, b in cl:
                t = a + 0.5
                while t < b - 0.3:
                    ts.append(round(t, 1)); t += 2.5
            ts = ts[::max(1, len(ts) // 10)][:10]
            d.text((4, ri * 280 + 4), k, fill="yellow")
            for i, t in enumerate(ts):
                tmp.unlink(missing_ok=True)
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(job / f"source/raw/{k}.mp4"),
                                "-frames:v", "1", "-vf", "scale=144:256", str(tmp)])
                if tmp.exists():
                    sheet.paste(Image.open(tmp), (i * 144, ri * 280 + 24)); d.text((i * 144 + 3, ri * 280 + 26), str(t), fill="white")
        sheet.save(out / f"{c}_{page // 6}.jpg", quality=80)
print(sorted(os.listdir(out)))
