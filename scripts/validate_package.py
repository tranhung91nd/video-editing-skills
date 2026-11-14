#!/usr/bin/env python3
"""Dependency-free checks for installable, self-contained video skills."""
import json,re,sys
from pathlib import Path
r=Path(__file__).resolve().parent.parent;errors=[]
for d in sorted((r/'skills').iterdir()):
    if not d.is_dir():continue
    md=(d/'SKILL.md').read_text();m=re.search(r'^name: (.+)$',md,re.M)
    if not md.startswith('---\n') or not m or m[1]!=d.name:errors.append(f'{d.name}: invalid name/frontmatter')
    tpl='assets/hyperframes' if (d/'assets/hyperframes').is_dir() else 'assets/remotion' if (d/'assets/remotion').is_dir() else 'assets/template'
    if tpl=='assets/hyperframes':req=['agents/openai.yaml',tpl+'/package.json',tpl+'/template.tpl',tpl+'/hyperframes.json','scripts/setup.sh','scripts/doctor.sh','scripts/new_job.sh','scripts/build.py','scripts/render.sh']
    else:req=['agents/openai.yaml',tpl+'/package.json',tpl+'/package-lock.json',tpl+'/src/index.tsx']
    if tpl=='assets/remotion':req+=['scripts/setup.sh','scripts/doctor.sh','scripts/new_job.sh']
    elif tpl=='assets/template':req+=['scripts/render.py','scripts/runtime.py','scripts/qa.py','scripts/doctor.py']
    for f in req:
        if not (d/f).is_file():errors.append(f'{d.name}: missing {f}')
    if tpl=='assets/template' and (not (d/'assets/fonts').is_dir() or not list((d/'assets/fonts').glob('*OFL.txt'))):errors.append(f'{d.name}: missing font licenses')
    if (d/tpl/'package-lock.json').exists():
        pkg=json.loads((d/tpl/'package.json').read_text());lock=json.loads((d/tpl/'package-lock.json').read_text())
        if pkg['dependencies']!=lock['packages']['']['dependencies']:errors.append(f'{d.name}: lockfile mismatch')
        if any(v.startswith(('^','~','*')) for v in pkg['dependencies'].values()):errors.append(f'{d.name}: runtime dependencies not pinned')
    for f in d.rglob('*'):
        if not f.is_file() or 'node_modules' in f.parts or '__pycache__' in f.parts:continue
        if f.suffix in ['.py','.sh','.tsx','.md','.json','.yaml','.tpl']:
            s=f.read_text()
            if '/Users/hungcoaching' in s or 'OpenMontage' in s:errors.append(f'{f.relative_to(r)}: machine-specific path')
        if f.suffix=='.md':
            for href in re.findall(r'\]\(([^)]+)\)',f.read_text()):
                if '://' not in href and not href.startswith('#') and not (f.parent/href.split('#')[0]).exists():errors.append(f'{f.relative_to(r)}: broken link {href}')
print('\n'.join(errors) if errors else 'Package validation passed: all skills, lockfiles, fonts, links and paths')
sys.exit(bool(errors))
