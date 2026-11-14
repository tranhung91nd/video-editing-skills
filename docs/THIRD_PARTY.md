# Thành phần bên thứ ba

- Anton: assets/fonts/Anton-OFL.txt trong skill Hanta.
- Montserrat: assets/fonts/Montserrat-OFL.txt trong skill Hanta, gồm biến thể thường và nghiêng.
- Be Vietnam Pro: assets/fonts/BeVietnamPro-OFL.txt trong skill tour.
- Font được lấy từ Google Fonts upstream; OFL kèm nguyên bản. Không đóng gói Avenir Next thương mại. Hệ thống macOS có Avenir Next có thể dùng font hệ thống này theo cấu hình ví dụ, nơi khác có fallback Tour Sans.
- Remotion, React và dependency được cài qua npm theo package-lock.json. Giấy phép và điều kiện thương mại của mỗi thư viện thuộc chủ sở hữu; không được cấp lại bởi repository này.
- Không có media TikTok/YouTube, video người thật, file clone giọng, mô hình TTS hay nhạc bản quyền trong gói. Ví dụ ghi tên file đầu vào để người dùng tự cung cấp từ nguồn phù hợp.
- Logo Vietnam Express Tour (skill tour-ad-vertical, assets/remotion/public/logo.png) thuộc Công ty CP Du lịch và Sự kiện VNExpress Tour; đơn vị khác thay bằng logo của mình. Font Roboto tải từ Google Fonts qua @remotion/google-fonts. Mô hình giọng VieNeu và Whisper do setup.sh tải từ nguồn gốc, không nằm trong gói.
- Pop/whoosh được tổng hợp bằng FFmpeg khi thiếu file SFX riêng của job.
- Skill itinerary-overlay-video: HyperFrames CLI (`hyperframes@0.8.181`) và GSAP 3.14.2 tải qua npx/CDN khi render; Roboto tải từ Google Fonts. Không kèm logo hay video: người dùng tự cung cấp source sạch chữ và logo của mình. Đường viền bản đồ Việt Nam, các đảo, Hoàng Sa và Trường Sa là toạ độ gần đúng do skill tự vẽ, chỉ để minh hoạ tuyến đi.
