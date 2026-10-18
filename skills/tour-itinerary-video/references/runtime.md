# Runtime và cài đặt

Đã kiểm trên macOS Apple Silicon. Cần Python 3.10+, Node.js 20+, npm, ffmpeg/ffprobe và Chrome/Chromium. Các template dùng Remotion 4.0.534, React 19.2.3 và package-lock.json để `npm ci`. Không cần ứng dụng Remotion hay HyperFrames chạy ngầm.

Lệnh `doctor.py` báo công cụ và font. render.py --setup-only tạo render-project riêng trong job, chạy npm ci nếu thiếu runtime đúng phiên bản, chép font vào media/fonts. Nếu không tìm thấy Chrome, đặt REMOTION_BROWSER_EXECUTABLE hoặc chạy lệnh `node node_modules/@remotion/cli/remotion-cli.js browser ensure` từ render-project để cài Chromium headless. Không tự đổi trình duyệt/biến môi trường toàn máy.

Có thể tái dùng runtime đúng phiên bản bằng REMOTION_NODE_MODULES=/path/to/node_modules; kiểm phiên bản trước khi dùng. Mặc định không phụ thuộc runtime của tác giả, không liên kết cả node_modules để tránh làm hỏng cache dự án khác. Mặc định concurrency=1. Có thể chuyển `--concurrency=2` khi phù hợp. Renderer chỉ khởi động tác vụ headless hữu hạn, có timeout và dọn nhóm tiến trình do nó tạo khi kết thúc.

ASR là tùy chọn. Nếu đã có words.json/transcript thì không tải model:

```bash
python3 -m venv .venv-asr
.venv-asr/bin/pip install mlx-whisper  # macOS Apple Silicon
.venv-asr/bin/python scripts/transcribe.py job/media/raw.mp4 job/analysis --backend mlx
```

Hoặc cài faster-whisper trong môi trường riêng rồi dùng --backend faster-whisper --model small. Model được tải khi gọi ASR lần đầu, không nằm trong skill. Đổi tên riêng sai và kiểm lại cuts gợi ý trước khi dùng. Không gọi ASR trên file chứa dữ liệu nhạy cảm qua dịch vụ ngoài khi chưa được yêu cầu; backend này chạy cục bộ.

Không hứa đã thử trên Windows/Linux: logic Python/Node không dùng đường dẫn home của tác giả, nhưng cài Chrome/FFmpeg và hỗ trợ dựng phải kiểm trên máy đích. Giấy phép Remotion và các dependency thuộc nhà cung cấp; repository này không cấp lại quyền dùng thư viện, ảnh, nhạc hoặc giọng của bên khác.
