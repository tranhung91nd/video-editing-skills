# Bố cục và lý do (khung 1080×1920)

Các thông số này nằm trong `assets/hyperframes/template.tpl`. Muốn đổi cho một thương hiệu khác thì sửa file template, đừng sửa `index.html` vì file đó được tạo lại mỗi lần build.

| Thành phần | Vị trí | Ghi chú |
|---|---|---|
| Vùng an toàn | trên 220 px, dưới 380 px, hai bên 64 px | Giao diện Reels/TikTok che phần ngoài vùng này |
| Thanh tiến độ | top 226, ngang toàn khung | Nhãn "YOUR N DAYS" và N ô, ô của các ngày đã qua tô vàng |
| Thẻ ngày | left 64, top 300, rộng 580 | Thẻ phương tiện có icon, ô vàng "DAY x", địa danh Roboto Black 78 px, hoạt động 38 px có chấm vàng |
| Bản đồ | right 40, top 290, 349×450 | Phạm vi kinh độ 102,1–114,8, vĩ độ 7,6–23,4, vừa đủ để hiện Hoàng Sa và Trường Sa |
| Hook | top 640, căn giữa | Dòng lớn 104 px, dòng phụ là ô navy hoặc ô vàng (`alt`) |
| Tiêu đề | top 720, căn giữa | Logo 120 px, "10 DAYS" 156 px màu vàng. Nếu đặt cao hơn thì đụng bản đồ, thấp hơn thì đụng phụ đề |
| Thẻ dịch vụ | top 250, left/right 64 | Đặt cao để chừa mặt người ở giữa khung |
| Phụ đề | top 1330, left/right 90 | Roboto Bold 52 px, `text-wrap: balance`, tối đa 2 dòng |
| Màn kết | top 520 | Logo 200 px, website 80 px màu vàng, ô WhatsApp màu xanh #128c7e |

Thương hiệu Vietnam Express Tour dùng font Roboto, màu vàng #FEC529, cam #F89B1D, navy #1A2B48. Chữ trắng có bóng mềm (đen 50%, blur 10 px), không dùng viền đen dày.

Các lớp phủ tối:
- Dải tối phía trên (cao 900 px): giúp thẻ ngày và bản đồ đọc được trên nền trời sáng.
- Vùng tối giữa khung hình elip: chỉ dùng cho hook, tiêu đề và câu hỏi chuyển.

Chuyển động:
- Chữ trượt lên 20 px và hiện dần trong 0,3–0,45 giây, ease `power3.out`.
- Đường đi trên bản đồ vẽ trọn một lượt ở màn tiêu đề. Sau đó mỗi chặng vẽ thêm đoạn của nó và làm sáng chấm điểm đến.
- Mỗi dịch vụ trong thẻ sáng lên và hiện dấu tích đúng lúc giọng đọc nhắc tới.
