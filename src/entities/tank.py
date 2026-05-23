"""
Tank — Lớp cơ sở cho tất cả xe tăng trong game.

File này chứa logic quan trọng nhất về việc xe tăng di chuyển như thế nào, 
xoay nòng ra sao, và làm thế nào để vẽ hình ảnh xe lên màn hình một cách chính xác nhất.
"""

import pygame # Thư viện đồ họa
import math   # Thư viện toán học để tính sin, cos (di chuyển theo góc)
# Nhập các thông số cấu hình từ settings
from src.core.settings import (
    TANK_WIDTH, TANK_HEIGHT, TANK_SPEED, TANK_ROTATION_SPEED,
    TURRET_ROTATION_SPEED, TANK_MAX_HEALTH, TANK_SHOOT_DELAY,
    TANK_IMAGES_DIR, BULLET_SPEED, BULLET_DAMAGE, TILE_SIZE
)


class Tank:
    """
    Lớp cha định nghĩa mọi hành vi chung của xe tăng (cả của người chơi và máy).
    """

    def __init__(self, x=0, y=0, color="green", health=100, speed=200.0):
        """
        Khởi tạo các thông số ban đầu cho xe tăng.
        """
        # Lưu trữ vị trí x, y dưới dạng số thực (float) để di chuyển mượt mà hơn
        self.x = float(x)
        self.y = float(y)
        self.color = color # Màu xe (green, blue, beige, black)

        # Góc xoay (đơn vị: radian)
        # Trong toán học và lập trình, góc 0 radian là hướng sang PHẢI (hướng Đông)
        self.angle = 0.0           # Góc xoay của thân xe
        self.turret_angle = 0.0    # Góc xoay của nòng súng độc lập

        # Tốc độ
        self.speed = speed # Tốc độ di chuyển
        self.rotation_speed = TANK_ROTATION_SPEED       # Tốc độ xoay thân xe (độ/giây)
        self.turret_rotation_speed = TURRET_ROTATION_SPEED  # Tốc độ xoay nòng (độ/giây)

        # Thông số sinh mạng
        self.health = health      # Máu hiện tại
        self.max_health = health  # Máu tối đa để vẽ thanh máu
        self.alive = True         # Trạng thái còn sống hay đã nổ
        self.name = "Tank"        # Tên mặc định

        # Hệ thống bắn
        self.shoot_cooldown = 0.0 # Bộ đếm thời gian hồi chiêu
        self.shoot_delay = TANK_SHOOT_DELAY # Khoảng cách tối thiểu giữa 2 lần bắn

        # Kích thước vật lý
        self.width = TANK_WIDTH
        self.height = TANK_HEIGHT
        # Tạo một Rect (Hình chữ nhật) dùng để kiểm tra va chạm trong Pygame
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (int(self.x), int(self.y))

        # Biến chứa hình ảnh sẽ được tải sau
        self.body_image = None
        self.turret_image = None
        self._tai_hinh_anh() # Gọi hàm tải ảnh ngay khi khởi tạo

    def _tai_hinh_anh(self):
        """Tải và chuẩn bị hình ảnh xe tăng từ bộ nhớ."""
        # Chuyển tên màu thành chữ hoa đầu (ví dụ: green thành Green) để khớp tên file
        cap_color = self.color.capitalize()

        # --- Tải THÂN XE ---
        try:
            # Load ảnh gốc với hỗ trợ trong suốt (.convert_alpha())
            body = pygame.image.load(f"{TANK_IMAGES_DIR}/tank{cap_color}.png").convert_alpha()
            # Thay đổi kích thước ảnh cho đúng với cài đặt game
            body = pygame.transform.scale(body, (self.width, self.height))
            # Vì ảnh gốc Kenney hướng lên trên (Bắc), ta xoay -90 độ để khớp với 
            # hệ tọa độ Pygame (hướng sang Phải là góc 0)
            self.body_image = pygame.transform.rotate(body, -90)
        except (pygame.error, FileNotFoundError):
            # Nếu không tìm thấy file ảnh, vẽ một hình chữ nhật màu làm xe tăng (Fallback)
            self.body_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            bang_mau = {"green": (0,180,0), "blue": (0,0,180), "beige": (180,160,120), "black": (60,60,60)}
            pygame.draw.rect(self.body_image, bang_mau.get(self.color, (0,180,0)), (4, 4, self.width-8, self.height-8), border_radius=4)

        # --- Tải NÒNG SÚNG ---
        try:
            turret = pygame.image.load(f"{TANK_IMAGES_DIR}/barrel{cap_color}.png").convert_alpha()
            turret = pygame.transform.scale(turret, (16, 40))
            self.turret_image = pygame.transform.rotate(turret, -90)
        except (pygame.error, FileNotFoundError):
            self.turret_image = pygame.Surface((40, 16), pygame.SRCALPHA)
            bang_mau = {"green": (0,150,0), "blue": (0,0,150), "beige": (150,130,100), "black": (40,40,40)}
            pygame.draw.rect(self.turret_image, bang_mau.get(self.color, (0,150,0)), (0, 2, 40, 12))

        # --- Tải BÁNH XÍCH (Tracks) ---
        try:
            tracks = pygame.image.load(f"{TANK_IMAGES_DIR}/tracksLarge.png").convert_alpha()
            tracks = pygame.transform.scale(tracks, (self.width, self.height))
            self.tracks_image = pygame.transform.rotate(tracks, -90)
        except (pygame.error, FileNotFoundError):
            self.tracks_image = None

    def _cap_nhat_rect(self):
        """Đồng bộ hóa hình chữ nhật va chạm với tọa độ thực tế của xe."""
        self.rect.center = (int(self.x), int(self.y))

    def get_rect(self):
        """Cung cấp hình chữ nhật va chạm cho các module khác (va chạm tường, đạn)."""
        return self.rect

    def update(self, dt):
        """Cập nhật logic của xe tăng sau mỗi khung hình."""
        # Giảm thời gian chờ bắn
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        # Cập nhật lại khung va chạm
        self._cap_nhat_rect()

    # ==========================================
    # HÀNH VI DI CHUYỂN
    # ==========================================

    def move_forward(self, dt):
        """Tiến về phía trước dựa theo góc xoay hiện tại của thân xe."""
        # Công thức: x = x + cos(góc) * tốc độ, y = y + sin(góc) * tốc độ
        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt
        self._cap_nhat_rect()

    def move_backward(self, dt):
        """Lùi về phía sau (tốc độ lùi chỉ bằng 60% tốc độ tiến)."""
        self.x -= math.cos(self.angle) * self.speed * 0.6 * dt
        self.y -= math.sin(self.angle) * self.speed * 0.6 * dt
        self._cap_nhat_rect()

    def rotate_body_left(self, dt):
        """Xoay thân xe sang bên trái."""
        self.angle -= math.radians(self.rotation_speed) * dt

    def rotate_body_right(self, dt):
        """Xoay thân xe sang bên phải."""
        self.angle += math.radians(self.rotation_speed) * dt

    # ==========================================
    # QUẢN LÝ NÒNG SÚNG
    # ==========================================

    def rotate_turret_to_angle(self, target_angle, dt):
        """Xoay nòng súng về phía một góc xác định một cách mượt mà."""
        diff = target_angle - self.turret_angle
        # Chuẩn hóa góc để xe luôn xoay theo hướng ngắn nhất (tránh xoay vòng 360 độ)
        while diff > math.pi: diff -= 2 * math.pi
        while diff < -math.pi: diff += 2 * math.pi
        
        # Giới hạn tốc độ xoay mỗi khung hình
        max_rot = math.radians(self.turret_rotation_speed) * dt
        if abs(diff) < max_rot:
            self.turret_angle = target_angle # Nếu lệch ít thì gán thẳng luôn
        elif diff > 0:
            self.turret_angle += max_rot # Xoay phải
        else:
            self.turret_angle -= max_rot # Xoay trái

    def rotate_turret_to_target(self, target_x, target_y, dt):
        """Xoay nòng súng về phía tọa độ mục tiêu một cách mượt mà."""
        # Tính toán góc cần đạt được bằng hàm atan2
        desired = math.atan2(target_y - self.y, target_x - self.x)
        # Tính khoảng cách góc giữa hiện tại và mục tiêu
        diff = desired - self.turret_angle
        # Chuẩn hóa góc để xe luôn xoay theo hướng ngắn nhất (tránh xoay vòng 360 độ)
        while diff > math.pi: diff -= 2 * math.pi
        while diff < -math.pi: diff += 2 * math.pi
        
        # Giới hạn tốc độ xoay mỗi khung hình
        max_rot = math.radians(self.turret_rotation_speed) * dt
        if abs(diff) < max_rot:
            self.turret_angle = desired # Nếu lệch ít thì gán thẳng luôn
        elif diff > 0:
            self.turret_angle += max_rot # Xoay phải
        else:
            self.turret_angle -= max_rot # Xoay trái

    # ==========================================
    # HỆ THỐNG CHIẾN ĐẤU
    # ==========================================

    def shoot(self):
        """Thực hiện bắn đạn."""
        # Nếu đang trong thời gian nạp đạn (cooldown) thì không bắn
        if self.shoot_cooldown > 0:
            return None
        
        # Đặt lại thời gian nạp đạn
        self.shoot_cooldown = self.shoot_delay

        # Tính toán điểm xuất phát của viên đạn (đầu nòng súng)
        # Dịch chuyển ra xa khỏi tâm xe khoảng 30 pixel theo hướng nòng
        muzzle_dist = 30
        bx = self.x + math.cos(self.turret_angle) * muzzle_dist
        by = self.y + math.sin(self.turret_angle) * muzzle_dist

        # Trả về dữ liệu cấu hình viên đạn
        return {
            "x": bx, "y": by,
            "angle": self.turret_angle,
            "speed": BULLET_SPEED,
            "damage": BULLET_DAMAGE,
            "owner": self # Lưu chủ sở hữu để đạn không tự bắn trúng mình
        }

    def take_damage(self, damage):
        """Trừ máu khi xe tăng bị trúng đạn hoặc dính sát thương nổ."""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False # Đánh dấu là đã chết

    def is_alive(self):
        """Kiểm tra trạng thái sinh mạng."""
        return self.alive and self.health > 0

    # ==========================================
    # TOÁN HỌC HỖ TRỢ
    # ==========================================

    def get_distance_to(self, tx, ty):
        """Tính khoảng cách đường chim bay đến một điểm bất kỳ."""
        return math.sqrt((self.x - tx)**2 + (self.y - ty)**2)

    def get_angle_to(self, tx, ty):
        """Tính góc cần xoay để nhìn thẳng vào một điểm bất kỳ."""
        return math.atan2(ty - self.y, tx - self.x)

    # ==========================================
    # HIỂN THỊ ĐỒ HỌA
    # ==========================================

    def draw(self, screen, cam_x=0, cam_y=0):
        """Vẽ toàn bộ thành phần xe tăng lên màn hình."""
        if not self.alive: return

        # Tính toán tọa độ hiển thị trên màn hình (đã trừ đi vị trí Camera)
        sx = self.x - cam_x
        sy = self.y - cam_y

        # 1. Vẽ bánh xích
        if getattr(self, 'tracks_image', None):
            rotated_tracks = pygame.transform.rotate(self.tracks_image, -math.degrees(self.angle))
            tracks_rect = rotated_tracks.get_rect(center=(int(sx), int(sy)))
            screen.blit(rotated_tracks, tracks_rect)

        # 2. Vẽ thân xe (Xoay ảnh dựa theo góc angle hiện tại)
        rotated_body = pygame.transform.rotate(self.body_image, -math.degrees(self.angle))
        body_rect = rotated_body.get_rect(center=(int(sx), int(sy)))
        screen.blit(rotated_body, body_rect)

        # 3. Vẽ nòng súng (Xoay nòng theo góc turret_angle hiện tại)
        rotated_turret = pygame.transform.rotate(self.turret_image, -math.degrees(self.turret_angle))
        # Dịch nòng súng lên trước một chút để khớp với thân xe
        offset_dist = 15
        tx = sx + math.cos(self.turret_angle) * offset_dist
        ty = sy + math.sin(self.turret_angle) * offset_dist
        turret_rect = rotated_turret.get_rect(center=(int(tx), int(ty)))
        screen.blit(rotated_turret, turret_rect)

        # 4. Vẽ thanh máu trên đầu
        bar_w = 40
        bar_h = 5
        bx = int(sx - bar_w / 2)
        by = int(sy - self.height / 2 - 15)
        # Viền đen
        pygame.draw.rect(screen, (0, 0, 0), (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        # Phần máu đỏ (phần mất đi)
        pygame.draw.rect(screen, (200, 0, 0), (bx, by, bar_w, bar_h))
        # Phần máu hiện tại (xanh hoặc vàng tùy lượng máu)
        if self.health > 0:
            ratio = self.health / self.max_health
            hp_w = int(bar_w * ratio)
            c = (0, 200, 0) if ratio > 0.5 else (255, 150, 0) if ratio > 0.25 else (255, 0, 0)
            if hp_w > 0:
                pygame.draw.rect(screen, c, (bx, by, hp_w, bar_h))
                
        # 5. Vẽ tên định danh
        if hasattr(self, 'name') and self.name:
            from src.core.font import get_font
            font = get_font(14)
            name_surf = font.render(self.name, True, (255, 255, 255))
            shadow = font.render(self.name, True, (0, 0, 0)) # Đổ bóng chữ cho dễ đọc
            name_rect = name_surf.get_rect(midbottom=(int(sx), by - 2))
            screen.blit(shadow, name_rect.move(1, 1))
            screen.blit(name_surf, name_rect)

    def get_stats(self):
        """Trả về dữ liệu thống kê mặc định (Sẽ được Player ghi đè)."""
        return {"kills": 0, "shots_fired": 0, "shots_hit": 0, "accuracy": 0}
