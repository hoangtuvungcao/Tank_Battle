"""
Player — Xe tăng do người chơi điều khiển.

Lớp này kế thừa từ lớp Tank và bổ sung các tính năng riêng biệt:
- Xử lý điều khiển từ bàn phím.
- Quản lý hệ thống tàng hình (Stealth) khi đi vào bụi rậm.
- Theo dõi các thống kê chiến đấu như số mạng tiêu diệt, độ chính xác.
"""

import pygame
import math
from src.entities.tank import Tank # Nhập lớp cha
from src.core.settings import (
    PLAYER_HEALTH, PLAYER_SPEED, PLAYER_ROTATION_SPEED,
    PLAYER_TURRET_SPEED, PLAYER_SHOOT_DELAY, TILE_SIZE
)
from src.world.collision import Collision # Hỗ trợ xử lý va chạm tường


class Player(Tank):
    """
    Xe tăng của người chơi — Sử dụng WASD để di chuyển và SPACE để bắn.
    """

    def __init__(self, x=0, y=0, color="green"):
        """
        Khởi tạo người chơi với các chỉ số ưu việt hơn so với kẻ địch.
        """
        # Gọi hàm khởi tạo của lớp Tank với các hằng số riêng cho Player
        super().__init__(x=x, y=y, color=color, health=PLAYER_HEALTH, speed=PLAYER_SPEED)
        
        self.name = "Bạn" # Tên hiển thị của người chơi
        
        # Ghi đè tốc độ xoay từ settings
        self.rotation_speed = PLAYER_ROTATION_SPEED
        self.turret_rotation_speed = PLAYER_TURRET_SPEED
        self.shoot_delay = PLAYER_SHOOT_DELAY

        # Các biến thống kê thành tích (Achievements)
        self.kills = 0       # Số kẻ địch đã tiêu diệt
        self.shots_fired = 0 # Tổng số phát đạn đã bắn
        self.shots_hit = 0   # Số phát đạn trúng mục tiêu

        # Trạng thái tàng hình
        self.in_stealth = False

    def handle_input(self, keys, mouse_pos, dt, map_data, cam_x=0, cam_y=0):
        """
        Xử lý các phím bấm từ người chơi để điều khiển xe tăng.
        """
        # Lưu lại vị trí cũ trước khi di chuyển để dùng nếu bị kẹt tường
        old_x, old_y = self.x, self.y

        # --- XỬ LÝ DI CHUYỂN TRỤC (WASD hoặc Phím mũi tên) ---
        dx, dy = 0.0, 0.0
        if keys.get(pygame.K_w) or keys.get(pygame.K_UP):
            dy -= 1 # Đi lên (trục y âm)
        if keys.get(pygame.K_s) or keys.get(pygame.K_DOWN):
            dy += 1 # Đi xuống (trục y dương)
        if keys.get(pygame.K_a) or keys.get(pygame.K_LEFT):
            dx -= 1 # Sang trái (trục x âm)
        if keys.get(pygame.K_d) or keys.get(pygame.K_RIGHT):
            dx += 1 # Sang phải (trục x dương)
        
        # Nếu có bất kỳ phím di chuyển nào được nhấn
        if dx != 0 or dy != 0:
            # Chuẩn hóa vector để tốc độ đi chéo không bị nhanh hơn đi thẳng
            length = math.sqrt(dx * dx + dy * dy)
            self.x += (dx / length) * self.speed * dt
            self.y += (dy / length) * self.speed * dt
            
            # Tính toán góc hướng xe cần xoay tới dựa trên tổ hợp phím nhấn
            target_angle = math.atan2(dy, dx)
            # Tính độ lệch giữa góc hiện tại và góc mục tiêu
            diff = target_angle - self.angle
            # Chuẩn hóa góc về đoạn [-pi, pi]
            while diff > math.pi: diff -= 2 * math.pi
            while diff < -math.pi: diff += 2 * math.pi
            
            # Cơ chế xoay thân xe mượt mà
            # Nếu góc lệch quá lớn (quay ngoắt 180 độ), ta cho xe xoay tức thì
            if abs(diff) > math.pi / 2:
                self.angle = target_angle
            else:
                # Nếu lệch ít, xoay từ từ theo rotation_speed
                max_rot = math.radians(self.rotation_speed * 1.5) * dt
                if abs(diff) < max_rot:
                    self.angle = target_angle
                else:
                    self.angle += math.copysign(max_rot, diff)
            
            # Cập nhật khung va chạm sau khi dịch chuyển
            self._cap_nhat_rect()

        # Áp dụng thuật toán Va Chạm Trượt nếu va vào vật cản trên bản đồ
        Collision.resolve_tank_wall(self, map_data, old_x, old_y)

        # --- CƠ CHẾ NÒNG SÚNG HARDCORE ---
        # Nòng súng luôn khóa chặt theo hướng của thân xe (không dùng chuột)
        self.turret_angle = self.angle

        # --- CƠ CHẾ TÀNG HÌNH (STEALTH) ---
        # Kiểm tra xem tâm xe tăng có đang nằm trong ô Bụi Cây (TreeSmall hoặc TreeLarge) không
        tile = map_data.get_tile_at(self.x, self.y) if map_data else None
        # Nếu đứng trên cây, người chơi được trạng thái Stealth
        self.in_stealth = (tile is not None and tile.loai in ["tree_small", "tree_large"])

    def handle_shoot(self):
        """
        Khai hỏa và ghi nhận thống kê bắn.
        """
        # Gọi hàm bắn của lớp cha Tank
        data = self.shoot()
        if data:
            # Nếu bắn thành công (không bị cooldown), tăng số đạn đã bắn
            self.shots_fired += 1
        return data

    def add_kill(self):
        """Ghi nhận khi người chơi tiêu diệt được một kẻ địch."""
        self.kills += 1

    def add_hit(self):
        """Ghi nhận khi một viên đạn của người chơi bắn trúng xe tăng địch."""
        self.shots_hit += 1

    def get_stats(self):
        """
        Trả về bảng thống kê thành tích của người chơi để hiển thị lên HUD.
        """
        acc = 0
        if self.shots_fired > 0:
            # Tính tỷ lệ chính xác (%)
            acc = round(self.shots_hit / self.shots_fired * 100, 1)
        return {
            "kills": self.kills,
            "shots_fired": self.shots_fired,
            "shots_hit": self.shots_hit,
            "accuracy": acc
        }

    def draw(self, screen, cam_x=0, cam_y=0):
        """
        Vẽ xe tăng người chơi với hiệu ứng mờ nếu đang tàng hình.
        """
        if not self.alive: return

        # Tính toán tọa độ hiển thị thực tế
        sx = self.x - cam_x
        sy = self.y - cam_y

        # Nếu đang tàng hình (Stealth), đặt độ trong suốt là 120 (khoảng 50%)
        # Nếu không tàng hình, đặt độ mờ tối đa (255)
        alpha = 120 if self.in_stealth else 255

        # --- Vẽ Thân Xe ---
        rotated_body = pygame.transform.rotate(self.body_image, -math.degrees(self.angle))
        if alpha < 255:
            # Tạo bản sao ảnh và áp dụng độ mờ alpha
            rotated_body = rotated_body.copy()
            rotated_body.set_alpha(alpha)
        body_rect = rotated_body.get_rect(center=(int(sx), int(sy)))
        screen.blit(rotated_body, body_rect)

        # --- Vẽ Nòng Súng ---
        rotated_turret = pygame.transform.rotate(self.turret_image, -math.degrees(self.turret_angle))
        if alpha < 255:
            rotated_turret = rotated_turret.copy()
            rotated_turret.set_alpha(alpha)
            
        # Tính toán vị trí nòng súng nhô ra phía trước xe
        offset_dist = 15
        tx = sx + math.cos(self.turret_angle) * offset_dist
        ty = sy + math.sin(self.turret_angle) * offset_dist
        
        turret_rect = rotated_turret.get_rect(center=(int(tx), int(ty)))
        screen.blit(rotated_turret, turret_rect)

    def reset(self, x, y):
        """
        Hồi sinh người chơi (gọi khi bắt đầu màn mới hoặc sau khi chết).
        """
        self.x = x
        self.y = y
        self.angle = 0.0
        self.turret_angle = 0.0
        self.alive = True
        self.health = self.max_health # Hồi đầy máu
        self.shoot_cooldown = 0.0     # Reset thời gian nạp đạn
        self._cap_nhat_rect()
