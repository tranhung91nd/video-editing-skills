#!/usr/bin/env python3
"""Behavioral preflight tests against local synthetic fixture inputs."""
from pathlib import Path
import importlib.util,json,shutil,sys,tempfile
ROOT=Path(__file__).resolve().parent.parent
fixtures=Path(sys.argv[1]).resolve()
def load(name):
    path=ROOT/'skills'/name/'scripts/render.py';sys.path.insert(0,str(path.parent));spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);sys.path.pop(0);return module
th=load('talking-head-reference-editor');tour=load('tour-itinerary-video');passed=[]
def case(label,module,fixture,mutate=None,reject=False):
    with tempfile.TemporaryDirectory(prefix='video-skill-validation-') as temp:
        job=Path(temp);(job/'media').symlink_to(fixtures/fixture/'media',target_is_directory=True);p=json.loads((fixtures/fixture/'edit.json').read_text())
        if mutate:mutate(p)
        (job/'edit.json').write_text(json.dumps(p))
        try:_,report=module.validate(job)
        except (ValueError,KeyError):
            if not reject:raise
        else:
            if reject:raise AssertionError(label+': invalid plan was accepted')
            if label=='Hanta brand and all insert types':assert report['frames']==288
            if label=='Tour valid timeline':assert report['frames']==300
        passed.append(label)
case('Hanta brand and all insert types',th,'hanta-smoke')
case('Hanta rejects missing source',th,'hanta-smoke',lambda p:p.update(video='missing.mp4'),True)
case('Hanta rejects overlapping cuts',th,'hanta-smoke',lambda p:p['cuts'][1].update(start=3),True)
case('Hanta rejects source overrun',th,'hanta-smoke',lambda p:p['cuts'][-1].update(end=50),True)
case('Hanta rejects outside media',th,'hanta-smoke',lambda p:p.update(video='../edit.json'),True)
case('Hanta rejects invalid proof type',th,'hanta-smoke',lambda p:p['inserts'][-1].update(media='photo-2.jpg'),True)
case('Tour valid timeline',tour,'tour-smoke')
case('Tour rejects narration truncation',tour,'tour-smoke',lambda p:p.update(duration=9),True)
case('Tour rejects arbitrary voice speed',tour,'tour-smoke',lambda p:p['voice'].update(speed=1.2),True)
case('Tour rejects timeline gap',tour,'tour-smoke',lambda p:p['shots'][1].update(s=2.5),True)
case('Tour rejects missing media',tour,'tour-smoke',lambda p:p['shots'][0].update(src='missing.jpg'),True)
case('Tour rejects footage overrun',tour,'tour-smoke',lambda p:p['shots'][2].update(mediaStart=100),True)
print(json.dumps({'passed':len(passed),'tests':passed},ensure_ascii=False,indent=2))
