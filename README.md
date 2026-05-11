# TANK BATTLE v2.0 - HỒI SINH TỪ TÀN TRO

Game bắn tank top-down 2D chiến thuật hạng nặng được viết bằng Python + Pygame. Phiên bản 2.0 mang đến một trải nghiệm Hardcore tập trung vào kỹ năng di chuyển, điều khiển nòng súng độc lập và tư duy chiến thuật môi trường.

---

## TÍNH NĂNG MỚI TRONG V2.0

### 1. Cơ chế Điều Khiển Hardcore
- Loại bỏ hoàn toàn việc ngắm bắn bằng chuột.
- Nòng súng giờ đây khóa cứng theo thân xe. Bạn phải xoay toàn bộ thân xe (phím A/D) để nhắm bắn, đòi hỏi kỹ năng căn góc và timing cực kỳ chuẩn xác.
- Nhấn SPACE để khai hỏa.

### 2. Trí Tuệ Nhân Tạo (AI) Nâng Cấp
- A* Pathfinding: Kẻ địch biết tự động tìm đường ngắn nhất, lách qua các hành lang và tránh chướng ngại vật để săn lùng bạn.
- Hệ số Thông Minh: AI phản xạ trong chớp mắt (0.3s), tầm nhìn xa hơn và độ chính xác tuyệt đối ở mức độ khó.
- Chiến Thuật Sinh Tồn: AI biết cách tự động lùi lại (Dodge) sang hai bên khi bị bắn trúng.
- Định Danh & Thanh Máu: Mỗi con Bot được gắn tên ngẫu nhiên và có thanh máu hiển thị trực tiếp trên đầu.

### 3. Chiến Thuật Môi Trường & Bản Đồ
- 10 Màn Chơi Tự Tạo: Bản đồ rộng dần theo từng cấp độ, tối đa 43x33 ô.
- Va Chạm Trượt (Sliding Collision): Hệ thống vật lý cho phép xe tăng trượt mượt mà dọc theo các bức tường, loại bỏ hoàn toàn tình trạng kẹt góc.
- Sát Thương Nổ Lan: Thùng phuy là vật phẩm chiến thuật, gây sát thương diện rộng khi phát nổ.
- Tàng Hình (Stealth): Nấp trong bụi rậm hoặc dưới tán cây lớn để hoàn toàn biến mất trước tầm nhìn của AI.

### 4. Hệ Thống Âm Thanh Tuyệt Đỉnh
- Live Preview: Cảm nhận sự thay đổi âm lượng ngay lập tức trong menu cài đặt.
- Dynamic Music: Nhạc nền thay đổi linh hoạt giữa Menu và trận đấu.

---

## HƯỚNG DẪN ĐIỀU KHIỂN

| Phím | Hành động |
| :--- | :--- |
| W | Tiến tới |
| S | Lùi lại |
| A / D | Xoay thân xe sang Trái / Phải |
| SPACE | Bắn đạn |
| ESC | Tạm dừng (Pause) |

Mẹo: Luôn giữ phím W và kết hợp A/D để thực hiện các pha drift lách qua đạn địch.

---

## CÀI ĐẶT & CHẠY GAME

### Yêu cầu hệ thống:
- Python 3.8+
- Pygame 2.5+

### Các bước cài đặt:
1. Clone dự án:
   ```bash
   git clone https://github.com/hoangtuvungcao/Tank_Battle.git
   cd Tank_Battle
   ```
2. Cài đặt thư viện:
   ```bash
   pip install -r requirements.txt
   ```
3. Khởi động trận chiến:
   ```bash
   python main.py
   ```

---

## KIẾN TRÚC MÃ NGUỒN

Tài liệu chi tiết dành cho lập trình viên: [docs/architecture.md](docs/architecture.md)

- src/core/: Quản lý vòng lặp chính, âm thanh và trạng thái.
- src/ai/: Thuật toán tìm đường và máy trạng thái của địch.
- src/entities/: Logic vật lý của xe tăng và đạn.
- src/world/: Hệ thống bản đồ và va chạm trượt.
- src/ui/: Giao diện người dùng, thanh máu và hiệu ứng hạt.

---
*Phát triển bởi nhóm sinh viên đam mê AI và Game Development.*
