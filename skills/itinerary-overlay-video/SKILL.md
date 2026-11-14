---
name: itinerary-overlay-video
description: Chèn đồ hoạ lịch trình lên một video du lịch dọc 9:16 đã dựng sẵn, sạch chữ và có sẵn giọng đọc (thường tiếng Anh, cho khách nước ngoài). Giữ nguyên hình, thứ tự cảnh và âm thanh; thêm hook, màn tiêu đề, thẻ ngày (phương tiện, ngày, địa danh, hoạt động), bản đồ Việt Nam có đảo và Hoàng Sa/Trường Sa với tuyến đường sáng dần, thanh tiến độ N ngày, câu hỏi chuyển, thẻ dịch vụ đã bao gồm, phụ đề trọn câu không trùng với chữ trên khung, màn kết logo + website + WhatsApp. Render bằng HyperFrames, nháp 720p trước, 1080p khi chốt. Dùng khi người dùng gửi "source gốc không dính text" hoặc video lịch trình nhiều ngày và muốn thêm chữ/font chuyên nghiệp để khách nước ngoài hiểu lịch trình; cả khi nói "edit lại font chữ video lịch trình", "thêm bản đồ và thẻ ngày", "dựng giống video Vietnam 10 ngày".
---

# Đồ hoạ lịch trình trên source sạch chữ (mẫu Vietnam 10 ngày – Vietnam Express Tour)

Mẫu gốc: `examples/vietnam-10days/job.json`, video 94,5 giây, 7 chặng, 10 ngày, 34 vế câu thoại (5 vế hiện phụ đề). Đọc mẫu trước khi làm job mới. Không chép số ngày, địa danh, website hay số WhatsApp của mẫu sang thương hiệu khác.

Công cụ (cài một lần bằng `bash $SK/scripts/setup.sh`, kiểm tra bằng `bash $SK/scripts/doctor.sh`):
- `PY=~/.itinerary-overlay/venv/bin/python`: mlx-whisper (Mac chip Apple), Pillow, numpy
- HyperFrames CLI ghim bản `hyperframes@0.8.181`, gọi qua `npx`
- `SK=<thư mục skill này>`

## 1. Tạo job
```bash
bash $SK/scripts/new_job.sh <job_dir> <source.mp4> <logo.png> en
```
Lệnh này tạo các file sau:
- `hyperframes/assets/footage.mp4`: hình, đổi sang 30 fps cố định. Clip VFR làm lệch giờ, nên không dùng thẳng file gốc.
- `hyperframes/assets/audio.wav`: âm thanh gốc.
- `hyperframes/assets/logo-white.png`: logo đã đổi chữ tối sang trắng.
- `plan/words.json`: mốc thời gian từng từ.
- `plan/clauses_draft.json`: lời thoại tách thành các vế câu.
- `plan/scenes.txt`: các điểm cắt cảnh.
- `plan/contact_2s.jpg`: ảnh ghép, ô thứ n là giây 2n.
- `job.json`: chép từ mẫu.

Source tải từ Google Drive: `rclone backend copyid <remote>: <file_id> <dir>/` nếu máy có remote. File tải về có thể không có đuôi `.mp4`, cần đổi tên.

## 2. Viết job.json
Đọc `plan/clauses_draft.json` (lời thoại) và xem `plan/contact_2s.jpg` (cảnh) cùng nhau rồi điền:
- `duration`: độ dài source. `total_days`: số ngày của tour.
- `brand`: tên, website, WhatsApp.
- `word_fixes`: sửa tên địa danh Whisper nghe sai. Từ mẫu: "Huan Giam" → "Hoan Kiem", "Hui" → "Hue", "Tianmu" → "Thien Mu", "Halong" → "Ha Long".
- `hook` (0 → `end`): `kicker`, `big`, các `subs` có mốc `at` khớp lời đọc. Viết `[từ]` để tô vàng.
- `title` (`hook.end` → `end`): dòng lớn, dòng 2, dòng phụ và chuỗi `route`.
- `stops`: kinh độ, vĩ độ, `side` của nhãn (`l`, `r`, hoặc `bl` là dưới-trái, dùng khi nhãn đè lên đảo).
- `legs`: mỗi chặng gồm các trường sau:
  - `start`/`end`: bắt đầu ở câu thoại nhắc tới điểm đó, rồi xê dịch tới điểm cắt gần nhất trong `scenes.txt`.
  - `day`, `place` (IN HOA), `last_day` (ô tiến độ tô tới ngày này).
  - `transport`: `[boat|car|train|plane, "nhãn"]` hoặc `null`.
  - `activities`: 2–3 mục, mỗi mục không quá 22 ký tự.
  - `stop`: số thứ tự điểm trên bản đồ. `bend` (tuỳ chọn) chỉnh độ cong đường nối.
- `plan.start`, `inclusions` (`start` và từng mục `[giây, chữ]` đúng lúc giọng đọc nhắc tới), `end_card`.
- `captions.clauses`: chép từ `clauses_draft.json`. Gộp hoặc tách vế cho trọn ý, rồi đặt `true`/`false` theo mục 3. Ghép các vế lại phải ra đúng toàn bộ lời thoại, nếu không `build.py` dừng và chỉ ra chỗ lệch.
- **Chia ngày phải theo lịch trình tour thật.** Lời thoại thường không nói ngày nào ở đâu. Nếu người dùng chưa đưa lịch trình thì hỏi, hoặc ghi rõ đây là giả định trong câu trả lời.

## 3. Phụ đề: quy tắc người dùng đã chốt
- Một vế phụ đề là một câu hoặc vế câu trọn ý. Không cắt ngang tên riêng như "Vietnam Express Tour" hay "Hai Van Pass". Tên trong `captions.highlight` được tô vàng và không bị xuống dòng giữa chừng. Mỗi phụ đề tối đa 2 dòng.
- **Câu nào đã có chữ trên khung thì đặt `false`.** Áp dụng cho hook, tiêu đề, thẻ ngày, danh sách dịch vụ, câu hỏi chuyển và màn kết. Ví dụ: thẻ HANOI đang hiện thì bỏ "First, you'll start in Hanoi"; danh sách dịch vụ đang hiện thì bỏ "hotels, transfers, flights". Trong mẫu, cả phần lịch trình không có phụ đề.
- Vế ngắn kiểu "Next," hay "From there," không đứng một mình.

## 4. Soát trước khi render
```bash
bash $SK/scripts/snapshot.sh <job_dir> 5.5,17,22.5,30,41.5,50.5,61,70,76.5,85,92
```
Xem ảnh ghép và sửa tới khi đạt các điểm sau:
- Chữ không che mặt người. Ví dụ ở mẫu: thẻ dịch vụ bị dời lên trên để chừa mặt cô gái và biển "Hanoi Train Street".
- Dòng hành trình trên màn tiêu đề không bị phụ đề đè. Nhãn bản đồ không chạm logo và không đè lên đảo.
- Mặt người thường di chuyển trong cảnh, nên chụp thêm vài mốc trong cùng một cảnh trước khi kết luận là không che.
- Thông số bố cục và lý do ở [references/design.md](references/design.md).

## 5. Render
```bash
bash $SK/scripts/render.sh <job_dir> draft <ten-video>   # vòng sửa: out/<ten>-draft-720p.mp4
bash $SK/scripts/render.sh <job_dir> final <ten-video>   # chỉ khi người dùng chốt: out/<ten>-1080p.mp4
```
- Video 94 giây render mất khoảng 3–4 phút, nên chạy nền.
- Sau khi render, cắt vài khung hình từ file MP4 để kiểm tra lại.
- Bản final nặng khoảng 230 MB. Nếu cần bản nhẹ để đăng: `ffmpeg -i in.mp4 -c:v libx264 -crf 21 -preset slow -movflags +faststart -c:a aac -b:a 192k out-nhe.mp4` (khoảng 80 MB).
- Gửi file qua app có giới hạn 30 MB. File lớn hơn thì xuất thêm một bản 720p `-crf 30` để xem trên điện thoại.

## Không làm
- Không cắt lại cảnh, không thêm nhạc, không đổi giọng đọc. Skill này chỉ thêm lớp đồ hoạ.
- Không ghi tên "Hoang Sa" và "Truong Sa" trên bản đồ, chỉ vẽ các chấm đảo (người dùng đã yêu cầu). Không bỏ hai quần đảo khỏi bản đồ.
- Không tự thêm giá, ưu đãi hay dịch vụ mà lời thoại hoặc người dùng không nói tới.
