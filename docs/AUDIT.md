# Kiểm toán hai video và trạng thái đóng gói

Ngày kiểm tra: 18/10/2026. Đã kiểm khung hình xuyên suốt, các cảnh thẻ/intro/tuyến đường/CTA, metadata, mã nguồn và hash của đúng hai file được gửi. Đã giải mã toàn bộ hai MP4, không gặp lỗi. Không tuyên bố đã nghe trực tiếp toàn bộ âm thanh.

## 1. Hanta ai.mp4

- Video: 1080×1920, 30 fps, 1422 frame; 47,4 giây hình / khoảng 47,445 giây container.
- SHA-256: `bb49e2843dda794997fa8c0378d20f974339a5bad19e3b803fdff73a3d363fbd`.
- Khớp đúng `job-123123123/out/final.mp4`. edit.json có hai đoạn giữ 11.2–35.08 và 35.52–59.05 giây của nguồn. Các insert là sự kiện du lịch Việt Nam ở phía trên, thẻ Morning/Build, brand HANTA AI Basecamp 2026 và CTA.
- Workflow gốc: **talking-head-editor** của Claude, renderer **Remotion**. Template cùng hash tồn tại ở bản alias talking-head-reference-editor của Codex. Đường lệnh dựng trong lịch sử gọi scripts/render.sh của talking-head-editor.
- Đặc trưng: Anton kéo ngang khoảng 1.245×, Montserrat thường/nghiêng, chữ vàng/quầng sáng, phụ đề gõ chữ, thẻ card/compare/proof, pip phía trên không che người nói, âm pop/whoosh và CTA mũi tên.

Trước đóng gói: có hai template song song (bản Claude đúng Hanta và bản offline League Gothic cũ). render.sh và render.py trỏ hai quy trình khác nhau; runtime/Whisper có đường dẫn riêng máy; chưa có lockfile và installer thống nhất. Vì vậy không coi bản cũ là gói hoàn chỉnh có thể chuyển máy.

Sau sửa: skill **talking-head-reference-editor** có một template đúng nguồn Hanta; offline Anton/Montserrat có OFL; một entry render.py, render.sh gọi cùng entry; validator hỗ trợ brand và kiểm proof đúng kiểu trước khi render; runtime theo job, lockfile và installer sao lưu.

## 2. Cửu Trại Câu V6 — Thục Đoan

- Video: 1920×1080, 30 fps, 2310 frame; 77 giây hình / khoảng 77,013 giây container.
- SHA-256: `8b586018266b3ad8c134e15f813792f4f87b9ae75e28a4237b2d212df1c9dffe`.
- Khớp đúng output của `job-cuu-trai-cau-ngang`. Mã nguồn: JourneyThucDoan.tsx, data-thuc-doan.json, composition ThucDoan. Kế hoạch V6 ghi giọng Thục Đoan qua VieNeu v3 Turbo ở tốc độ 1.0; không time-stretch bản này.
- Đây là **dự án Remotion viết riêng**, không có một skill tour tổng quát đã hoàn thiện vào thời điểm tạo V6. Không nhầm với bản HyperFrames 66 giây/Hải Đăng làm sau đó.
- Đặc trưng: intro 6N5Đ và sơ đồ tuyến, 25 cảnh, nhãn ngày/địa danh, Ken Burns, tan cảnh 12 frame, tàu chạy từ Thành Đô hướng Cửu Trại Câu, logo trong suốt, phụ đề và CTA ảnh tròn.

Sau đóng gói: **tour-itinerary-video** tham số hóa lịch trình, cảnh, phụ đề, logo, màu, tuyến tàu, thương hiệu, CTA và audio; không khóa vào Cửu Trại Câu. Ví dụ V6 lưu đúng timing và lời đã dùng. Giọng/audio riêng là đầu vào được duyệt; skill không chứa model hay dữ liệu clone giọng. Avenir Next không phân phối lại; font Be Vietnam Pro OFL kèm làm fallback.

## Kiểm thử bản đóng gói

- Hai kế hoạch gốc qua preflight: Hanta 1422 frame; tour V6 2310 frame.
- Render fixture tự tạo bằng runtime npm cài mới từ lockfile: Hanta 288 frame dọc; tour 300 frame ngang. Cả hai giải mã đầy đủ, có audio, metadata đúng; đã kiểm bảng ảnh và khung thẻ/tuyến.
- TypeScript: tsc --noEmit đạt ở cả hai template; frontmatter cả hai skill hợp lệ.
- 12 kiểm thử hành vi đạt: các kiểu insert hợp lệ, brand, thiếu file, vượt nguồn, cắt chồng, đường dẫn ra ngoài media, proof sai kiểu, cắt cụt narration, đổi tốc độ giọng ngầm và lỗ timeline tour.
- Cài thử vào thư mục trống, thay bản cũ có backup, đối chiếu hash từng file: đạt.
- Không mở Studio/tab/file khi kiểm thử. Render một luồng, hữu hạn, dọn nhóm tiến trình do job tạo.

## Phạm vi hoàn chỉnh

Gói hoàn chỉnh về workflow, template, font phân phối được, setup, kiểm tra, render, ví dụ và cập nhật Git. Không phải bản phát hành kèm video cá nhân, footage tải mạng, nhạc hoặc dataset giọng. Muốn dựng lại hai video mẫu, cung cấp các file trong examples/required-inputs.json; stage_example.py sẽ kiểm và gom đúng nguồn vào job mới. Mỗi job vẫn cần rà soát sự thật, quyền tư liệu và âm thanh thực tế.

macOS Apple Silicon đã kiểm; Windows/Linux chưa được thử. Chỉ đặt repo riêng tư, không cấp quyền cộng tác hay đăng video đi nơi khác ngoài yêu cầu tải skill lên GitHub.
