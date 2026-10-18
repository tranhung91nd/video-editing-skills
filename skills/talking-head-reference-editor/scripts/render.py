#!/usr/bin/env python3
"""Validate and render a self-contained talking-head job without modifying the skill."""
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

SKILL = Path(__file__).resolve().parent.parent
FULL = {'card', 'compare', 'proof'}

def jsround(value):
    return math.floor(value + 0.5)

def validate(job):
    plan = json.loads((job / 'edit.json').read_text())
    fps = plan.get('fps', 30)
    if not isinstance(fps, (int, float)) or not math.isfinite(fps) or fps <= 0:
        raise ValueError('fps must be positive and finite')
    cuts = plan.get('cuts', [])
    if not cuts:
        raise ValueError('cuts must contain at least one retained interval')
    acc, last, tl = 0, -1, []
    for i, c in enumerate(cuts):
        start, end = c['start'], c['end']
        if not all(isinstance(x, (float, int)) and math.isfinite(x) for x in (start, end)):
            raise ValueError(f'cut {i}: start/end must be finite seconds')
        if start < 0 or end <= start or start < last:
            raise ValueError(f'cut {i}: require nonnegative, positive, ordered non-overlapping cuts')
        begin = jsround(acc * fps)
        acc += end - start
        duration = jsround(acc * fps) - begin
        if duration < 1:
            raise ValueError(f'cut {i}: interval rounds to zero frames')
        tl.append({**c, 'from': begin, 'dur': duration, 'sourceFrame': jsround(start * fps)})
        last = end
    def fr(t):
        for c in tl:
            if t < c['start']:
                return c['from']
            if t <= c['end']:
                return jsround((sum(q['end']-q['start'] for q in tl[:tl.index(c)]) + t-c['start'])*fps)
        return tl[-1]['from'] + tl[-1]['dur']
    media = (job / 'media').resolve()
    def asset(value):
        if not isinstance(value, str) or not value or '://' in value or Path(value).is_absolute():
            raise ValueError(f'media paths must be local and relative: {value!r}')
        path = (media / value).resolve()
        if not path.is_relative_to(media) or not path.is_file():
            raise ValueError(f'missing or out-of-job media: {value}')
    asset(plan['video'])
    if plan.get('music'):
        asset(plan['music'])
    def media_refs(obj):
        if isinstance(obj, dict):
            if 'src' in obj:
                asset(obj['src'])
            for key, value in obj.items():
                if key == 'media' and isinstance(value, str):
                    asset(value)
                elif isinstance(value, (dict, list)):
                    media_refs(value)
        elif isinstance(obj, list):
            for value in obj:
                media_refs(value)
    intervals = {'captions': [], 'inserts': []}
    for group, types in [('captions', {'hero', 'sub', 'cta', 'brand'}), ('inserts', FULL | {'broll', 'pip'})]:
        for i, item in enumerate(plan.get(group, [])):
            if item.get('type') not in types:
                raise ValueError(f'{group}[{i}]: unsupported type')
            t, end = item['t'], item['end']
            if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in [t, end]):
                raise ValueError(f'{group}[{i}]: finite t/end required')
            if t < 0 or end <= t or end > cuts[-1]['end'] + 1 / fps or fr(end) <= fr(t):
                raise ValueError(f'{group}[{i}]: no positive visible duration inside retained source')
            typ = item['type']
            for key in {'hero':['main'], 'cta':['main'], 'brand':['lines'], 'sub':['line1'], 'stats':['before','after'], 'card':['title'], 'compare':['left','right'], 'proof':['media','stat'], 'pip':['src'], 'broll':['src']}[typ]:
                if not item.get(key):
                    raise ValueError(f'{group}[{i}]: {key} required')
            if typ == 'stats':
                if not all(isinstance(item[x], str) for x in ['before', 'after']):
                    raise ValueError('stats before/after must be text strings')
                if 'changeAt' in item and not (t <= item['changeAt'] < end):
                    raise ValueError('stats changeAt must fall inside its source interval')
            if typ == 'proof':
                proof_refs = item.get('media')
                if not isinstance(proof_refs, list) or not 1 <= len(proof_refs) <= 2:
                    raise ValueError('proof.media must contain one or two media references')
                for ref in proof_refs:
                    asset(ref if isinstance(ref, str) else ref['src'])
            if typ == 'brand' and (not isinstance(item.get('lines'), list) or not all(isinstance(x, str) for x in item['lines'])):
                raise ValueError('brand.lines must be a list of text strings')
            if typ == 'card' and not isinstance(item.get('items', []), list):
                raise ValueError('card.items must be a list')
            intervals[group].append((fr(t), fr(end), typ, i))
            media_refs(item)
    for a in intervals['captions']:
        for b in intervals['inserts']:
            if b[2] in FULL and max(a[0], b[0]) < min(a[1], b[1]):
                print(f'Warning: caption {a[3]} is covered by full-screen insert {b[3]}', file=sys.stderr)
    probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(media / plan['video'])], capture_output=True, text=True, check=True).stdout)
    duration = float(probe['format']['duration'])
    if cuts[-1]['end'] > duration + 1 / fps:
        raise ValueError('retained cut extends beyond source duration')
    videos = [s for s in probe['streams'] if s['codec_type'] == 'video']
    if not videos:
        raise ValueError('input has no video stream')
    rotation = [d.get('rotation', 0) for d in videos[0].get('side_data_list', [])]
    if any(abs(float(x)) % 360 > .1 for x in rotation):
        raise ValueError('normalize video rotation metadata before editing; see references/workflow.md')
    if not any(s['codec_type'] == 'audio' for s in probe['streams']):
        print('Warning: input has no original voice/audio stream', file=sys.stderr)
    return plan, {'fps': fps, 'frames': jsround(acc * fps), 'duration': jsround(acc * fps) / fps, 'cuts': tl}

def main():
    from runtime import render,prepare,run
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job',type=Path);parser.add_argument('output',nargs='?',default='final.mp4')
    parser.add_argument('--check-only',action='store_true');parser.add_argument('--setup-only',action='store_true')
    args,flags=parser.parse_known_args();job=args.job.resolve();plan,report=validate(job)
    (job/'analysis').mkdir(exist_ok=True)
    (job/'analysis/render-timeline.json').write_text(json.dumps(report,indent=2))
    print(f"Preflight OK: {report['frames']} frames, {report['duration']:.3f}s",flush=True)
    if args.check_only:return
    if plan.get('sfx'):
        sfx=job/'media/sfx';sfx.mkdir(exist_ok=True)
        for name,src,af in [('pop.wav','aevalsrc=0.8*sin(2*PI*(700-2500*t)*t)*exp(-30*t):d=0.12',None),('whoosh.wav','anoisesrc=d=0.5:c=pink:a=0.9:seed=42','highpass=f=500,lowpass=f=6000,afade=t=in:d=0.32,afade=t=out:st=0.32:d=0.18')]:
            if not (sfx/name).exists():
                cmd=['ffmpeg','-v','error','-f','lavfi','-i',src]
                if af:cmd+=['-af',af]
                run([*cmd,str(sfx/name)])
    if args.setup_only:print(prepare(SKILL,job)[0]);return
    render(SKILL,job,'edit.json','Main',args.output,flags)
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,RuntimeError) as e:sys.exit(f'Preflight error: {e}')
