#!/usr/bin/env python3
"""Stage the reference plan with separately supplied, local source media."""
import argparse,json,shutil
from pathlib import Path
SKILL=Path(__file__).resolve().parent.parent
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source_media',type=Path);p.add_argument('job',type=Path);p.add_argument('--check-only',action='store_true');a=p.parse_args()
    req=json.loads((SKILL/'examples/required-inputs.json').read_text());root=a.source_media.resolve();files=[]
    for name in req['files']:
        f=(root/name).resolve()
        if not f.is_relative_to(root) or not f.is_file():p.error('Missing required input: '+name)
        files.append((name,f))
    print('Reference inputs present:',len(files))
    if a.check_only:return
    job=a.job.resolve()
    if job.exists() and any(job.iterdir()):p.error('Use a new or empty job directory')
    (job/'media').mkdir(parents=True,exist_ok=True)
    for name,f in files:
        out=job/'media'/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,out)
    shutil.copy2(SKILL/'examples'/req['example'],job/'edit.json')
    (job/'media/sources.json').write_text(json.dumps([{'file':name,'rightsStatus':'user-supplied, not independently verified'} for name,_ in files],ensure_ascii=False,indent=2))
    print('Staged job:',job)
if __name__=='__main__':main()
