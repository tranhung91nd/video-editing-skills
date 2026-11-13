#!/usr/bin/env python3
"""Quick OCR pre-screen of candidate source clips (macOS Vision).

Samples 2 frames/second, reports which clips/time ranges show readable text, and
writes an 8-frame strip per clip for a fast visual pass. This only removes obvious
rejects early; a clip that passes still needs check_plan_text.py and a look at
native resolution before it goes into a plan.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent


def ocr_binary(cache):
    exe = cache / 'ocr_frames'
    if not exe.exists():
        subprocess.run(['swiftc', '-O', str(HERE / 'ocr_frames.swift'), '-o', str(exe)],
                       check=True, capture_output=True)
    return exe


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('videos', nargs='+', type=Path)
    p.add_argument('--out', required=True, type=Path, help='result folder (report.json, strips)')
    a = p.parse_args()
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    exe = ocr_binary(out)
    report = out / 'report.json'
    res = json.loads(report.read_text(encoding='utf-8')) if report.exists() else {}
    for v in sorted(a.videos):
        name = v.stem
        if name in res:
            continue
        d = out / name
        if d.exists():
            shutil.rmtree(d)
        d.mkdir()
        meta = json.loads(subprocess.check_output(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
             'stream=width,height,r_frame_rate,bit_rate:format=duration', '-of', 'json', str(v)]))
        st = meta['streams'][0]
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(v), '-vf', 'fps=2,scale=720:-2',
                        '-q:v', '4', str(d / 'f%04d.jpg')], check=True)
        frames = []
        for line in subprocess.check_output([str(exe), str(d)]).decode().strip().split('\n'):
            f, _, text = line.partition('\t')
            frames.append((round((int(f[1:5]) - 1) * 0.5, 1), text))
        texty = [(t, x) for t, x in frames if x.strip()]
        clean, start = [], None
        for t, x in frames:
            if not x.strip():
                start = t if start is None else start
            else:
                if start is not None and t - start >= 1.5:
                    clean.append([start, t])
                start = None
        if start is not None and frames[-1][0] + 0.5 - start >= 1.5:
            clean.append([start, round(frames[-1][0] + 0.5, 1)])
        res[name] = {'file': str(v), 'dur': round(float(meta['format']['duration']), 1),
                     'size': f"{st['width']}x{st['height']}", 'fps': st['r_frame_rate'],
                     'kbps': round(int(st.get('bit_rate', 0)) / 1000),
                     'frames': len(frames), 'texty': len(texty), 'clean_ranges': clean,
                     'sample_text': [x[:90] for _, x in texty[:3]]}
        n = len(frames)
        picks = sorted({int(i * (n - 1) / 7) for i in range(8)})
        sel = '+'.join(f'eq(n\\,{i})' for i in picks)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '2', '-i', str(d / 'f%04d.jpg'),
                        '-vf', f"select='{sel}',scale=180:320:force_original_aspect_ratio=decrease,"
                               'pad=180:320:(ow-iw)/2:(oh-ih)/2,tile=8x1',
                        '-frames:v', '1', str(out / f'{name}.strip.jpg')])
        report.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
    for name in sorted(res):
        r = res[name]
        print(f"{name} | {r['dur']}s {r['size']} {r.get('kbps', '?')}kbps | text {r['texty']}/{r['frames']} "
              f"| clean {r['clean_ranges']} | {r['sample_text'][:1]}")


if __name__ == '__main__':
    main()
