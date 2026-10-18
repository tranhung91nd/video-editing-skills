"""Job-local Remotion runtime. No preview server, no machine-specific dependency path."""
from pathlib import Path
import hashlib,json,os,shutil,signal,subprocess,sys

def run(cmd,cwd=None,timeout=1800):
    p=subprocess.Popen([str(c) for c in cmd],cwd=cwd,start_new_session=(os.name=="posix"))
    try:
        code=p.wait(timeout=timeout)
        if code:raise RuntimeError(f"Command exited {code}: {cmd[0]}")
    finally:
        if os.name=="posix":
            try:os.killpg(p.pid,signal.SIGTERM)
            except ProcessLookupError:pass
        elif p.poll() is None:
            subprocess.run(["taskkill","/PID",str(p.pid),"/T","/F"],capture_output=True)

def probe(file):
    return json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(file)],text=True))

def asset(job,value):
    media=(job/"media").resolve()
    if not isinstance(value,str) or not value or "://" in value or Path(value).is_absolute():raise ValueError(f"Expected local relative media path: {value!r}")
    file=(media/value).resolve()
    if not file.is_relative_to(media) or not file.is_file():raise ValueError(f"Missing or outside media/: {value}")
    return file

def browser():
    if os.environ.get("REMOTION_BROWSER_EXECUTABLE"):return os.environ["REMOTION_BROWSER_EXECUTABLE"]
    options=["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome","/Applications/Chromium.app/Contents/MacOS/Chromium"]
    for f in options:
        if Path(f).is_file():return f
    for name in ["google-chrome","chromium","chromium-browser"]:
        if shutil.which(name):return shutil.which(name)
    return None

def prepare(skill,job):
    for command in ["node","npm","ffmpeg","ffprobe"]:
        if not shutil.which(command):raise RuntimeError(f"Missing executable: {command}")
    major=int(subprocess.check_output(["node","--version"],text=True).lstrip("v").split(".")[0])
    if major<20:raise RuntimeError("Node.js 20+ is required")
    project=job/"render-project"
    shutil.copytree(skill/"assets/template",project,dirs_exist_ok=True,ignore=shutil.ignore_patterns("node_modules",".cache"))
    expected=json.loads((project/"package.json").read_text())["dependencies"]
    modules=project/"node_modules"
    external=os.environ.get("REMOTION_NODE_MODULES")
    if external:
        source=Path(external).expanduser().resolve()
        for package,version in expected.items():
            f=source/package/"package.json"
            if not f.exists() or json.loads(f.read_text())["version"]!=version:raise RuntimeError(f"REMOTION_NODE_MODULES requires {package}@{version}")
        modules.mkdir(exist_ok=True)
        for item in source.iterdir():
            if item.name.startswith("."):continue
            target=modules/item.name
            if not target.exists():target.symlink_to(item,target_is_directory=item.is_dir())
    else:
        valid=True
        for package,version in expected.items():
            f=modules/package/"package.json"
            if not f.exists() or json.loads(f.read_text())["version"]!=version:valid=False;break
        if not valid:run(["npm","ci","--no-audit","--no-fund"],cwd=project,timeout=600)
    fonts=job/"media/fonts";fonts.mkdir(parents=True,exist_ok=True)
    for f in (skill/"assets/fonts").glob("*.ttf"):shutil.copy2(f,fonts/f.name)
    return project,modules

def render(skill,job,planfile,composition,output,flags):
    project,modules=prepare(skill,job)
    target=Path(output)
    if not target.is_absolute():target=job/"out"/target
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.suffix.lower()!=".mp4":raise ValueError("Output must be an MP4")
    def supplied(name):return any(x==name or x.startswith(name+"=") for x in flags)
    defaults=[]
    for key,value in [("--concurrency","1"),("--bundle-cache","false"),("--browser-executable",browser()),("--codec","h264"),("--crf","18")]:
        if value is not None and not supplied(key):defaults.append(key+"="+value)
    run(["node",modules/"@remotion/cli/remotion-cli.js","render","src/index.tsx",composition,target.resolve(),"--props="+str(job/planfile),"--public-dir="+str(job/"media"),*defaults,*flags],cwd=project)
    print("Rendered:",target.resolve())
    print("Next: run scripts/qa.py and inspect its contact sheets. No Studio was opened.")
