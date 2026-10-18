# Cấu trúc `edit.json`

Đường dẫn file tính từ `job/media/`. Thời gian (`t`, `end`, `at`) là giây của **video gốc**; riêng `start` trong media là giây bắt đầu của chính clip chèn.

```json
{
  "video": "raw.mp4",
  "cuts": [{"start": 0.12, "end": 8.4}, {"start": 9.1, "end": 20.3}],
  "zoom": 1.08,
  "sfx": true,
  "music": "assets/music.mp3",
  "musicVolume": 0.08,
  "captions": [],
  "inserts": []
}
```

- `cuts`: các đoạn giữ lại, theo thứ tự. Đoạn chẵn/lẻ xen kẽ phóng `zoom` để điểm cắt trông như đổi cỡ cảnh. Đặt `zoom: 1` nếu mặt đã sát khung.
- `shade`: bỏ trống (mặc định `"soft"`) thì chỉ có một dải tối nhẹ sau chữ, phần dưới video vẫn thấy rõ. `"full"` làm đen hẳn phần dưới như video mẫu; chỉ dùng khi phần dưới khung hình không có gì đáng xem hoặc người dùng muốn giống mẫu.
- Phần tử có `t` rơi vào đoạn đã cắt sẽ bám vào đầu đoạn giữ kế tiếp.
- Vị trí, cỡ chữ, màu và chuyển động đã cố định theo mẫu; kế hoạch chỉ quyết định nội dung và thời điểm.

## captions

| type | Trường | Dùng khi |
|---|---|---|
| `hero` | `main`, `top?`, `bottom?`, `number?`, `size?`, `raw?` | Ý chính: từ khoá vàng có quầng sáng. |
| `sub` | `line1`, `line2?` | Câu chuyển tiếp: gõ từng ký tự, dòng 1 trắng, dòng 2 vàng nhạt. |
| `brand` | `lines` (1–3 dòng), `top?`, `bar?` | Tên sản phẩm, chương trình, dịch vụ: các dòng giãn hết bề rộng, thanh vàng bên dưới. |
| `cta` | `main`, `top?` | Câu kêu gọi cuối, có mũi tên đỏ chỉ xuống. |

Chi tiết `hero`:

- `main` tự in hoa và tự giãn. Giữ 1–4 từ: tới khoảng 13 ký tự (tính cả dấu cách) thì chữ giãn đủ 1,245 lần như mẫu, 14–19 ký tự bị ép hẹp dần, từ 20 ký tự thì chữ nhỏ lại.
- `size`: bỏ trống cho cỡ thường; `"lg"` cho từ khoá mở phần hoặc ý quan trọng (tối đa khoảng 11 ký tự); `"xl"` cho một hai từ then chốt của cả video (tối đa khoảng 9 ký tự). Mỗi video chỉ nên có một hai chỗ `xl`.
- `raw: true` giữ nguyên chữ hoa/thường (tên riêng như tên phần mềm).
- `number`: số chương lớn mờ phía sau, dùng khi mở một phần đánh số.
- `bottom` là mảng từ 2 dòng trở lên sẽ thành kiểu phủ định/liệt kê: từ khoá nhỏ ở trên, các dòng hiện lần lượt bên dưới (`top` bị bỏ qua).
- `hero` đặt trong lúc có `pip` sẽ thành nhãn giãn hết bề rộng dưới cửa sổ (chỉ dùng `main`).

`sub`: mỗi dòng tối đa khoảng 28 ký tự. Gõ hết hai dòng tổng 40 ký tự mất khoảng 1,6 giây, nên phụ đề cần hiện ít nhất 2,2 giây; câu nói ngắn hơn thế thì viết phụ đề ngắn lại.

```json
{"type": "hero", "t": 12.0, "end": 14.6, "top": "bước đầu tiên", "main": "Chọn đúng khách", "bottom": "trước khi chạy quảng cáo", "number": 1, "size": "lg"}
{"type": "hero", "t": 40.2, "end": 43.0, "main": "Không", "bottom": ["cần thuê người", "cần biết kỹ thuật"]}
{"type": "sub", "t": 15.0, "end": 18.0, "line1": "Mỗi tuần chỉ cần quay", "line2": "một buổi là đủ"}
{"type": "brand", "t": 20.0, "end": 24.0, "top": "dịch vụ", "lines": ["Edit video", "trọn gói"], "bar": "quay xong gửi là có video"}
{"type": "cta", "t": 55.0, "end": 58.0, "top": "Nhắn tin ngay", "main": "Link bên dưới"}
```

## inserts

Media là `"đường/dẫn"` hoặc `{"src": "...", "start"?: giây, "label"?: "...", "wide"?: true}`; đuôi mp4/mov/webm phát như video tắt tiếng, còn lại là ảnh. Ảnh bị cắt cho vừa khung (cover).

### `card`: thẻ tối toàn màn hình

Trường chung: `title` (1–2 dòng; dòng cuối vàng kim), `ghost?` (một từ tiếng Anh ngắn làm chữ mờ khổng lồ), `tag?` (nhãn nhỏ góc phải), `top?` (dòng nghiêng trên tiêu đề), `items?`, `media?`, `lines?` (2–3 dòng chữ gần đáy, dòng cuối vàng kim), `footer?` (một từ khoá vàng kim gần đáy).

Mỗi mục trong `items`: `label`, `note?`, `at?` (mốc giây lời nói đọc tới mục đó; bỏ trống thì hiện đều nhau).

| `layout` | Cần | Hình thức |
|---|---|---|
| `rows` (mặc định), không `media` | 2–4 mục | Mỗi mục một ô bo viền, số + nhãn vàng, `note` nghiêng bên dưới |
| `rows`, không `media`, 5–7 mục | chỉ `label` | Tự chuyển sang hàng kẻ mảnh (số nhỏ + nhãn trắng), giãn dòng theo số mục; `note` bị bỏ qua |
| `rows` có `media` | ảnh ngang + 2–3 mục | Ảnh lớn phía trên, các hàng kẻ mảnh bên dưới |
| `paper` | ảnh dọc + 2–3 mục, `listTitle?` | Ảnh nghiêng bên phải, tờ giấy kem liệt kê đè bên trái |
| `stack` | 2–3 mục có `lines` (mảng), `tag?` từng mục | Ba thẻ giấy kem xếp chồng lệch |
| `steps` | 3 mục, mỗi mục có `media` | Ảnh trái/phải so le với số, nhãn, ghi chú |

```json
{"type": "card", "t": 30.0, "end": 36.5, "ghost": "Process", "tag": "Quy trình", "title": ["Ba việc", "mỗi tuần"],
 "items": [{"label": "Quay", "note": "một buổi", "at": 30.6}, {"label": "Gửi", "note": "video thô", "at": 32.4}, {"label": "Đăng", "note": "đều mỗi ngày", "at": 34.5}]}
{"type": "card", "t": 60.0, "end": 66.0, "layout": "paper", "ghost": "Result", "title": ["Kết quả", "sau 30 ngày"],
 "media": "assets/khach.jpg", "listTitle": "Thay đổi", "items": [{"label": "Lượt xem"}, {"label": "Tin nhắn"}, {"label": "Đơn hàng"}], "footer": "Đo được"}
```

### `compare`: so sánh trước/sau

`left`, `right` là media có `label`. Hai kiểu:

- Không có `title`: nền xám sáng, nhãn trong ô đen, kèm `pills` [`t`, `top?`, `main`] là ô chữ đen phía dưới đổi nội dung theo mốc giây.
- Có `title`: nền kem, nhãn chữ trơn, `footer?` là dòng chú thích xám. `pills` bị bỏ qua.

Muốn cho xem chính video đang dựng ở khung "sau": render một lượt, chép file xuất vào `media/assets/`, trỏ `right.src` tới đó rồi render lại.

### `proof`: bằng chứng

`name?`, `media` (1–2 media; thêm `"wide": true` cho ảnh ngang), `stat`, `note?`. Chỉ dùng tư liệu và số liệu thật.

### `broll` và `pip`

- `broll`: `src`, `start?`. Cảnh chèn phủ kín khung, nằm dưới lớp phủ tối nên chữ vẫn hiện bên trên.
- `pip`: `src`, `start?`, `pos?`, `focus?`. Cửa sổ nổi 16:9.
  - `"pos": "top"`: đặt ở khoảng trống phía trên đầu người nói (864×486, từ y=100 tới 586). Chữ giữ nguyên vị trí thường. **Ưu tiên kiểu này** khi phía trên đầu còn trống ít nhất khoảng 600px, để ảnh và video chèn không che người nói.
  - Bỏ trống `pos`: cửa sổ nằm ở nửa dưới như mẫu; `sub` và `hero` trong lúc đó tự dời xuống dưới cửa sổ.
  - `focus` (ví dụ `"50% 38%"`): chọn vùng giữ lại khi cắt video dọc vào khung ngang; xem thử vài khung cắt để mặt người không bị mất.
  - Các `pip` cùng vị trí nối tiếp nhau (mốc `end` trùng `t` kế tiếp) chuyển cảnh liền, không nhấp nháy.

```json
{"type": "compare", "t": 3.0, "end": 9.0, "left": {"src": "raw.mp4", "start": 5, "label": "Trước"}, "right": {"src": "assets/edited.mp4", "start": 5, "label": "Sau"},
 "pills": [{"t": 3.0, "top": "Cùng một video", "main": "Khác hẳn"}, {"t": 6.0, "top": "Thời gian dựng", "main": "15 phút"}]}
{"type": "proof", "t": 70.0, "end": 73.0, "name": "Tên khách hàng", "media": [{"src": "assets/trang.png", "label": "Fanpage"}], "stat": "Số liệu thật", "note": "trong bao lâu"}
{"type": "pip", "t": 44.0, "end": 50.0, "src": "assets/quay-man-hinh.mp4", "start": 4}
```
