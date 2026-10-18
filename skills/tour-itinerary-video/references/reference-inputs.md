# Ví dụ Cửu Trại Câu V6

Plan examples/cuu-trai-cau-v6.json được trích đúng JourneyThucDoan.tsx và data-thuc-doan.json. 77 giây × 30 fps = 2310 frame. Brand, lịch trình và giọng Thục Đoan thuộc ví dụ, cần đổi khi dựng tour khác.

Cần tự cung cấp toàn bộ file được gọi trong plan dưới media/, gồm narration revision6, music revision6, logo revision5, ảnh và clip. Những file này không được đưa lên GitHub vì không phải mã skill/tài nguyên phân phối chung. sources.json nên ghi file, source URL, rightsStatus, approvedVoice và notes. Giọng TTS được dùng ở tốc độ gốc 1.0.

V6 là Remotion; không nhầm với các bản HyperFrames 66 giây làm sau đó. Video gốc không thay đổi khi cài skill.

Có thể kiểm và gom file đầu vào từ nguồn riêng bằng `python3 scripts/stage_example.py /path/to/source-media /path/to/new-job --check-only`. Bỏ --check-only để chép đúng các file cần, cùng edit.json vào job mới; không ghi đè job đang có.
