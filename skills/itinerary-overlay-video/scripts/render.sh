#!/usr/bin/env bash
# Usage: render.sh <job_dir> draft|final [name]
#   draft -> out/<name>-draft-720p.mp4 (review rounds)
#   final -> out/<name>-1080p.mp4 (render once, after the user signs off)
set -euo pipefail
JOB="$(cd "$1" && pwd)"; MODE="$2"; NAME="${3:-video}"
SK="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$SK/scripts/build.py" "$JOB"
cd "$JOB/hyperframes"
npx --yes hyperframes@0.8.181 check | tail -3
if [ "$MODE" = final ]; then
  npx --yes hyperframes@0.8.181 render -q delivery -o "$JOB/out/$NAME-1080p.mp4" . > "$JOB/out/render.log" 2>&1
  echo "final: $JOB/out/$NAME-1080p.mp4"
else
  npx --yes hyperframes@0.8.181 render -q draft -o "$JOB/out/.tmp-1080.mp4" . > "$JOB/out/render.log" 2>&1
  ffmpeg -v error -y -i "$JOB/out/.tmp-1080.mp4" -vf scale=720:1280 -c:v libx264 -crf 26 -preset medium -c:a aac -b:a 128k "$JOB/out/$NAME-draft-720p.mp4"
  rm -f "$JOB/out/.tmp-1080.mp4"
  echo "draft: $JOB/out/$NAME-draft-720p.mp4"
fi
