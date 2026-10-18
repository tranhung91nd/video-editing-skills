#!/usr/bin/env python3
"""Install packaged skills. Explicit --replace always preserves a backup."""
import argparse,shutil
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
NAMES=['talking-head-reference-editor','tour-itinerary-video']
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',choices=['codex','claude','agents'],default='codex');p.add_argument('--destination',type=Path);p.add_argument('--skill',choices=NAMES+['all'],default='all');p.add_argument('--replace',action='store_true');a=p.parse_args()
    dest=a.destination or Path.home()/('.'+a.target)/'skills';dest=dest.expanduser().resolve();names=NAMES if a.skill=='all' else [a.skill]
    for name in names:
        target=dest/name
        if (target.exists() or target.is_symlink()) and not a.replace:p.error(f'{target} exists; use --replace to back it up first')
    dest.mkdir(parents=True,exist_ok=True)
    for name in names:
        target=dest/name
        if target.exists() or target.is_symlink():
            backup=dest.parent/'skill-backups'/datetime.now().strftime('%Y%m%d-%H%M%S-%f')/name;backup.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(target),backup);print('Backup:',backup)
        shutil.copytree(ROOT/'skills'/name,target,ignore=shutil.ignore_patterns('node_modules','__pycache__','*.pyc'));print('Installed:',target)
if __name__=='__main__':main()
