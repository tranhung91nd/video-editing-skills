---
name: tour-ad-vertical
description: Dựng video quảng cáo tour du lịch dọc 9:16 (Reels/TikTok, khoảng 90 giây) có lồng tiếng Việt theo công thức AIDA - viết lời thoại từ thông tin tour (Google Drive/file content/fanpage chi nhánh), lồng giọng VieNeu + Whisper kiểm tra, nhạc nền lấy từ link TikTok, tự tìm source TikTok nhiều view sạch chữ, khung chữ thương hiệu (logo + tên chi nhánh, thẻ địa danh vàng, phụ đề hộp navy từ khoá vàng, thẻ giá, bảng lịch khởi hành, màn kết số điện thoại + địa chỉ) render bằng Remotion. Dùng khi người dùng gửi thông tin một tour (lịch trình, giá, ngày khởi hành) và muốn lời thoại quảng cáo, hoặc muốn dựng video dọc quảng cáo tour từ lời thoại đó; cả khi nói "viết lời thoại AIDA cho tour", "dựng video dọc giống video Nam Ninh", "edit video quảng cáo tour cho chi nhánh".
---

# Video quảng cáo tour dọc 9:16 (mẫu Nam Ninh 3N2Đ – VNE Quảng Trị)

Mẫu gốc nằm ở `examples/nam-ninh-quang-tri/`: `script.json` (lời thoại 23 câu), `shots.json` (42 cảnh, nhãn địa danh, thẻ, thông tin thương hiệu), `cands.txt` (source TikTok). Video ra dài 92 giây, 1080×1920. Đọc mẫu trước khi làm job mới, nhưng không chép giá, ngày hay số điện thoại của mẫu sang tour khác.

Đường dẫn công cụ (cài một lần bằng `scripts/setup.sh`, kiểm tra bằng `scripts/doctor.sh`):
- `TTS=~/.tour-ad-video/tts/bin/python`: VieNeu, Pillow, librosa
- `ASR=~/.tour-ad-video/asr/bin/python`: mlx-whisper
- `SK=<thư mục skill này>`

Nếu `doctor.sh` báo lỗi, chạy `bash $SK/scripts/setup.sh` trước rồi mới làm job.

## 1. Lấy thông tin tour
- Link Google Drive: tải bằng `rclone` nếu máy có remote, không thì nhờ người dùng tải file về. File content (.docx) đọc bằng `textutil -convert txt -stdout file.docx`.
- Lấy giá, lịch khởi hành, điểm đến, phương tiện **đúng như file**. Không tự thêm "lo visa", "khách sạn 4 sao", "xe đón tận nơi" khi file không ghi.
- Video làm cho chi nhánh: mở fanpage trong trình duyệt, tab Giới thiệu (`?sk=about`). Lấy tên trang, số điện thoại, địa chỉ. Email không đưa vào lời đọc.
- Nội dung "tuyển cộng tác viên, com cao" là cho đại lý, không đưa vào video bán cho khách.

## 2. Viết lời thoại AIDA
- **A (0–12s):** hook gọi tên người xem theo địa phương chi nhánh + giá + điều bất ngờ ("Người Quảng Trị ơi, chưa tới ba triệu rưỡi mà đã được đi nước ngoài").
- **I (12–43s):** từng điểm đến, mỗi điểm 2–3 câu tả cảnh cụ thể (màu sắc, ánh đèn, món ăn).
- **D (43–65s):** trải nghiệm, sự tiện (xe đưa đón, không phải lo đường) và giá.
- **A (65–90s):** lịch khởi hành, chỗ có hạn, số điện thoại, địa chỉ, câu chốt có tên đơn vị.
- **Độ dài:** VieNeu đọc khoảng 4,7 âm tiết/giây. Video 90 giây cần khoảng 340–400 âm tiết. Nếu đọc ra dài hơn thì tăng `--tempo` ở bước ghép, không cắt câu.
- **Gửi lời thoại cho người dùng duyệt trước khi dựng.** Khi người dùng muốn dựng, hỏi những gì còn thiếu (dùng câu hỏi có lựa chọn):
  - điểm đón khách (không biết thì không nhắc)
  - giọng đọc
  - kiểu khung chữ
  - xử lý độ dài
- Viết `voice/script.json` theo mẫu. Mỗi câu có:
  - `id`, `sec` (A/I/D/A2), `pause`
  - `tts`: câu cho máy đọc
  - `display`: phụ đề một dòng, khoảng 30 ký tự, `<từ khoá>` sẽ tô vàng
- Quy tắc viết `tts`:
  - Mọi con số viết bằng chữ ("ba triệu bốn trăm chín mươi nghìn đồng", "hai mươi bảy tháng mười một").
  - Số điện thoại đọc theo cụm, có dấu phẩy ("không chín không, ba chín hai, bốn tám sáu không").
  - Không viết chữ IN HOA vì máy sẽ đánh vần.
  - Tên thương hiệu viết "Vietnam Express Tour".

## 3. Lồng tiếng
```bash
bash $SK/scripts/new_job.sh <job>
$TTS $SK/scripts/voice_generate.py <job>/voice 4           # 4 bản mỗi câu (~2 phút)
$ASR $SK/scripts/voice_analyze.py <job>/voice              # Whisper chấm, chạy ngầm ~5 phút
$ASR $SK/scripts/voice_assemble.py <job>/voice --tempo 1.15 --pause-scale 0.75
```
- Giọng nữ VieNeu:
  - Ngọc Huyền: Bắc, tự nhiên
  - Đoan Trang: Bắc
  - Ngọc Trân: Trung
  - Thùy Dung: Nam
  - Liệt kê đủ giọng bằng `Vieneu().list_preset_voices()`.
- Claude không nghe được. Whisper nghe giọng miền Trung/Nam sai dấu nhiều (ví dụ "Thái Bình" thành "thái bên"), nên điểm `match` thấp chưa chắc là đọc sai. Phải nói rõ với người dùng là cần họ nghe lại.
- Câu có điểm thấp bất thường thì tạo thêm bản: `voice_generate.py <job>/voice 8 s09`, rồi chạy `voice_analyze.py <job>/voice s09`.
- Muốn chọn tay bản đọc thì ghi `voice/pick.json`.
- Chỉnh `--tempo` cho tổng thời lượng in ra khoảng 90 giây (mẫu: 1,15 → 92,4 giây).
- Sau khi ghép: chép `timeline.json` vào `remotion/src/`, rồi hard link narration (`ln -f voice/narration.wav remotion/public/narration.wav`).

## 4. Nhạc nền
```bash
yt-dlp -q -o "<job>/music/bgm.%(ext)s" "<link TikTok người dùng gửi>"
ffmpeg -v error -i <job>/music/bgm.mp4 -vn -ac 2 -ar 48000 -t 100 <job>/remotion/public/music.wav
```
Template tự hạ nhạc xuống 0,13 khi có lời và nâng lên 0,45 ở chỗ nghỉ.

## 5. Source TikTok (nhiều view, sạch chữ)
1. **Tìm link:** trang tìm kiếm TikTok cần đăng nhập, nên dùng trang hashtag. Mở `https://www.tiktok.com/tag/<hashtag>` trong trình duyệt, cuộn trang rồi chạy JS lấy `a[href*="/video/"]`. Mỗi điểm đến thử cả hashtag tiếng Việt viết liền (`thanhtuson`) và tiếng Trung (`青秀山`, `太平古镇`, `南宁之夜`).
2. **Ghi danh sách:** ghi vào `<job>/source/cands.txt`, mỗi dòng `<nhóm> <@user/video/id>`. Nhóm là mã ngắn của cảnh (ví dụ `ts` = Thanh Tú Sơn, `cd` = phố đêm).
3. **Lấy view và tải:** `python3 $SK/scripts/tiktok_meta.py <job>/source/cands.txt --download --min-views 4000`. Script lấy view/like và chỉ tải clip dọc. Nhóm nào ít clip nhiều view thì hạ `--min-views` cho riêng nhóm đó.
4. **Quét chữ:** `python3 $SK/scripts/screen_text.py <job>/source/raw/*.mp4 --out <job>/work/screen`. Script trả `clean_ranges` cho từng clip.
5. **Xem bằng mắt:** `$TTS $SK/scripts/contact_sheet.py <job>`, rồi mở từng ảnh trong `work/sheets/`. Chọn cảnh hot, đẹp, lạ: flycam, show ánh sáng, lửa, hoa, người mặc cổ trang, món ăn. Loại cảnh selfie, vlog nói chuyện, trong phòng khách sạn, cảnh mờ hoặc loá nắng.
6. **OCR có điểm mù.** Nó bỏ sót chữ viết tay, font trang trí, chữ Thái và tiêu đề chữ Trung hai dòng. Thấy chữ chèn trên ảnh thu nhỏ thì **bỏ cả clip**, vì clip đó thường có chữ ở đoạn khác nữa.

## 6. Ghép cảnh
- **Viết `<job>/shots.json`** theo mẫu:
  - `total`: lấy từ bước ghép giọng.
  - `shots`: danh sách `[giây trên video, tên clip, giây trong clip]`, mỗi cảnh dài 1,5–2,7 giây và đổi cảnh theo câu thoại.
  - `tags`: thẻ địa danh, đặt từ câu nhắc địa danh đến hết đoạn đó.
  - `cards`: `price` (lúc đọc giá), `schedule` (lúc đọc lịch), `end` (từ lúc đọc số điện thoại đến hết).
  - `brand`: thông tin thương hiệu.
- **Chạy kiểm tra:** `$TTS $SK/scripts/plan_check.py <job>`. Dòng `FIX` nghĩa là cảnh ra ngoài đoạn sạch chữ hoặc vắt qua điểm cắt của clip gốc: dời giây trong clip hoặc đổi clip, rồi chạy lại đến khi hết `FIX`.
- **Xem `work/plan_sheet.jpg`.** Mỗi ô là khung giữa của một cảnh, kiểm tra cảnh có khớp câu thoại không.
- **Logo:** đặt PNG nền trong vào `remotion/public/logo.png` (template đã có sẵn logo Vietnam Express Tour).

## 7. Render và kiểm tra
```bash
cd <job>/remotion && npx remotion render src/index.tsx Main ../out/draft.mp4 --scale=0.6667 --crf=26 --concurrency=6
$TTS $SK/scripts/qc_sheet.py <job>/out/draft.mp4 <job>/work/qc     # mở từng qc_*.jpg
ffmpeg -v error -y -i <job>/out/draft.mp4 -c:v libx264 -crf 28 -preset slow -c:a aac -b:a 128k -movflags +faststart <job>/out/<ten>-nhap-v1.mp4
```
- **Vòng sửa** chỉ xuất bản nháp 720p, nén dưới 30 MB để gửi được qua điện thoại. Gửi xong thì xoá `draft.mp4`.
- **Bản 1080p** chỉ render khi người dùng chốt:
  1. Tải lại đúng các clip đã dùng ở chất lượng cao nhất: `tiktok_meta.py ... --download --best`, rồi chạy lại `plan_check.py`.
  2. Render bỏ `--scale`, dùng `--crf=18`.
- **Gửi người dùng xem** kèm danh sách những gì cần họ kiểm tra: phát âm, tên riêng, giá.

## Lỗi người dùng đã bắt (đừng lặp lại)
- Cảnh dính chữ chèn "Vi vu 3N2Đ Nam Ninh" lọt qua OCR. Phải soát `qc_sheet` bằng mắt mọi lần.
- Chữ chèn mờ nhỏ ở góc (ví dụ "航拍 嗍广西" trên flycam) chỉ xuất hiện từ giữa clip và nhìn ảnh 135px không thấy. Soát QC ở cỡ ít nhất 216×384, và xem lại to hơn các cảnh nằm dưới thẻ giá hoặc màn kết.
- Cảnh tượng đá loá nắng bị chê "mờ nhoè". Loại cảnh có lens flare hoặc mờ ngay ở bước chọn.
- Chữ chèn phải một dòng, không dính nhau: logo ở trên cùng, thẻ địa danh bên dưới logo, phụ đề ở khoảng 70% chiều cao. Màn giá và màn kết thì ẩn phụ đề.
- Chữ có sẵn trong cảnh (biển hiệu, cổng "南宁之夜") giữ lại được. Chỉ loại chữ chèn hậu kỳ (caption, sticker, watermark, số điện thoại của đơn vị khác).
