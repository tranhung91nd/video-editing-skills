#!/usr/bin/env bash
# One-time setup: Python venv with mlx-whisper (word timestamps) + Pillow (logo recolour).
set -euo pipefail
V="$HOME/.itinerary-overlay/venv"
python3 -m venv "$V"
"$V/bin/pip" install -q --upgrade pip
"$V/bin/pip" install -q "mlx-whisper==0.4.3" "pillow>=10" "numpy>=1.26"
"$V/bin/python" -c "import mlx_whisper, PIL; print('venv ready:', '$V')"
npx --yes hyperframes@0.8.181 --version >/dev/null && echo "hyperframes CLI ready"
