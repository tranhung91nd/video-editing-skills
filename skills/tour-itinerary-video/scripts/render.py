#!/usr/bin/env python3
"""Validate narration-driven 16:9 tour edit, then render without opening Studio."""
import argparse,json,math,sys
from pathlib import Path
from runtime import asset,probe,prepare,render
SKILL=Path(__file__).resolve().parent.parent

def validate(job):
    p=json.loads((job/'edit.json').read_text());fps=p.get('fps',30);duration=p['duration']
    if not isinstance(fps,(int,float)) or not math.isfinite(fps) or fps<=0:raise ValueError('Positive finite fps required')
    if not isinstance(duration,(int,float)) or not math.isfinite(duration) or duration<=0:raise ValueError('Positive finite duration required')
    if p['voice'].get('speed',1)!=1:raise ValueError('Use an approved audio file at original speed; retime shot and caption anchors instead')
    voice=probe(asset(job,p['voice']['file']))
    if not any(s['codec_type']=='audio' for s in voice['streams']):raise ValueError('Narration has no audio')
    if float(voice['format']['duration'])>duration+1/fps:raise ValueError('Composition would truncate the narration')
    if p.get('music',{}).get('file'):
        music=probe(asset(job,p['music']['file']))
        if float(music['format']['duration'])<duration-1/fps:raise ValueError('Music is shorter than composition; supply an explicitly looped/prepared bed')
    if p['brand'].get('logo'):asset(job,p['brand']['logo'])
    for f in p['intro']['photos']+[p['cta']['image']]+p.get('postcards',[]):asset(job,f)
    for k in ['kicker','title','accent','routeLabel']:
        if not p['intro'].get(k):raise ValueError('intro.'+k+' is required')
    for k in ['kicker','title','accent','prompt','button']:
        if not p['cta'].get(k):raise ValueError('cta.'+k+' is required')
    if not p.get('days') or not p.get('routePoints'):raise ValueError('days and schematic routePoints are required')
    end=0;count=0
    for i,s in enumerate(p['shots']):
        a,b=s['s'],s['e']
        if not all(isinstance(x,(int,float)) and math.isfinite(x) for x in [a,b]):raise ValueError('Finite shot timing required')
        if a<0 or b<=a or b>duration+1/fps or a<end-1/fps or a>end+1/fps:raise ValueError(f'Shot {i}: require complete, ordered timeline without gaps')
        file=asset(job,s['src'])
        if file.suffix.lower() in ['.mp4','.mov','.m4v','.webm']:
            d=probe(file)
            if not any(x['codec_type']=='video' for x in d['streams']):raise ValueError(f'Shot {i} has no video')
            if float(d['format']['duration'])<b-a+s.get('mediaStart',0)-1/fps:raise ValueError(f'Shot {i} exceeds source duration')
        if s.get('type') not in [None,'intro','route','cta','detail','postcard']:raise ValueError('Unsupported scene type')
        if round((b-a)*fps)<1:raise ValueError('Shot rounds to zero frames')
        end=b;count+=1
    if abs(end-duration)>1/fps:raise ValueError('Shots do not cover the full composition')
    for c in p['captions']:
        if not 0<=c['startMs']<c['endMs']<=duration*1000+1000/fps:raise ValueError('Caption outside composition')
        if not c.get('text'):raise ValueError('Caption text required')
    return p,{'duration':duration,'fps':fps,'frames':math.floor(duration*fps+.5),'shots':count,'voiceDuration':float(voice['format']['duration'])}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('job',type=Path);parser.add_argument('output',nargs='?',default='final.mp4');parser.add_argument('--check-only',action='store_true');parser.add_argument('--setup-only',action='store_true')
    args,flags=parser.parse_known_args();job=args.job.resolve();p,report=validate(job);(job/'analysis').mkdir(exist_ok=True);(job/'analysis/render-timeline.json').write_text(json.dumps(report,indent=2));print('Preflight OK:',json.dumps(report),flush=True)
    if args.check_only:return
    if args.setup_only:print(prepare(SKILL,job)[0]);return
    render(SKILL,job,'edit.json','Tour',args.output,flags)
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,RuntimeError) as e:sys.exit(f'Preflight error: {e}')
