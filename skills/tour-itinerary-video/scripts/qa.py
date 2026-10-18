#!/usr/bin/env python3
"""Decode check, duration/audio evidence, and timestamped contact sheets."""
import argparse
import json
from pathlib import Path
import re
import subprocess


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('video', type=Path)
    p.add_argument('out', type=Path)
    p.add_argument('--expected-frames', type=int)
    p.add_argument('--interval', type=float, default=2)
    args = p.parse_args()
    if args.interval <= 0:
        p.error('interval must be positive')
    args.out.mkdir(parents=True, exist_ok=True)
    probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(args.video)], capture_output=True, text=True, check=True).stdout)
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(args.video), '-f', 'null', '-'], check=True)
    report = {'file': str(args.video.resolve()), 'decode': 'passed', 'probe': probe}
    video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    frames = int(video['nb_frames']) if video.get('nb_frames', 'N/A') != 'N/A' else None
    if args.expected_frames is not None and frames is not None and frames != args.expected_frames:
        raise RuntimeError(f'Frame count mismatch: {frames} vs {args.expected_frames}')
    if any(s['codec_type'] == 'audio' for s in probe['streams']):
        audio = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(args.video), '-vn', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True, check=True)
        matches = re.findall(r'\{\s*"input_i".*?\}', audio.stderr, re.S)
        if matches:
            report['loudness'] = json.loads(matches[-1])
    (args.out / 'qa.json').write_text(json.dumps(report, indent=2))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(args.video), '-vf', f'fps=1/{args.interval},scale=216:-2,tile=5x3', '-q:v', '3', str(args.out / 'sheet-%03d.jpg')], check=True)
    (args.out / 'timestamps.txt').write_text('Read sheets left to right, top to bottom.\n' + '\n'.join(f'Sheet {i // 15 + 1:03d}, cell {i % 15 + 1:02d}: approximately {i * args.interval:.2f}s' for i in range(int(float(probe['format']['duration']) / args.interval) + 1)) + '\n')
    print(json.dumps({'decode': 'passed', 'frames': frames, 'size': [video['width'], video['height']], 'duration': probe['format']['duration'], 'qc': str(args.out.resolve()), 'loudness': report.get('loudness')}, indent=2))
    print('Inspect the sheets and listen at cuts: decoder success does not prove text/audio timing or visual quality.')

if __name__ == '__main__':
    main()
