"""Bullet — Viên đạn trong game.

Mỗi viên đạn:
- Bay thẳng theo góc bắn
- Tự hủy khi chạm tường (KHÔNG chạm barrel — đạn xuyên barrel)
- Tự hủy khi bay quá 600px
- Gây 25 sát thương khi chạm tank
"""

import pygame
import math
from src.core.settings import (
    BULLET_SPEED, BULLET_DAMAGE, BULLET_MAX_DISTANCE,
    BULLET_RADIUS, BULLET_IMAGES_DIR
)


class Bullet:
    """Một viên đạn đang bay.

    Thuộc tính:
        x, y (float): Vị trí hiện tại
        angle (float): Hướng bay (radian)
        speed (float): Tốc độ bay (pixel/giây)
        damage (int): Sát thương khi trúng
        owner: Tank đã bắn viên đạn này (để không tự bắn mình)
        active (bool): Còn hoạt động hay đã hủy
    """

    def __init__(self, x, y, angle, speed=BULLET_SPEED, damage=BULLET_DAMAGE, owner=None):
        self.x = float(x)
        self.y = float(y)
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.owner = owner
        self.active = True
        self.distance_traveled = 0.0
        self.radius = BULLET_RADIUS

        # Vận tốc (tính 1 lần, dùng lại mỗi frame)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        # Tải ảnh đạn
        self.image = self._tai_hinh_anh()

    def _tai_hinh_anh(self):
        """Tải ảnh đạn từ file tương ứng màu của xe tăng bắn. Fallback: vẽ hình tròn vàng."""
        color = "Green"
        if self.owner and hasattr(self.owner, 'color'):
            c = self.owner.color.capitalize()
            # Xử lý màu black không có đạn black
            if c == "Black":
                color = "Silver"
            else:
                color = c

        try:
            img = pygame.image.load(f"{BULLET_IMAGES_DIR}/bullet{color}_outline.png").convert_alpha()
            # Ảnh gốc có thể hơi dài, xoay đạn theo hướng bắn
            img = pygame.transform.scale(img, (12, 16))
            img = pygame.transform.rotate(img, -math.degrees(self.angle) - 90)
            return img
        except (pygame.error, FileNotFoundError):
            s = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 200, 0), (6, 6), 5)
            pygame.draw.circle(s, (255, 255, 255), (6, 6), 2)
            return s

    def update(self, dt, map_data=None):
        """Cập nhật vị trí đạn mỗi frame.

        - Di chuyển theo vận tốc
        - Kiểm tra bay quá xa → hủy
        - Kiểm tra va chạm tường → hủy (barrel KHÔNG chặn đạn)
        """
        if not self.active:
            return

        # Di chuyển
        dx = self.vx * dt
        dy = self.vy * dt
        self.x += dx
        self.y += dy
        self.distance_traveled += math.sqrt(dx * dx + dy * dy)

        # Tự hủy nếu bay quá xa
        if self.distance_traveled > BULLET_MAX_DISTANCE:
            self.active = False
            return

        # Va chạm tường (is_wall_at KHÔNG tính barrel → đạn xuyên barrel)
        if map_data:
            from src.world.collision import Collision
            if Collision.bullet_vs_map(self.x, self.y, map_data):
                self.active = False

    def check_collision_with_tank(self, tank):
        """Kiểm tra đạn có trúng tank không.

        Trả về True nếu:
        - Đạn đang hoạt động
        - Tank còn sống
        - Tank KHÔNG phải chủ nhân đạn
        - Khoảng cách < bán kính va chạm
        """
        if not self.active or not tank.is_alive():
            return False
        if tank is self.owner:
            return False
        dist = math.sqrt((self.x - tank.x)**2 + (self.y - tank.y)**2)
        return dist < self.radius + max(tank.width, tank.height) // 2

    def draw(self, screen, cam_x=0, cam_y=0):
        """Vẽ đạn lên màn hình."""
        if not self.active:
            return
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        screen.blit(self.image, self.image.get_rect(center=(sx, sy)))
