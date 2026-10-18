---
name: talking-head-reference-editor
description: Dựng video người nói dọc 9:16 theo phong cách Hanta AI, với chữ vàng Anton/Montserrat, thẻ đồ họa, cảnh chèn không che người và CTA; chép lời, lập edit.json theo mốc nguồn và xuất MP4 bằng Remotion. Dùng cho talking-head hoặc video chuyên gia theo mẫu này, không dùng cho montage tour có lời thuyết minh.
---

# Talking-head theo mẫu Hanta AI

Đây là bản đóng gói từ template `talking-head-editor` đã tạo video Hanta AI, không phải bản League Gothic cũ. Giữ cách bố trí và chuyển động của mẫu; không tuyên bố giống từng pixel khi nội dung, người nói hoặc hệ điều hành khác nhau.

## Nhận đầu vào

Nhận video người nói và tư liệu chèn được phép dùng. Mỗi công việc tạo một thư mục riêng:

```
job/
  media/raw.mp4
  media/assets/...
  edit.json
  analysis/
  out/
```

Dùng thời gian **video gốc** cho cuts, captions và inserts. Đọc [cấu trúc edit.json](references/plan.md) khi viết kế hoạch; [style.md](references/style.md) mô tả hero, sub, brand, card, compare, proof, pip, broll và CTA.

Nếu có transcript sẵn thì dùng lại và kiểm tên riêng. Khi cần ASR, chạy `scripts/transcribe.py` trong Python có backend tương ứng; `--help` không cần model. Đọc [runtime.md](references/runtime.md) để cài backend tùy chọn. Mô hình nhận dạng và TTS không nằm trong gói.

## Dựng

- Hero tóm ý, nhấn từ khóa vàng. Sub cho câu chuyển; brand khi giới thiệu tên chương trình; CTA ở cuối. Mỗi cụm đủ thời gian đọc, không tự bịa thành tích hoặc ảnh bằng chứng.
- Căn chữ theo lời nói, không chỉ theo đầu câu ước lượng. Kiểm cả phần chữ được gõ chưa kịp hết trước khi biến mất.
- Kiểm vị trí mặt/người trước khi đặt pip. Với người nói như mẫu Hanta, cửa sổ chèn nằm trong phần trống phía trên; không che đầu/mặt. Giữ cảnh Việt Nam nếu ngữ cảnh là sự kiện/doanh nghiệp Việt.
- Tránh dùng bảng tên hoặc sân khấu của sự kiện khác làm người xem hiểu nhầm sự kiện đang được giới thiệu. Thẻ toàn màn hình không chồng lên hero/sub.
- Giữ giọng thật của video; nhạc và SFX nhỏ hơn lời nói. Không cắt cụt từ hoặc đổi nghĩa vì bỏ khoảng lặng.

## Chạy

Tất cả đường dẫn script tính từ thư mục skill này, không theo thư mục người tạo:

```bash
python3 scripts/doctor.py
python3 scripts/render.py /path/to/job --check-only
python3 scripts/render.py /path/to/job --setup-only
python3 scripts/render.py /path/to/job final.mp4
python3 scripts/qa.py /path/to/job/out/final.mp4 /path/to/job/out/qa
```

Lần setup đầu dùng `npm ci` từ lockfile trong render-project của job. Những lần sau tái sử dụng đúng phiên bản. Không tự mở Studio, trình duyệt hoặc file video. Mặc định một luồng render; chỉ tăng khi máy phù hợp hoặc người dùng yêu cầu. Render ngắn bằng `--frames=0-59` để kiểm trước, rồi render toàn bộ.

Font Anton và Montserrat có sẵn trong assets/fonts cùng OFL, không tải font khi render. Pop/whoosh được tạo cục bộ nếu job chưa có file riêng. Script `render.sh` chỉ gọi render.py; không có template thứ hai.

## Bàn giao

Chạy QA giải mã toàn bộ, đối chiếu số frame, kiểm các bảng ảnh và các thẻ ở kích thước đầy đủ. Đối chiếu lại transcript/timing và nghe khi có khả năng phát nghe thực sự; không nói đã nghe nếu chỉ kiểm metadata/ASR. Nếu không nghe trực tiếp được, ghi rõ giới hạn này. Dọn đúng các tiến trình do job tạo; không đóng chương trình khác của người dùng.

Ví dụ [hanta-reference.json](examples/hanta-reference.json) lưu kế hoạch của bản mẫu; các video/nhạc cá nhân không được đóng gói. Đọc [reference-inputs.md](references/reference-inputs.md) trước khi dùng ví dụ để tái dựng.
