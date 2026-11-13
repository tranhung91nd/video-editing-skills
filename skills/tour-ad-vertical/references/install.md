# Cài skill "tour-ad-vertical" cho Claude Code

Skill này giúp Claude dựng video quảng cáo tour dọc 9:16, khoảng 90 giây, có lồng tiếng Việt. Claude làm hết các bước sau:

1. Viết lời thoại AIDA
2. Lồng giọng
3. Lấy nhạc TikTok
4. Tìm source TikTok nhiều view, sạch chữ
5. Chèn khung chữ thương hiệu
6. Xuất video

Video mẫu đã làm bằng skill này: tour Nam Ninh 3N2Đ cho VNE Quảng Trị.

## Máy cần có
- Mac chip Apple (M1/M2/M3/M4). Bộ chấm giọng mlx-whisper chỉ chạy trên chip này.
- Claude Code (app desktop hoặc terminal).
- Khoảng 10 GB ổ trống cho mô hình giọng và Whisper. Lần đầu chạy sẽ tải mô hình từ mạng.

## Cài (làm một lần)
1. Tải ZIP ở trang Releases của repo, giải nén, mở Terminal tại thư mục vừa giải nén (nơi có README.md) rồi chạy:
   ```bash
   python3 scripts/install.py --target claude --skill tour-ad-vertical
   ```
   Hoặc chép tay thư mục `skills/tour-ad-vertical` vào `~/.claude/skills/`.
2. Mở Terminal, chạy:
   ```bash
   bash ~/.claude/skills/tour-ad-vertical/scripts/setup.sh
   ```
   Lệnh này cài ffmpeg, Node, yt-dlp, Python 3.10, VieNeu (giọng đọc), mlx-whisper và Remotion. Mất khoảng 10–20 phút. Nếu máy chưa có Homebrew thì cài trước tại https://brew.sh.
3. Kiểm tra:
   ```bash
   bash ~/.claude/skills/tour-ad-vertical/scripts/doctor.sh
   ```
   Tất cả các dòng phải là `OK`.
4. Mở phiên Claude Code mới để Claude nhận skill.

## Cách dùng
Mở Claude Code trong một thư mục làm việc (ví dụ `~/Videos/tour`), rồi gõ giống người tạo skill đã dùng:

> Viết giúp tôi lời thoại quảng cáo video (khoảng 1 phút 30s) cho sản phẩm này theo công thức AIDA: <link Drive hoặc dán nội dung tour>

> Tour này quảng cáo cho chi nhánh <tên>. Xem SĐT và thông tin trên fanpage <link> bổ sung vào lời thoại.

> Edit giúp tôi video dọc 9:16 dựa trên lời thoại trên. Source: TikTok nhiều view và lượt thích. Lời thoại: giọng nữ nhẹ nhàng. Nhạc nền: <link TikTok>. Câu lệnh còn thiếu gì thì hỏi lại.

Claude sẽ hỏi lại những gì còn thiếu, như điểm đón, giọng đọc, kiểu khung chữ. Sau đó Claude gửi bản nháp 720p. Bạn góp ý theo số giây, ví dụ "giây 24 bị mờ, thay cảnh khác". Khi bạn chốt, Claude mới render bản 1080p.

## Cần biết
- **Claude không nghe được âm thanh.** Giọng đọc chỉ được kiểm tra bằng Whisper, nên người dùng phải tự nghe lại tên riêng, giá và số điện thoại.
- **Logo:** skill có sẵn logo Vietnam Express Tour. Đơn vị khác thì đưa logo PNG nền trong cho Claude.
- **Bản quyền source:** source TikTok là video của người khác. Bên dùng tự cân nhắc quyền sử dụng khi chạy quảng cáo.
- **Remotion:** công ty từ 4 người trở lên cần mua giấy phép Remotion (xem remotion.dev/license).
