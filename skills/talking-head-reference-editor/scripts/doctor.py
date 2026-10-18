import json,shutil,sys
from pathlib import Path
from runtime import browser
s=Path(__file__).resolve().parent.parent
print(json.dumps({'python':sys.version.split()[0],'commands':{c:shutil.which(c) for c in ['node','npm','ffmpeg','ffprobe']},'existing_browser':browser(),'lockfile':(s/'assets/template/package-lock.json').is_file(),'fonts':[p.name for p in (s/'assets/fonts').glob('*.ttf')]},indent=2))
