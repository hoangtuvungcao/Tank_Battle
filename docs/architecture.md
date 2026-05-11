# TÀI LIỆU KIẾN TRÚC MÃ NGUỒN (TANK BATTLE V2.0)

Tài liệu này giải thích chi tiết cấu trúc mã nguồn, luồng hoạt động và các thuật toán cốt lõi của game để bạn có thể dễ dàng hiểu và tùy biến mọi dòng code.

## 1. VÒNG LẶP GAME (Core Game Loop)
**Tệp tin:** `src/core/game.py`
- Đây là trái tim của trò chơi. Hàm `Game.run()` chứa vòng lặp `while True`.
- Ở mỗi khung hình (frame), vòng lặp sẽ thực hiện 3 bước:
  1. Xử lý Input (Phím/Chuột) qua `event_handler`.
  2. Tính toán Logic Game (Di chuyển, AI, Đạn bay, Va chạm).
  3. Vẽ mọi thứ lên màn hình (Draw).
- Mọi logic va chạm đạn với xe tăng, phát âm thanh vụ nổ, và sát thương nổ lan của thùng phuy (Splash Damage) đều nằm trong hàm `_update_playing()`.

## 2. HỆ THỐNG VẬT LÝ VÀ VA CHẠM (Collision System)
**Tệp tin:** `src/world/collision.py`
Thuật toán va chạm hoạt động theo cơ chế **Sliding Collision** (Va chạm trượt):
- Khi một xe tăng di chuyển, hệ thống sẽ kiểm tra xem tọa độ mới có đè lên một vật cản cứng (`is_solid=True`) hay không.
- Nếu có, thay vì dừng xe tăng lại hoàn toàn (gây giật lag/kẹt tường), code sẽ phân tách trục X và trục Y để thử nghiệm độc lập.
- Điều này cho phép xe tăng tự động "trượt" dọc theo bề mặt bức tường nếu bị đẩy vào góc chéo.

## 3. TRÍ TUỆ NHÂN TẠO (Artificial Intelligence)
**Tệp tin:** `src/ai/enemy.py` và `src/ai/behavior.py`
AI hoạt động theo mô hình Máy Trạng Thái (State Machine):
- `PATROL`: Đi dạo ngẫu nhiên và liên tục xoay nòng súng dò tìm.
- `CHASE`: Khi phát hiện bạn, AI gọi thuật toán A* (A-Star) trong `behavior.py` để tìm đường ngắn nhất luồn lách qua các chướng ngại vật để tiếp cận bạn.
- `ATTACK`: Khi vào tầm ngắm, AI sẽ vừa ngắm bắn vừa di chuyển theo hình chữ chi (Strafe).
- `DODGE` (Né đạn): Bất cứ khi nào lượng máu của AI giảm sút so với khung hình trước (`self.health < self.last_health`), AI lập tức kích hoạt Dodge, bẻ lái 90 độ so với hướng của bạn để né loạt đạn tiếp theo.

## 4. HỆ THỐNG TÀNG HÌNH (Stealth) VÀ ĐỊA HÌNH
**Tệp tin:** `src/entities/player.py` và `src/world/tile.py`
- Bất cứ khi nào trọng tâm của xe tăng đè lên một Tile có `loai` là `tree_small` hoặc `tree_large`, biến `self.in_stealth` sẽ trở thành True.
- Khi tàng hình, AI sẽ bị mù tạm thời (giảm tầm nhìn xuống còn 80 pixel). Đồng thời, hàm `draw()` của xe tăng sẽ hạ độ mờ (Alpha) xuống để tạo hiệu ứng trong suốt trên màn hình.

## 5. QUẢN LÝ ÂM THANH (Sound Manager)
**Tệp tin:** `src/core/sound_manager.py`
- Để tránh việc đọc file từ ổ cứng liên tục gây sụt giảm FPS, lớp `SoundManager` sử dụng cơ chế Cache (`self._sfx_cache`). File âm thanh chỉ được load đúng 1 lần vào RAM.
- Thuộc tính `self.individual_volumes` chứa bảng tra cứu (Lookup table) cho phép nhân hệ số âm lượng riêng biệt cho từng loại âm thanh (VD: giảm tiếng nút bấm nhưng giữ nguyên tiếng nổ).

## 6. HỆ THỐNG GIAO DIỆN (UI & HUD)
**Tệp tin:** `src/ui/hud.py`
- Minimap: Được tính toán động (Dynamic Scaling) thông qua tỷ lệ `MINIMAP_SIZE / map_width`. Điều này đảm bảo dù bản đồ ở Level 1 (25x15) hay Level 10 (43x33) thì Minimap luôn được render vừa khít với viền trắng bao quanh, không thừa bất kỳ mảng đen nào.
- Kill Feed: Sử dụng Queue (hàng đợi) với bộ đếm thời gian (timer). Khi một thông báo hiển thị quá 3 giây, độ mờ (Alpha) của chữ sẽ giảm dần cho đến khi biến mất hoàn toàn. Mọi xe tăng địch khi sinh ra đều được gán ngẫu nhiên một cái tên từ mảng `ENEMY_NAMES` để thông báo lên Kill Feed.

---
Mọi hàm và phương thức trong mã nguồn đều đã được tôi viết **Docstring (chuỗi chú thích)** bằng tiếng Việt giải thích rõ đầu vào (Tham số) và đầu ra (Trả về) trực tiếp ngay phía trên dòng code đó. Bạn có thể mở bất kỳ file nào lên để đọc trực tiếp.
