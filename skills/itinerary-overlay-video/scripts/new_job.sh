#!/usr/bin/env bash
# Usage: new_job.sh <job_dir> <text-free-source.mp4> <logo.png> [language]
# Prepares footage (30 fps CFR), audio, white-text logo, word timestamps,
# a clause draft and a scene list. Then edit <job_dir>/job.json and run build.py.
set -euo pipefail
JOB="$1"; SRC="$2"; LOGO="$3"; LANG_="${4:-en}"
SK="$(cd "$(dirname "$0")/.." && pwd)"; V="$HOME/.itinerary-overlay/venv/bin/python"
mkdir -p "$JOB/hyperframes/assets" "$JOB/plan" "$JOB/out"
cp "$SK/assets/hyperframes/package.json" "$SK/assets/hyperframes/hyperframes.json" "$JOB/hyperframes/"
cp "$SRC" "$JOB/source.mp4"
ffmpeg -v error -y -i "$JOB/source.mp4" -vn -ac 2 -ar 48000 "$JOB/hyperframes/assets/audio.wav"
ffmpeg -v error -y -i "$JOB/source.mp4" -an -vf fps=30 -c:v libx264 -preset fast -crf 18 -g 30 -pix_fmt yuv420p "$JOB/hyperframes/assets/footage.mp4"
"$V" -I "$SK/scripts/logo_white.py" "$LOGO" "$JOB/hyperframes/assets/logo-white.png"
"$V" -I "$SK/scripts/transcribe.py" "$JOB/hyperframes/assets/audio.wav" "$JOB/plan" "$LANG_"
bash "$SK/scripts/scenes.sh" "$JOB/source.mp4" "$JOB/plan"
[ -f "$JOB/job.json" ] || cp "$SK/examples/vietnam-10days/job.json" "$JOB/job.json"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$JOB/source.mp4" | xargs printf "source duration: %s s\n"
echo "Next: edit $JOB/job.json (duration, legs, captions.clauses from plan/clauses_draft.json), then build.py"
