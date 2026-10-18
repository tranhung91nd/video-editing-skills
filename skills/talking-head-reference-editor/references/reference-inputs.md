# Ví dụ Hanta AI

examples/hanta-reference.json là edit.json của dự án đã tạo video Hanta ai.mp4: raw.mp4, hai clip sự kiện và music.mp3 là input riêng, không có trong gói. Tệp này dùng để so cấu trúc/timing, không thể render khi thiếu input.

Đầu vào cần đặt trong media/: raw.mp4; assets/hhdl-hoinghi.mp4; assets/ceo-success-recap.mp4; assets/music.mp3. SFX có thể tự tạo. Đầu ra dự kiến 1422 frame (47.4 giây video) 1080×1920. Container video được nộp dài 47.445 giây do padding audio.

Đã xác minh SHA-256 của video nộp khớp out/final.mp4 trong dự án gốc. Xem docs/AUDIT.md ở gốc repository để biết nguồn và phạm vi kiểm.

Có thể kiểm và gom file đầu vào từ nguồn riêng bằng `python3 scripts/stage_example.py /path/to/source-media /path/to/new-job --check-only`. Bỏ --check-only để chép đúng các file cần, cùng edit.json vào job mới; không ghi đè job đang có.
