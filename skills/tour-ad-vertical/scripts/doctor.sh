#!/bin/bash
# Check that every tool the skill uses is installed.
H="$HOME/.tour-ad-video"; ok=1
chk(){ if eval "$2" >/dev/null 2>&1; then echo "OK   $1"; else echo "LỖI $1"; ok=0; fi; }
chk "ffmpeg" "ffmpeg -version"
chk "node" "node -v"
chk "yt-dlp" "yt-dlp --version"
chk "swiftc (OCR)" "swiftc --version"
chk "VieNeu (giọng)" "$H/tts/bin/python -c 'import vieneu'"
chk "Pillow/librosa" "$H/tts/bin/python -c 'import PIL, librosa'"
chk "mlx-whisper" "$H/asr/bin/python -c 'import mlx_whisper'"
chk "Remotion" "test -d $H/remotion/node_modules/remotion"
[ $ok = 1 ] && echo "Đủ công cụ." || echo "Chạy lại setup.sh cho các mục LỖI."
