"""BulletManager — Quản lý tất cả đạn đang bay.

Nhiệm vụ:
- Tạo đạn mới khi tank bắn
- Cập nhật vị trí mỗi frame
- Kiểm tra va chạm đạn vs tank
- Xóa đạn đã hết hoạt động
- Vẽ tất cả đạn
"""

from src.entities.bullet import Bullet


class BulletManager:
    """Quản lý toàn bộ đạn trong game.

    Sử dụng:
        bm = BulletManager()
        bm.add_bullet(bullet_data)      # Thêm đạn mới
        bm.update_all(dt, tanks, map)    # Cập nhật + kiểm tra va chạm
        bm.draw_all(screen, cx, cy)      # Vẽ tất cả
    """

    def __init__(self):
        self.bullets = []  # Danh sách đạn đang bay

    def add_bullet(self, bullet_data):
        """Tạo viên đạn mới từ data dict (do Tank.shoot() trả về).

        Tham số:
            bullet_data: dict chứa x, y, angle, speed, damage, owner
                         Nếu None thì bỏ qua (tank bắn thất bại)
        """
        if bullet_data is None:
            return
        bullet = Bullet(
            x=bullet_data["x"],
            y=bullet_data["y"],
            angle=bullet_data["angle"],
            speed=bullet_data.get("speed", 400),
            damage=bullet_data.get("damage", 25),
            owner=bullet_data.get("owner")
        )
        self.bullets.append(bullet)

    def update_all(self, dt, tanks, map_data):
        """Cập nhật tất cả đạn — di chuyển + kiểm tra va chạm tank.

        Tham số:
            dt: Delta time (giây)
            tanks: Danh sách tank (player + enemies) để kiểm tra va chạm
            map_data: Bản đồ để kiểm tra va chạm tường
        """
        for bullet in self.bullets:
            if not bullet.active:
                continue

            # Di chuyển đạn + kiểm tra tường
            bullet.update(dt, map_data)
            if not bullet.active:
                continue

            # Kiểm tra va chạm với từng tank
            for tank in tanks:
                if bullet.check_collision_with_tank(tank):
                    tank.take_damage(bullet.damage)
                    bullet.active = False
                    break

        # Xóa đạn đã hết hoạt động
        self.bullets = [b for b in self.bullets if b.active]

    def draw_all(self, screen, cam_x=0, cam_y=0):
        """Vẽ tất cả đạn lên màn hình."""
        for bullet in self.bullets:
            bullet.draw(screen, cam_x, cam_y)

    def clear(self):
        """Xóa tất cả đạn (dùng khi chuyển màn)."""
        self.bullets.clear()

    def get_count(self):
        """Đếm số đạn đang bay."""
        return len(self.bullets)
