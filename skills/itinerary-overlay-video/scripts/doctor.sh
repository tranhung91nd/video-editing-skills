#!/usr/bin/env bash
# Check every tool the skill needs. Exit 1 if anything is missing.
V="$HOME/.itinerary-overlay/venv/bin/python"; ok=1
for t in ffmpeg ffprobe node npx python3; do command -v "$t" >/dev/null || { echo "MISSING: $t"; ok=0; }; done
[ "$(uname -m)" = arm64 ] || echo "WARN: mlx-whisper needs Apple Silicon"
if [ -x "$V" ]; then "$V" -c "import mlx_whisper, PIL" 2>/dev/null || { echo "MISSING: python modules (run setup.sh)"; ok=0; }
else echo "MISSING: $V (run setup.sh)"; ok=0; fi
[ $ok = 1 ] && echo "doctor: all good" || exit 1
