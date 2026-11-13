"""One frame per second of a render, 27 per sheet, to look for captions/stickers that OCR missed
(handwritten/decorative fonts, Thai, two-line Chinese titles) and for blurry or flared shots.
Run: <python with Pillow> qc_sheet.py <video.mp4> <out_dir>"""
import glob, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw

video, out = sys.argv[1], Path(sys.argv[2]); fr = out / "frames"; fr.mkdir(parents=True, exist_ok=True)
for f in fr.glob("*.jpg"):
    f.unlink()
subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf", "fps=1,scale=216:384", str(fr / "%03d.jpg")], check=True)
f = sorted(glob.glob(str(fr / "*.jpg")))
for pg in range(0, len(f), 27):
    ch = f[pg:pg + 27]; im = Image.new("RGB", (216 * 9, 394 * 3)); d = ImageDraw.Draw(im)
    for i, x in enumerate(ch):
        im.paste(Image.open(x), ((i % 9) * 216, (i // 9) * 394 + 10)); d.text(((i % 9) * 216 + 2, (i // 9) * 394), str(pg + i), fill="yellow")
    im.save(out / f"qc_{pg // 27}.jpg")
    print(out / f"qc_{pg // 27}.jpg")
