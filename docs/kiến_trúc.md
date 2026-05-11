# Kiến trúc hệ thống Tank Battle v2.0

## Tổng quan

Game được chia thành 5 module chính, mỗi module đảm nhận một nhiệm vụ riêng biệt.

## Sơ đồ module

```
main.py
  └── Game (src/core/game.py)
        ├── StateManager   — Quản lý trạng thái (MENU → PLAYING → PAUSED → GAME_OVER)
        ├── EventHandler   — Đọc bàn phím + chuột mỗi frame
        ├── SoundManager   — Phát nhạc nền và hiệu ứng âm thanh
        │
        ├── GameMap        — Tải bản đồ từ file text, quản lý lưới tile
        │   ├── Tile       — Một ô trên bản đồ (đất, tường, cây, thùng phuy...)
        │   └── Collision  — Kiểm tra va chạm tank-tường, đạn-tường
        │
        ├── Camera         — Theo dõi player, tính offset vẽ
        │
        ├── Player (kế thừa Tank)   — Xe tăng người chơi, xử lý WASD + chuột
        ├── Enemy  (kế thừa Tank)   — Xe tăng địch, AI tự động
        │   └── TrangThaiAI         — 5 trạng thái: PATROL, CHASE, ATTACK, INVESTIGATE, FLEE
        │
        ├── BulletManager  — Quản lý tất cả đạn đang bay
        │   └── Bullet     — Một viên đạn, tự bay và kiểm tra va chạm
        │
        └── UI
            ├── MainMenu          — Menu chính (gradient background, animation)
            ├── SettingsMenu      — Cài đặt (âm lượng, độ khó, fullscreen)
            ├── TankSelectMenu    — Chọn màu xe tăng
            ├── HUD               — Thanh máu, điểm số, minimap, kill feed
            ├── LevelTransition   — Hiệu ứng chuyển màn
            └── ParticleSystem    — Hiệu ứng nổ và chớp lửa
```

## Luồng chạy chính

1. `main.py` → khởi tạo `Game` → gọi `game.run()`
2. `run()` chạy vòng lặp: đọc input → cập nhật → vẽ → flip display
3. Dựa trên trạng thái hiện tại, gọi hàm cập nhật và vẽ tương ứng

## Hệ thống va chạm

- **Tank vs tường**: Kiểm tra 4 góc rect của tank, dùng `is_solid_at()` (bao gồm barrel)
- **Đạn vs tường**: Kiểm tra tâm đạn, dùng `is_wall_at()` (KHÔNG bao gồm barrel)
- **Đạn vs barrel**: Xử lý riêng trong `game.py` — đạn phá hủy barrel thay vì bị chặn
- **Đạn vs tank**: Kiểm tra rect overlap, gây damage

## Hệ thống AI

AI địch sử dụng máy trạng thái (State Machine) với 5 trạng thái:

| Trạng thái | Điều kiện chuyển vào | Hành vi |
|------------|---------------------|---------|
| PATROL | Không thấy player, không bị tấn công | Di chuyển ngẫu nhiên, quét nòng súng |
| CHASE | Thấy player ngoài tầm bắn | Đuổi theo + đi vòng (flank) |
| ATTACK | Thấy player trong tầm bắn | Bắn + strafe + giữ khoảng cách |
| INVESTIGATE | Mất dấu player hoặc bị bắn từ stealth | Tìm kiếm theo hình quạt |
| FLEE | Máu dưới 30% | Chạy xa player |

### Phát hiện bị tấn công
AI so sánh máu hiện tại với frame trước. Nếu máu giảm → biết bị bắn → chuyển sang INVESTIGATE hoặc ATTACK, đồng thời dodge sang ngang.

### Stealth
Khi player ở trong `tree_small`, AI không thấy player (chuyển PATROL). Nhưng nếu AI bị bắn, nó sẽ bỏ qua stealth và xông thẳng về phía attacker.

## Ký hiệu bản đồ

File bản đồ nằm trong `maps/levelN.txt`. Mỗi ký tự = 1 tile 64×64 pixel.

Xem bảng ký hiệu đầy đủ trong README.md.
