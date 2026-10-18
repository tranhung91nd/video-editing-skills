# Phong cách của video mẫu

Nguồn: video Facebook của Mai Kim Quý, 4 phút 40, dọc, 30 fps; bản tải về (720p) và ảnh phân tích nằm ở `Skill Edit Video/mau-moi/`. Chỉ học cách dựng; không dùng lại hình, lời hay tư liệu của video này.

Mọi thông số dưới đây đo trực tiếp trên khung hình mẫu rồi quy về khung 1080×1920, và đã được dựng sẵn trong `template/src/index.tsx`. Font được xác định bằng cách vẽ chồng từng font ứng viên lên chữ cắt từ mẫu và chấm độ trùng khít, không chọn bằng mắt.

## Font

| Chỗ dùng | Font | Ghi chú |
|---|---|---|
| Từ khoá vàng, tiêu đề thẻ, số thứ tự, số chương | **Anton** | Trùng khít 88–98% trên 19 mẫu chữ. Oswald, Barlow Condensed, League Gothic, Bebas Neue đều lệch rõ (58–85%). |
| Dòng nghiêng nhỏ trên/dưới từ khoá | **Montserrat SemiBold Italic** (600) | |
| Phụ đề hai dòng | **Montserrat Bold** (700) | |
| Nhãn, tên, số liệu trên thẻ | Montserrat 600/700/800 | |

Từ khoá Anton **bị kéo giãn ngang 1,245 lần**; đây là lý do chữ trông bè hơn Anton thường. Khi chữ giãn vượt 860px thì giảm độ giãn cho vừa. Tên thương hiệu và nhãn dưới cửa sổ nổi giãn tới hết 860px (mẫu giãn tới 1,9 lần).

## Từ khoá vàng

- Cỡ chữ: thường 112px; nhấn mạnh 136px; từ rất ngắn, rất quan trọng 170px; kiểu phủ định 102px.
- Màu chuyển ngang đối xứng: vàng đậm `#FEDA3C` ở hai mép, `#FCE56C` ở 15%, `#F9EA8B` ở 30%, vàng nhạt `#F8ED96` ở giữa. Không chuyển theo chiều dọc.
- **Đổ sáng**: quầng cam `#FF8C00` nhoè 15px, độ đậm 0,69, cộng một viền tối mỏng sát mép chữ (đen nhoè 6px, 0,6) để chữ tách khỏi quầng. Quầng tắt hẳn ở khoảng 30px cách mép chữ.
- Xuất hiện trong 18 khung hình: hiện từ nhoè 10px và mờ, phóng từ 83% vọt lên 113% ở khung thứ 6 rồi co đều về 100% ở khung thứ 17. Trong lúc đó quầng sáng nở rộng thêm và 7 đốm sao trắng bốn cánh lấp lánh quanh chữ, tắt hết trước khung 18.
- Biến mất: mờ dần trong 4 khung hình, không đổi cỡ.
- Vị trí: mẫu neo theo **đỉnh phần mực** của chữ (kể cả dấu) ở y=1129 (cỡ thường) hoặc 1117 (cỡ lớn), nên từ khoá không dấu nằm cao hơn từ khoá có dấu.

## Dòng nhỏ và số chương

- Dòng trên: nghiêng trắng 58px, đường chân chữ y=1094 (1082 với cỡ lớn), hiện trước từ khoá 1 khung hình.
- Dòng dưới: nghiêng trắng 55,5px, y=1314 (1326), hiện sau từ khoá 3 khung hình; tự lùi xuống nếu từ khoá có dấu nặng.
- Số chương: Anton 660px giãn 1,22 lần, trắng độ đậm 0,325, đáy ở y=1533, nằm sau khối chữ.

## Phụ đề hai dòng

- Montserrat Bold 48,6px; dòng 1 trắng (y=1173), dòng 2 vàng nhạt `#F7ED92` (y=1239). Tâm khối ở 62% chiều cao khung.
- **Gõ từng ký tự** tại đúng vị trí cuối cùng, khoảng 23 ký tự mỗi giây, có con trỏ là vạch dọc mảnh sau ký tự vừa gõ. Dòng 2 bắt đầu khi dòng 1 còn 3 ký tự. Gõ xong thì con trỏ tắt.

## Nền video

Mẫu dùng lớp phủ đen tăng dần: trong suốt ở 45% chiều cao, 0,33 ở 56%, 0,55 ở 62,5%, 0,82 ở 70%, đen hẳn từ 79%. Khuôn mặt nằm ở nửa trên. Template dựng kiểu này khi `shade` là `"full"`.

Mặc định của template khác mẫu ở điểm này: người dùng thấy khoảng đen phía dưới thừa, nên `shade` mặc định là `"soft"`, chỉ làm tối một dải sau chữ (đậm nhất 0,62 ở 61–69% chiều cao) rồi nhạt dần về 0,3 ở đáy.

## Các khối khác

- **Kêu gọi cuối**: dòng nghiêng in hoa 59px, từ khoá, và mũi tên đỏ `#FE5130` chỉ xuống (rộng 366, cao 201, nét 54), đứng yên, hiện sau từ khoá 6 khung hình.
- **Tên thương hiệu**: dòng nghiêng dẫn, 1–3 dòng Anton 133px giãn hết bề rộng, thanh vàng nhạt 888×72 chứa chữ nghiêng đen.
- **Phủ định**: từ khoá nhỏ ở trên, dòng đầu nghiêng 73px, các dòng sau 58px, hiện lần lượt.
- **Cửa sổ nổi**: 720×405 tại (180, 1050), bo 15px, viền trắng mảnh; chữ dời xuống dưới cửa sổ; từ khoá thành nhãn Anton 86px giãn hết bề rộng.

## Thẻ toàn màn hình

Thẻ vào và ra bằng mờ dần 6 khung hình; các mục hiện đúng lúc lời nói nhắc tới.

- **Thẻ tối**: nền `#0C0E12` ánh xanh ở góc trên trái và ánh nâu ấm ở mép phải. Chữ mờ khổng lồ Anton 216px màu `#1B1D23` phía trên, vạch vàng kim ngắn bên trái, nhãn nhỏ xám `#B6B8BD` bên phải. Tiêu đề Anton 92–145px không giãn: dòng đầu trắng ngà `#F8F8F0`, dòng cuối vàng kim `#F4E1A1` (màu phẳng).
  - Hàng trong ô: ô bo 20px nền `#1D201F` viền vàng xám, số và nhãn Anton màu chuyển vàng, ghi chú nghiêng trắng.
  - Ảnh + hàng kẻ: ảnh 888×498 bo 26px, bên dưới là các hàng số nhỏ vàng kem `#EBDFAB` + nhãn Anton trắng, ngăn bằng đường kẻ mảnh.
  - Giấy kem: ảnh dọc nghiêng 2,5° bên phải, tờ giấy kem `#EEEADB` nghiêng −3° đè lên bên trái, số Anton màu đồng `#A8873A`, nhãn Montserrat đậm.
  - Chồng thẻ giấy: ba thẻ kem xếp lệch, xoay −7°, 5°, 0°, mỗi thẻ có nhãn đen nhỏ, tiêu đề và vài dòng.
  - Các bước so le: ảnh trái/phải xen kẽ, bên kia là số Anton vàng kim, nhãn trắng, ghi chú xám.
- **So sánh nền xám sáng** (không tiêu đề): khung nhỏ trái, khung lớn phải, nhãn trong ô đen đặt trên mép khung, ô chữ đen 921×269 phía dưới chứa dòng nghiêng và từ khoá vàng.
- **So sánh nền kem** `#EEEBE8` (có tiêu đề): tiêu đề và nhãn chữ trơn màu tối, dòng chân trang xám.
- **Bằng chứng**: nền `#06080E`, tên trắng, ảnh trong khung bo viền trắng, số liệu Montserrat ExtraBold 92px màu kem `#ECE7A0`, dòng chú thích trắng.

## Cấu trúc nội dung và nhịp

| Mốc | Phần | Cách dựng |
|---|---|---|
| 0–13s | Hook: cho xem kết quả ngay | Người nói 2 giây, rồi thẻ so sánh trước/sau với ô chữ đổi nhiều lần |
| 13–48s | Giới thiệu, nỗi đau | Thẻ danh sách, khối tên thương hiệu |
| 48–224s | Các phần đánh số | Mỗi phần mở bằng số chương + từ khoá, rồi phụ đề, và một thẻ hoặc cảnh chèn |
| 224–260s | Bằng chứng | Chuỗi thẻ bằng chứng 2–3 giây mỗi người |
| 260–280s | Cam kết, kêu gọi | Kiểu phủ định, từ khoá, mũi tên chỉ link |

- Lời nói liền mạch, không có khoảng lặng trên 0,25 giây.
- Chữ đổi theo từng câu, 2–4 giây một lần; giữa hai cụm chữ có khoảng 0,3 giây chỉ thấy người nói.
- Khoảng 20 giây có một thẻ toàn màn hình hoặc cảnh chèn, mỗi lần 3–10 giây.
- 30 giây đầu của mẫu (cảnh ngoài trời) dùng một biến thể: Anton không giãn, nhỏ hơn, không quầng sáng. Template không dựng biến thể này.

## Âm thanh

Lời nói là chính. Lời trong video nhắc có sound effect đi cùng hiệu ứng. Chưa nghe trực tiếp được nên chưa xác nhận video có nhạc nền hay không.
