"""
HUD (Heads-Up Display) — Giao diện thông tin trong trận đấu.

File này quản lý tất cả những gì người chơi nhìn thấy đè lên màn hình game:
- Thanh máu (Health Bar).
- Điểm số, số mạng, độ chính xác.
- Minimap (Bản đồ nhỏ) tự động co giãn.
- Kill Feed (Thông báo tiêu diệt) ở góc màn hình.
- Hiệu ứng chuyển màn (Level Transition).
"""

import pygame
from src.core.font import get_font
from src.core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, HUD_MARGIN,
    HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT,
    COLOR_WHITE, COLOR_RED, COLOR_GREEN, COLOR_BLACK,
    COLOR_YELLOW, MINIMAP_SIZE, MINIMAP_ALPHA, TILE_SIZE
)


class KillFeed:
    """Quản lý các dòng thông báo tiêu diệt biến mất dần theo thời gian."""
    def __init__(self):
        self.messages = [] # Danh sách [nội dung, thời gian_còn_lại]

    def add(self, text):
        """Thêm thông báo mới, tồn tại trong 3 giây."""
        self.messages.append([text, 3.0])

    def update(self, dt):
        """Giảm thời gian tồn tại của các thông báo."""
        for m in self.messages: m[1] -= dt
        # Xóa các thông báo đã hết thời gian
        self.messages = [m for m in self.messages if m[1] > 0]

    def draw(self, screen, font, x, y):
        """Vẽ tối đa 4 thông báo gần nhất."""
        for i, (text, timer) in enumerate(self.messages[-4:]):
            s = font.render(text, True, COLOR_YELLOW)
            # Tạo hiệu ứng mờ dần (Alpha) dựa trên thời gian còn lại
            s.set_alpha(min(255, int(timer*255)))
            screen.blit(s, (x, y+i*25))


class HUD:
    """Lớp chính điều khiển giao diện người dùng trong game."""

    def __init__(self):
        """Khởi tạo font chữ và hệ thống thông báo."""
        self.font = get_font(28)
        self.small_font = get_font(18)
        self.kill_feed = KillFeed()

    def draw(self, screen, player, score=0, enemies_left=0, level=1,
             game_map=None, enemies=None, lives=3):
        """Vẽ toàn bộ thành phần giao diện lên màn hình chính."""
        y = HUD_MARGIN
        # 1. Vẽ thanh máu của người chơi
        self.draw_health_bar(screen, HUD_MARGIN, y, player.health, player.max_health)
        
        y += HEALTH_BAR_HEIGHT + 8
        stats = player.get_stats()
        
        # 2. Chuẩn bị danh sách các dòng chỉ số
        lines = [
            (f"Mạng: {'❤ '*lives}", (255,80,80)),
            (f"Điểm: {score}", COLOR_WHITE),
            (f"Địch: {enemies_left}", COLOR_RED),
            (f"Màn: {level}", COLOR_YELLOW),
            (f"Tiêu diệt: {stats['kills']}", COLOR_WHITE),
            (f"Chính xác: {stats['accuracy']}%", COLOR_WHITE),
        ]
        
        # 3. Vẽ từng dòng chỉ số với hiệu ứng đổ bóng đen (Shadow) để dễ nhìn
        for text, color in lines:
            shadow = self.font.render(text, True, COLOR_BLACK)
            screen.blit(shadow, (HUD_MARGIN+2, y+2))
            screen.blit(self.font.render(text, True, color), (HUD_MARGIN, y))
            y += 26
            
        # 4. Vẽ bảng thông báo tiêu diệt ở góc phải
        self.kill_feed.draw(screen, self.small_font, SCREEN_WIDTH-250, HUD_MARGIN)
        
        # 5. Vẽ bản đồ nhỏ (Minimap) nếu có dữ liệu map
        if game_map:
            self._draw_minimap(screen, game_map, player, enemies)

    def draw_health_bar(self, screen, x, y, current, maximum):
        """Vẽ thanh máu với màu sắc thay đổi theo tình trạng (Xanh -> Vàng -> Đỏ)."""
        # Khung viền và nền đỏ cố định
        pygame.draw.rect(screen, COLOR_BLACK, (x-2,y-2,HEALTH_BAR_WIDTH+4,HEALTH_BAR_HEIGHT+4))
        pygame.draw.rect(screen, COLOR_RED, (x,y,HEALTH_BAR_WIDTH,HEALTH_BAR_HEIGHT))
        
        if maximum > 0:
            ratio = current / maximum
            w = int(HEALTH_BAR_WIDTH * ratio)
            # Chọn màu dựa trên tỷ lệ máu còn lại
            c = (0,200,0) if ratio > 0.5 else (255,200,0) if ratio > 0.25 else (200,0,0)
            pygame.draw.rect(screen, c, (x,y,w,HEALTH_BAR_HEIGHT))
            
        # Hiển thị con số HP/MaxHP chính xác ở giữa thanh
        t = self.small_font.render(f"{current}/{maximum}", True, COLOR_WHITE)
        screen.blit(t, t.get_rect(center=(x+HEALTH_BAR_WIDTH//2, y+HEALTH_BAR_HEIGHT//2)))

    def _draw_minimap(self, screen, game_map, player, enemies):
        """Vẽ bản đồ thu nhỏ hiển thị vị trí đồng đội và kẻ địch."""
        pw, ph = game_map.get_pixel_width(), game_map.get_pixel_height()
        if pw == 0 or ph == 0: return
        
        # Tính toán tỷ lệ thu nhỏ (Scale) để map vừa khít vào ô Minimap
        s = min(MINIMAP_SIZE/pw, MINIMAP_SIZE/ph)
        scaled_w, scaled_h = int(pw * s), int(ph * s)
        
        # Tọa độ đặt Minimap (Góc dưới bên phải)
        mx = SCREEN_WIDTH - scaled_w - HUD_MARGIN
        my = SCREEN_HEIGHT - scaled_h - HUD_MARGIN
        
        # Tạo một bề mặt (Surface) trong suốt để vẽ Minimap
        mm = pygame.Surface((scaled_w, scaled_h), pygame.SRCALPHA)
        mm.fill((0, 0, 0, MINIMAP_ALPHA)) # Nền đen mờ
        
        # Vẽ các ô địa hình lên Minimap
        for row in game_map.tiles:
            for tile in row:
                tx, ty = int(tile.col * TILE_SIZE * s), int(tile.row * TILE_SIZE * s)
                ts = max(1, int(TILE_SIZE * s))
                # Tường có màu xám, đất có màu tối
                c = (100, 100, 100) if tile.is_solid else (60, 60, 40)
                pygame.draw.rect(mm, c, (tx, ty, ts, ts))
                
        # Vẽ vị trí Player bằng chấm XANH LÁ
        if player and player.is_alive():
            pygame.draw.circle(mm, (0, 255, 0), (int(player.x * s), int(player.y * s)), 4)
            
        # Vẽ vị trí các Enemy bằng chấm ĐỎ
        if enemies:
            for e in enemies:
                if e.is_alive():
                    pygame.draw.circle(mm, (255, 0, 0), (int(e.x * s), int(e.y * s)), 3)
                    
        # Vẽ khung viền trắng cho Minimap
        pygame.draw.rect(mm, COLOR_WHITE, (0, 0, scaled_w, scaled_h), 2)
        screen.blit(mm, (mx, my))

    def update(self, dt):
        """Cập nhật các thành phần động của giao diện."""
        self.kill_feed.update(dt)

    def add_kill_message(self, name="Enemy"):
        """Gửi thông báo tiêu diệt mới vào hệ thống thông báo."""
        self.kill_feed.add(f"✓ Tiêu diệt {name} +100")


class LevelTransition:
    """Hiển thị màn hình đen mờ và chữ 'MÀN X' khi bắt đầu mỗi cấp độ."""
    def __init__(self):
        self.active = False
        self.timer = 0.0
        self.level = 1
        self.font = get_font(56, bold=True)
        self.sub_font = get_font(28)

    def start(self, level, duration=2.0):
        """Kích hoạt hiệu ứng chuyển màn."""
        self.active = True
        self.timer = duration
        self.level = level

    def update(self, dt):
        """Giảm thời gian chờ và tắt hiệu ứng khi hết giờ."""
        if not self.active: return False
        self.timer -= dt
        if self.timer <= 0:
            self.active = False
            return True # Báo hiệu đã chuyển màn xong
        return False

    def draw(self, screen):
        """Vẽ lớp phủ đen mờ và thông báo màn chơi hiện tại."""
        if not self.active: return
        o = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SRCALPHA)
        # Hiệu ứng mờ dần theo thời gian
        a = int(200*(self.timer/2.0))
        o.fill((0,0,0,min(200,a)))
        screen.blit(o, (0,0))
        
        cx, cy = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
        # Vẽ chữ "MÀN X" chính giữa màn hình
        t = self.font.render(f"MÀN {self.level}", True, COLOR_YELLOW)
        screen.blit(t, t.get_rect(center=(cx,cy-20)))
        s = self.sub_font.render("Chuẩn bị chiến đấu!", True, COLOR_WHITE)
        screen.blit(s, s.get_rect(center=(cx,cy+40)))
