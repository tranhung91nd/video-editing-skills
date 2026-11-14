#!/usr/bin/env bash
# Frames for review before any render. Usage: snapshot.sh <job_dir> 5.5,16.5,22.5,...
set -euo pipefail
JOB="$(cd "$1" && pwd)"; SK="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$SK/scripts/build.py" "$JOB"
cd "$JOB/hyperframes" && npx --yes hyperframes@0.8.181 snapshot --at "$2" --no-end --timeout 20000 . | grep -e contact-sheet -e saved
