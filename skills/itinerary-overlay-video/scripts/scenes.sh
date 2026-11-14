#!/usr/bin/env bash
# Scene cuts of the source (to snap day cards to cuts) + a 2-second contact sheet.
# Usage: scenes.sh <source.mp4> <plan_dir>
set -euo pipefail
SRC="$1"; OUT="$2"
ffmpeg -v info -i "$SRC" -vf "select='gt(scene,0.3)',showinfo" -an -f null - 2>&1 \
  | grep -o 'pts_time:[0-9.]*' | cut -d: -f2 | awk '{printf "%.2f\n",$1}' > "$OUT/scenes.txt"
ffmpeg -v error -y -i "$SRC" -vf "fps=1/2,scale=160:-1,tile=10x5" -frames:v 1 "$OUT/contact_2s.jpg"
echo "$(wc -l < "$OUT/scenes.txt" | tr -d ' ') cuts -> $OUT/scenes.txt; sheet -> $OUT/contact_2s.jpg (tile n = second 2n)"
