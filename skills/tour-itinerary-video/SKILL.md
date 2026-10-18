---
name: tour-itinerary-video
description: Dựng video quảng bá tour ngang 16:9 có lời thuyết minh theo lịch trình ngày, nhãn địa danh, phụ đề, sơ đồ hành trình/tàu, logo và CTA bằng Remotion; lấy phong cách từ Cửu Trại Câu V6 giọng Thục Đoan. Dùng khi có tour hoặc lịch trình cần dựng, không dùng cho talking-head hay video chỉ cắt theo nhạc.
---

# Video tour theo lịch trình

Skill được tách từ mã nguồn Remotion của Cửu Trại Câu V6, 77 giây, 1920×1080. Đây là workflow tái sử dụng mới; video V6 trước đó được dựng bằng dự án Remotion riêng, không phải HyperFrames.

## Nội dung và tư liệu

- Lấy ngày, tuyến đường, điểm tham quan và dịch vụ từ lịch trình người dùng hoặc nguồn đã đối chiếu. Kiểm nguồn hiện hành khi cần giá, lịch khởi hành hay liên hệ. Không tự thêm giá/ưu đãi.
- Viết lời giới thiệu ngắn có hook, phần trải nghiệm theo ngày, và CTA tư vấn. Chọn ngôn từ tự nhiên, kiểm phát âm tên địa danh/đơn vị.
- Dùng giọng đã được người dùng chọn/duyệt. Nhập WAV/MP3 đã tạo qua công cụ có sẵn; dữ liệu clone, model TTS và tài khoản không phải thành phần skill này. Không nhận tốc độ giọng khác 1.0 trong plan; nếu đổi bản đọc, cập nhật lại mốc cảnh và phụ đề theo file thực.
- Chọn cảnh đúng địa danh và hoạt động. Tách rõ cảnh thật/ảnh tĩnh/sơ đồ. Không trình bày sơ đồ trang trí là bản đồ địa lý chính xác. Tàu chỉ chạy trên chặng đường sắt thực tế.
- Ghi nguồn và tình trạng quyền sử dụng trong media/sources.json. Việc xem được/tải được trên TikTok hoặc YouTube không chứng minh có quyền chạy quảng cáo. Giữ dấu tác giả, logo địa điểm gốc khi có; không xóa dấu để giả tư liệu sở hữu.

## Kế hoạch

Mỗi job có `media/`, `edit.json`, `analysis/`, `out/`. Mọi src trong plan là đường dẫn tương đối bên trong media. Đọc [plan.md](references/plan.md) và [ví dụ V6](examples/cuu-trai-cau-v6.json) khi viết plan. Không sao chép lịch trình, thương hiệu hay giọng của ví dụ sang tour khác khi chưa có yêu cầu.

Giọng quyết định thời lượng; chia cảnh, nhãn và phụ đề theo mốc đọc thực tế. Cảnh ảnh có Ken Burns, cảnh đổi tan nhẹ 12 frame; chữ lò xo, intro có đường hành trình và postcard, cảnh route có tàu chạy, cuối có CTA và ảnh tròn. Giữ nhãn gọn, không đặt phụ đề đè lên tiến trình ngày.

## Chạy và kiểm

```bash
python3 scripts/doctor.py
python3 scripts/render.py /path/to/job --check-only
python3 scripts/render.py /path/to/job --setup-only
python3 scripts/render.py /path/to/job final.mp4
python3 scripts/qa.py /path/to/job/out/final.mp4 /path/to/job/out/qa --expected-frames 2310
```

Con số 2310 chỉ áp dụng ví dụ 77 giây × 30 fps; tính lại cho tour thực tế. Có thể dùng `--frames=0-59` cho thử kỹ thuật. Không tự mở preview/file, dùng một luồng mặc định và đóng tiến trình của job sau khi xuất. Đọc [runtime.md](references/runtime.md) cho setup, ASR tùy chọn và font; [reference-inputs.md](references/reference-inputs.md) liệt kê cách gom nguồn riêng cho ví dụ.

Font Tour Sans (Be Vietnam Pro) được đóng gói với OFL. Ví dụ giữ Avenir Next nếu có trên macOS, dùng Tour Sans làm fallback; không kèm font thương mại Avenir và không hứa giống từng pixel trên nền tảng khác.

Trước bàn giao: giải mã toàn bộ MP4, xác nhận kích thước/độ dài/audio, xem các mốc chuyển cảnh, route, nhãn ngày, logo và CTA ở khung đầy đủ. So phụ đề với bản đọc. Chỉ nói đã nghe khi thực sự nghe được. Thông báo giới hạn quyền tư liệu hoặc kiểm âm nếu chưa xác minh; không tự gửi Zalo/đăng mạng ngoài yêu cầu người dùng.
