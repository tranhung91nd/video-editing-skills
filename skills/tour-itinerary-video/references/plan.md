# edit.json — tour 16:9

Canvas cố định 1920×1080. duration là tổng giây, fps mặc định 30. Mốc cảnh và caption theo thời gian output/narration, khác talking-head dùng mốc nguồn.

- brand: name, logo (relative media path hoặc null), whiteWordmarkFrom (phần trăm từ trái; null/100 nếu không cần xử lý chữ trắng). Giữ alpha gốc.
- voice: file, name (ghi chú), speed:1. File được phát một lần từ đầu, không time-stretch.
- music: file dài ít nhất bằng composition, volume (mặc định .32), fadeIn (.4), fadeOut (4). Nếu muốn loop phải chuẩn bị file dài sẵn, không loop ngầm.
- region, edition: nhãn góc. days: danh sách ngày cần hiển thị tiến trình.
- intro: kicker, title, accent, routeLabel, photos (hai file ảnh).
- routePoints: 2–4 điểm {x,y,name} trên viewBox 1280×500; là sơ đồ trang trí. rail: from, to, label cho chặng tàu.
- cta: kicker, title, accent, chips (mảng), prompt, button, image. Không đưa giá/điện thoại chưa xác minh vào chữ.
- shots: {s,e,src,day,title,sub?,type?,position?,focus?,mediaStart?}. type: intro, route, cta, detail, postcard hoặc bỏ trống. position:lower hạ nhãn, focus là object-position ảnh. mediaStart là offset nguồn video tính giây. Shots liên tục, không có lỗ timeline và không vượt duration.
- captions: [{text,startMs,endMs}]. Các trường start/end theo giây có thể giữ trong ví dụ để tra cứu nhưng renderer dùng Ms.
- fontFamily: optional; mặc định Tour Sans có sẵn. palette: tùy chọn đủ cream,gold,red,ink.

Đọc ví dụ đi kèm để thấy một plan hoàn chỉnh. Các tài nguyên tham chiếu phải được người dùng cung cấp/được phép dùng; không có video hay giọng clone trong repository.
