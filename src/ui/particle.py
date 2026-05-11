"""ParticleSystem — Hệ thống hiệu ứng hạt (particle).

Quản lý tất cả hiệu ứng đặc biệt:
- Nổ lớn (tank chết): Nhiều hạt khói + lửa bay ra
- Nổ nhỏ (barrel/trúng đạn): Ít hạt hơn, phạm vi nhỏ
- Chớp lửa đầu nòng (muzzle flash): Tia lửa ngắn khi bắn
- Khói di chuyển (trail): Vệt khói khi tank chạy nhanh

Tất cả hiệu ứng đều tự mờ dần và tự hủy sau thời gian sống.
"""

import pygame
import math
import random
from src.core.settings import (
    PARTICLE_LIFETIME, EXPLOSION_PARTICLE_COUNT, SMOKE_IMAGES_DIR
)


class Particle:
    """Một hạt hiệu ứng đơn lẻ (khói, lửa, tia lửa).

    Mỗi hạt có:
    - Vị trí (x, y) + vận tốc (vx, vy)
    - Thời gian sống (lifetime) — tự hủy khi hết
    - Ảnh hiển thị — mờ dần theo tuổi
    """

    def __init__(self, x, y, image, lifetime=PARTICLE_LIFETIME, vx=0.0, vy=0.0):
        """Tạo hạt hiệu ứng.

        Tham số:
            x, y: Vị trí ban đầu
            image: Ảnh pygame Surface
            lifetime: Thời gian sống (giây)
            vx, vy: Vận tốc ban đầu (pixel/giây)
        """
        self.x, self.y = x, y
        self.image = image
        self.lifetime = lifetime
        self.age = 0.0
        self.vx, self.vy = vx, vy
        self.active = True

    def update(self, dt):
        """Cập nhật vị trí + kiểm tra hết thời gian sống."""
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Giảm tốc dần (ma sát không khí)
        self.vx *= 0.95
        self.vy *= 0.95
        if self.age >= self.lifetime:
            self.active = False
            return False
        return True

    def draw(self, screen, cam_x=0, cam_y=0):
        """Vẽ hạt — mờ dần và co lại theo tuổi."""
        if not self.active:
            return
        # Alpha = 255 khi mới tạo → 0 khi hết lifetime
        alpha = max(0, 255 * (1 - self.age / self.lifetime))
        image = self.image.copy()
        image.set_alpha(int(alpha))

        # Co nhỏ dần theo tuổi
        scale = max(0.3, 1 - self.age / self.lifetime * 0.5)
        new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
        if new_size[0] > 0 and new_size[1] > 0:
            image = pygame.transform.scale(image, new_size)
        rect = image.get_rect(center=(int(self.x - cam_x), int(self.y - cam_y)))
        screen.blit(image, rect)


class ParticleSystem:
    """Hệ thống quản lý tất cả hiệu ứng hạt.

    Sử dụng:
        ps = ParticleSystem()
        ps.add_explosion(x, y)                    # Nổ lớn
        ps.add_explosion(x, y, small=True)         # Nổ nhỏ
        ps.add_muzzle_flash(x, y, angle)           # Chớp lửa bắn
        ps.add_smoke_trail(x, y)                   # Vệt khói
        ps.update_all(dt)                          # Cập nhật
        ps.draw_all(screen, cam_x, cam_y)          # Vẽ
    """

    def __init__(self):
        self.particles = []       # Danh sách hạt đang hoạt động
        self._smoke_images = []   # Cache ảnh khói đã load
        self._loaded = False

    def _load_smoke(self):
        """Tải ảnh khói từ assets/images/smoke/ (lazy load lần đầu).

        Có 4 màu x 6 ảnh = 24 ảnh khói khác nhau.
        Nếu không tìm thấy file → tạo hình tròn gradient thay thế.
        """
        if self._loaded:
            return
        # Tải tất cả ảnh khói: smokeOrange0-5, smokeGrey0-5, v.v.
        for color in ["Orange", "Grey", "White", "Yellow"]:
            for i in range(6):
                try:
                    path = f"{SMOKE_IMAGES_DIR}/smoke{color}{i}.png"
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, (48, 48))
                    self._smoke_images.append(img)
                except (pygame.error, FileNotFoundError):
                    pass

        # Fallback: nếu không load được ảnh nào → tạo hình tròn gradient
        if not self._smoke_images:
            for i in range(6):
                sz = 48 - i * 4
                s = pygame.Surface((sz, sz), pygame.SRCALPHA)
                c = (255, 150 - i * 20, 0, 200 - i * 30)
                pygame.draw.circle(s, c, (sz // 2, sz // 2), sz // 2 - 2)
                self._smoke_images.append(s)
        self._loaded = True

    def add_explosion(self, x, y, color="orange", small=False):
        """Tạo vụ nổ tại vị trí (x, y).

        Tham số:
            x, y: Tâm vụ nổ
            color: Không dùng hiện tại (dành cho mở rộng)
            small: True = nổ nhỏ (barrel/trúng đạn), False = nổ lớn (tank chết)
        """
        self._load_smoke()

        # Nổ nhỏ: ít hạt + tốc độ thấp. Nổ lớn: nhiều hạt + tốc độ cao
        count = EXPLOSION_PARTICLE_COUNT // 2 if small else EXPLOSION_PARTICLE_COUNT
        speed_range = (30, 120) if small else (50, 200)

        for _ in range(count):
            # Chọn ảnh khói ngẫu nhiên
            if self._smoke_images:
                img = random.choice(self._smoke_images).copy()
            else:
                img = self._fallback_img()

            # Hướng bay ra ngẫu nhiên 360°
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            # Thời gian sống ngẫu nhiên (0.5x - 1.5x mặc định)
            lt = PARTICLE_LIFETIME * random.uniform(0.5, 1.5)
            self.particles.append(Particle(x, y, img, lt, vx, vy))

    def add_muzzle_flash(self, x, y, angle, color="orange"):
        """Tạo hiệu ứng chớp lửa đầu nòng khi bắn.

        Bao gồm:
        - 1 flash tròn sáng tại đầu nòng (0.1 giây)
        - 5-8 tia lửa bay ra theo hướng bắn (0.1-0.3 giây)

        Tham số:
            x, y: Vị trí đầu nòng súng
            angle: Hướng bắn (radian)
        """
        bang_mau = {
            "orange": (255, 150, 0),
            "yellow": (255, 255, 100),
            "white": (255, 255, 255)
        }
        mau = bang_mau.get(color, (255, 150, 0))

        # Flash trung tâm — hình tròn sáng
        flash = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(flash, (255, 200, 100), (15, 15), 5)

        # Tia lửa bay ra theo hướng bắn (có spread nhẹ ±0.5 radian)
        for _ in range(random.randint(5, 8)):
            spark_angle = angle + random.uniform(-0.5, 0.5)
            spd = random.uniform(150, 300)
            vx = math.cos(spark_angle) * spd
            vy = math.sin(spark_angle) * spd

            # Tạo tia lửa mỏng
            sz = random.randint(6, 12)
            s = pygame.Surface((sz, 3), pygame.SRCALPHA)
            for i in range(sz):
                al = 255 - (i * 20)
                pygame.draw.line(s, (*mau[:3], max(0, al)), (0, 1), (sz, 1))

            lt = random.uniform(0.1, 0.3)
            # Offset 15px trước tâm theo hướng nòng
            tx = x + math.cos(angle) * 15
            ty = y + math.sin(angle) * 15
            self.particles.append(Particle(tx, ty, s, lt, vx, vy))

        # Flash trung tâm
        self.particles.append(Particle(x, y, flash, 0.1, 0, 0))

    def add_smoke_trail(self, x, y, alpha=100):
        """Tạo vệt khói nhẹ (dùng khi tank di chuyển).

        Tham số:
            x, y: Vị trí khói
            alpha: Độ trong suốt ban đầu
        """
        self._load_smoke()
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(s, (180, 180, 180, alpha), (8, 8), 6)
        vx = random.uniform(-10, 10)
        vy = random.uniform(-20, -5)  # Bay lên nhẹ
        lt = random.uniform(0.3, 0.8)
        self.particles.append(Particle(x, y, s, lt, vx, vy))

    def _fallback_img(self):
        """Tạo ảnh hạt dự phòng nếu không load được file."""
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 150, 0, 200), (10, 10), 8)
        return s

    def update_all(self, dt):
        """Cập nhật tất cả hạt — xóa hạt đã hết thời gian sống."""
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.active]

    def draw_all(self, screen, cam_x=0, cam_y=0):
        """Vẽ tất cả hạt lên màn hình."""
        for p in self.particles:
            p.draw(screen, cam_x, cam_y)

    def get_particle_count(self):
        """Đếm số hạt đang hoạt động (debug)."""
        return len(self.particles)

    def clear_all(self):
        """Xóa tất cả hạt (dùng khi chuyển màn)."""
        self.particles.clear()
