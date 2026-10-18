# Bộ skill dựng video — Hanta AI & Tour theo lịch trình

Hai workflow Remotion riêng biệt, được đối chiếu bằng hash với video gốc và đóng gói để cài vào Codex/Claude. Không cần HyperFrames hoặc Remotion Studio chạy ngầm.

| Video tham chiếu | Skill trong bộ | Kiểu dựng |
|---|---|---|
| Hanta ai.mp4 · 47,4 giây · 1080×1920 | talking-head-reference-editor | Người nói, chữ vàng Anton/Montserrat, thẻ, pip, CTA |
| Cửu Trại Câu V6 · 77 giây · 1920×1080 | tour-itinerary-video | Lời thuyết minh theo ngày, tuyến hành trình, nhãn cảnh, phụ đề, logo, CTA |

Skill Hanta bắt nguồn từ `talking-head-editor` của Claude; bản này thống nhất template đúng với Hanta và bỏ template League Gothic cũ. Tour V6 trước đây là dự án Remotion viết riêng, nay đã được tham số hóa thành skill mới. Xem [kiểm toán và kiểm thử](docs/AUDIT.md).

## Cài vào Codex

Repo công khai: bất kỳ ai có link đều có thể xem và tải, không cần đăng nhập GitHub.

**[Tải cả hai skill và bộ cài ZIP](https://github.com/tranhung91nd/video-editing-skills/releases/download/v1.0.1/video-editing-skills-v1.0.1.zip)** · [Tất cả bản tải](https://github.com/tranhung91nd/video-editing-skills/releases)

Cách dùng ZIP: giải nén, mở Terminal tại thư mục vừa giải nén (nơi có README.md), rồi chạy:

```bash
python3 scripts/validate_package.py
python3 scripts/install.py --target codex
```

Hoặc nếu đã có Git:

```bash
git clone https://github.com/tranhung91nd/video-editing-skills.git
cd video-editing-skills
python3 scripts/validate_package.py
python3 scripts/install.py --target codex
```

Đã có bản cũ thì thêm `--replace`; script sao lưu trước khi thay. Dùng `--target claude` hoặc `--target agents` để cài vào môi trường tương ứng. Có thể chọn `--skill tour-itinerary-video` thay vì cài cả hai. Nếu skill chưa xuất hiện trong danh sách, tải lại phiên làm việc.

```text
Dùng $talking-head-reference-editor dựng video nói của tôi theo mẫu Hanta AI.
Dùng $tour-itinerary-video dựng video ngang giới thiệu tour theo lịch trình này.
```

Cập nhật từ repository rồi cài lại:

```bash
git pull --ff-only
python3 scripts/install.py --target codex --replace
```

## Runtime

Python 3.10+, Node.js 20+, npm, FFmpeg/ffprobe và Chrome/Chromium. Chạy `python3 <skill>/scripts/doctor.py`. Đọc references/runtime.md trong skill. Font OFL đã kèm; dependency Node có lockfile. Mặc định render một luồng, không mở file hay tab xem trước. Các tiến trình con do renderer tạo được đóng khi tác vụ kết thúc.

Ví dụ edit.json nằm trong examples của mỗi skill. Các file video/nhạc/giọng trong ví dụ là **đầu vào riêng cần tự cung cấp**, không nằm trong repo. Không tải dataset clone giọng, model nặng, khóa/API hay video cá nhân lên đây.

## Kiểm thử kỹ thuật

```bash
python3 -m pip install -r tests/requirements.txt
python3 tests/make_fixtures.py /tmp/video-skills-test
python3 skills/talking-head-reference-editor/scripts/render.py /tmp/video-skills-test/hanta-smoke --setup-only
python3 skills/talking-head-reference-editor/scripts/render.py /tmp/video-skills-test/hanta-smoke test.mp4
python3 skills/tour-itinerary-video/scripts/render.py /tmp/video-skills-test/tour-smoke test.mp4
python3 skills/talking-head-reference-editor/scripts/qa.py /tmp/video-skills-test/hanta-smoke/out/test.mp4 /tmp/video-skills-test/hanta-smoke/out/qa --expected-frames 288
python3 skills/tour-itinerary-video/scripts/qa.py /tmp/video-skills-test/tour-smoke/out/test.mp4 /tmp/video-skills-test/tour-smoke/out/qa --expected-frames 300
python3 tests/test_validation.py /tmp/video-skills-test
```

Các fixture chỉ là màu/pattern/tone tổng hợp, không phải video quảng cáo mẫu. Sau kiểm kỹ thuật vẫn cần kiểm nội dung, vị trí người, nhãn và âm thanh của từng job thực tế. Không tuyên bố đã nghe chỉ từ metadata hoặc ASR.

Đã kiểm trên macOS Apple Silicon; không hứa đã thử Windows/Linux. Mỗi nơi sử dụng tự xác minh quyền tư liệu và điều kiện giấy phép Remotion. [Thành phần bên thứ ba](docs/THIRD_PARTY.md).
