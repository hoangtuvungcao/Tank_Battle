# HƯỚNG DẪN TẠO BẢN ĐỒ (MAP CREATION)

Bản đồ trong Tank Battle được lưu dưới dạng file văn bản `.txt` trong thư mục `maps/`. Bạn có thể dễ dàng tự tạo bản đồ mới bằng bất kỳ trình soạn thảo văn bản nào (Notepad, VS Code).

## 1. CÁC KÝ HIỆU TRÊN BẢN ĐỒ

| Ký hiệu | Ý nghĩa | Thuộc tính |
| :---: | :--- | :--- |
| `#` | Tường gạch | Chặn xe tăng & chặn đạn |
| `S` | Bao cát | Chặn xe tăng & chặn đạn |
| `B` | Thùng phuy | Chặn xe tăng, **nổ lan khi bị bắn** |
| `.` | Đất nâu | Đi qua bình thường |
| `G` | Thảm cỏ | Đi qua bình thường |
| `A` | Cát vàng | Đi qua bình thường |
| `l` | Bụi cây nhỏ | Đi xuyên qua, **Tàng hình (Stealth)** |
| `L` | Cây lớn | Đi xuyên qua, **Tàng hình (Stealth)** |
| `T` | Người chơi | Điểm xuất phát của bạn (trên nền đất) |
| `E` | Kẻ địch | Điểm xuất phát của Bot (trên nền đất) |

## 2. QUY TẮC THIẾT KẾ

1. **Khung bao**: Luôn bao quanh bản đồ bằng ký tự `#` hoặc `S` để ngăn xe tăng đi ra ngoài biên giới thế giới.
2. **Kích thước**: Kích thước mỗi ô là 64x64 pixel. Bản đồ tiêu chuẩn thường là 20x15 ô, nhưng game hỗ trợ lên đến 50x50 ô (có camera cuộn).
3. **Vị trí Spawn**:
   - Chỉ nên có **duy nhất một chữ `T`** trên bản đồ.
   - Có thể có nhiều chữ `E` tùy theo độ khó bạn muốn tạo ra.

## 3. VÍ DỤ MỘT BẢN ĐỒ ĐƠN GIẢN

```text
####################
#T.................#
#....B.............#
#..........l.......#
#...####.......E...#
#...#..#...........#
#...####...........#
#..........S.......#
#...l..............#
####################
```

---
*Sau khi tạo file xong, hãy đặt tên là `levelX.txt` (với X là số màn) và lưu vào thư mục `maps/` để game tự động nhận diện.*
