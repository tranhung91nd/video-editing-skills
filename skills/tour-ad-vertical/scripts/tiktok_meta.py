"""Fetch views/likes/duration/size for TikTok candidates, then (optionally) download the best.
Input file: one candidate per line "<cat> <@user/video/id>" (cat = short scene group, e.g. ts, tb, cd).
Run: python3 tiktok_meta.py <job>/source/cands.txt [--download --min-views 4000 --max-dur 320]
Writes <job>/source/meta.txt ("cat id views likes dur WxH path") and raw/<cat>-<id>.mp4."""
import argparse, subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("cands", type=Path)
p.add_argument("--download", action="store_true")
p.add_argument("--min-views", type=int, default=4000)
p.add_argument("--max-dur", type=float, default=320)
p.add_argument("--best", action="store_true", help="highest quality (final render); default h264 for drafts")
a = p.parse_args()
src = a.cands.parent
rows = [l.split()[:2] for l in a.cands.read_text().splitlines() if len(l.split()) >= 2]


def meta(r):
    cat, path = r
    out = subprocess.run(["yt-dlp", "-q", "--skip-download", "--no-warnings", "--print",
                          "%(id)s %(view_count)s %(like_count)s %(duration)s %(width)sx%(height)s",
                          f"https://www.tiktok.com/{path}"], capture_output=True, text=True).stdout.strip()
    return f"{cat} {out} {path}" if out else None


with ThreadPoolExecutor(8) as ex:
    got = [x for x in ex.map(meta, rows) if x]
(src / "meta.txt").write_text("\n".join(got) + "\n")
num = lambda s: int(s) if s.isdigit() else 0
got.sort(key=lambda l: (l.split()[0], -num(l.split()[2])))
for l in got:
    print(l)
if a.download:
    (src / "raw").mkdir(exist_ok=True)
    def dl(l):
        cat, vid, views, likes, dur, wh, path = l.split()
        w, h = (int(x) if x.isdigit() else 0 for x in wh.split("x"))
        if num(views) < a.min_views or float(dur if dur != "NA" else 0) > a.max_dur or h <= w:
            return
        out = src / "raw" / f"{cat}-{vid}.mp4"
        if out.exists() and not a.best:
            return
        fmt = "bv*+ba/b" if a.best else "best[vcodec^=h264]/best"
        subprocess.run(["yt-dlp", "-q", "--no-warnings", "-f", fmt, "--merge-output-format", "mp4", "--force-overwrites",
                        "-o", str(out), f"https://www.tiktok.com/{path}"])
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(dl, got))
    print("downloaded:", len(list((src / "raw").glob("*.mp4"))))
