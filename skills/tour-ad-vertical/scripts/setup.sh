#!/bin/bash
# One-time setup on a Mac with Apple Silicon (M1/M2/M3/M4). Re-running is safe.
# Creates ~/.tour-ad-video/tts (VieNeu voice + Pillow + librosa) and ~/.tour-ad-video/asr (mlx-whisper).
set -e
HOME_DIR="$HOME/.tour-ad-video"
command -v brew >/dev/null || { echo "Cài Homebrew trước: https://brew.sh"; exit 1; }
brew list ffmpeg >/dev/null 2>&1 || brew install ffmpeg
brew list node >/dev/null 2>&1 || brew install node
brew list yt-dlp >/dev/null 2>&1 || brew install yt-dlp
brew list python@3.10 >/dev/null 2>&1 || brew install python@3.10
PY=$(brew --prefix python@3.10)/bin/python3.10
xcode-select -p >/dev/null 2>&1 || xcode-select --install   # swiftc for the OCR helper
mkdir -p "$HOME_DIR"
[ -x "$HOME_DIR/tts/bin/python" ] || $PY -m venv "$HOME_DIR/tts"
"$HOME_DIR/tts/bin/pip" install -q --upgrade pip
"$HOME_DIR/tts/bin/pip" install -q "vieneu==3.8.3" soundfile pillow librosa
[ -x "$HOME_DIR/asr/bin/python" ] || $PY -m venv "$HOME_DIR/asr"
"$HOME_DIR/asr/bin/pip" install -q --upgrade pip
"$HOME_DIR/asr/bin/pip" install -q "mlx-whisper==0.4.3" soundfile numpy
# Shared Remotion node_modules, linked into every job (npm install once, not per video).
mkdir -p "$HOME_DIR/remotion"
cp "$(dirname "$0")/../assets/remotion/package.json" "$(dirname "$0")/../assets/remotion/package-lock.json" "$HOME_DIR/remotion/"
(cd "$HOME_DIR/remotion" && npm ci --silent)
echo "Xong. Kiểm tra: bash $(dirname "$0")/doctor.sh"
