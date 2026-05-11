import math
import pygame
from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, GAME_VERSION, COLOR_WHITE, COLOR_GREEN, COLOR_GRAY, COLOR_BLACK
from src.core.font import get_font


class MainMenu:
    """Menu chính — gradient background, animation, 3 nút."""

    def __init__(self):
        from src.ui.button import Button
        self.title_font = get_font(72, bold=True)
        self.subtitle_font = get_font(26)
        self.small_font = get_font(18)
        self.anim_time = 0.0
        cx = SCREEN_WIDTH // 2
        
        # Cấu hình hạt bụi 3D
        import random
        self.particles = [{"x": random.randint(0, SCREEN_WIDTH), 
                           "y": random.randint(0, SCREEN_HEIGHT), 
                           "z": random.uniform(0.5, 2.0),
                           "speed": random.uniform(10, 30)} for _ in range(100)]
        
        # Tạo nút bằng class Button hiện đại
        self.btn_start = Button(cx - 140, 380, 280, 60, "BẮT ĐẦU", color=(40, 160, 40), hover_color=(60, 200, 60))
        self.btn_settings = Button(cx - 140, 460, 280, 60, "CÀI ĐẶT", color=(60, 100, 180), hover_color=(80, 130, 220))
        self.btn_quit = Button(cx - 140, 540, 280, 60, "THOÁT", color=(180, 40, 40), hover_color=(220, 60, 60))
        
        self._decor = self._tao_decor()

    def _tao_decor(self):
        tanks = []
        for c in [(0,180,0), (180,0,0), (0,0,180)]:
            s = pygame.Surface((48,48), pygame.SRCALPHA)
            pygame.draw.rect(s, c, (6,6,36,36), border_radius=6)
            pygame.draw.rect(s, (255,255,255,100), (6,6,36,36), 2, border_radius=6)
            pygame.draw.rect(s, c, (18,0,12,24)) # Nòng súng
            tanks.append(s)
        return tanks

    def update(self, dt=0.0):
        self.anim_time += dt
        mouse_pos = pygame.mouse.get_pos()
        self.btn_start.update(mouse_pos)
        self.btn_settings.update(mouse_pos)
        self.btn_quit.update(mouse_pos)

    def draw(self, screen):
        # 1. Vẽ nền gradient đậm (deep space / dark battlefield)
        screen.fill((10, 15, 20))
        
        # Lưới 3D chạy dọc (Perspective grid)
        # Sử dụng anim_time để tạo hiệu ứng di chuyển về phía trước
        offset = (self.anim_time * 50) % 80
        if not hasattr(self, '_line_cache'):
            self._line_cache = {}
            
        for i in range(15):
            y = int(SCREEN_HEIGHT - (i * 80) + offset)
            if y < SCREEN_HEIGHT // 2: continue
            alpha = max(0, min(255, int((y - SCREEN_HEIGHT//2) * 1.5)))
            
            if alpha not in self._line_cache:
                surf = pygame.Surface((SCREEN_WIDTH, 2), pygame.SRCALPHA)
                surf.fill((20, 80, 40, alpha))
                self._line_cache[alpha] = surf
                
            screen.blit(self._line_cache[alpha], (0, y))
            
        cx = SCREEN_WIDTH // 2
        for x in range(0, SCREEN_WIDTH + 100, 100):
            # Vẽ đường dọc tỏa ra từ giữa màn hình (Perspective)
            dx = x - cx
            pygame.draw.line(screen, (20, 60, 30), (cx, SCREEN_HEIGHT // 2), (cx + dx * 3, SCREEN_HEIGHT), 1)

        # 2. Vẽ particles (hạt bụi bay bổng 3D)
        for p in self.particles:
            # Cập nhật vị trí
            p["y"] -= p["speed"] * 0.016
            if p["y"] < 0:
                p["y"] = SCREEN_HEIGHT
                import random
                p["x"] = random.randint(0, SCREEN_WIDTH)
            
            # Vẽ hạt - sử dụng pre-rendered surface nếu có, hoặc tạo một lần
            if "surf" not in p:
                size = max(1, int(3 / p["z"]))
                alpha = max(50, min(255, int(255 / p["z"])))
                color = (150, 255, 150, alpha)
                psurf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(psurf, color, (size, size), size)
                p["surf"] = psurf
            
            screen.blit(p["surf"], (p["x"], p["y"]))
            
        # Trang trí nền nổi bật
        for i, t in enumerate(self._decor):
            x = 150 + i*350 + math.sin(self.anim_time*0.6+i*2)*40
            y = 150 + math.cos(self.anim_time*0.4+i*1.5)*30
            rot = pygame.transform.rotate(t, math.sin(self.anim_time*1.2+i)*20)
            screen.blit(rot, rot.get_rect(center=(int(x),int(y))))
            
        # Panel trung tâm Glassmorphism 3D
        panel_w, panel_h = 400, 420
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 25, 35, 200), (0,0,panel_w,panel_h), border_radius=20)
        pygame.draw.rect(panel, (100, 120, 150, 100), (0,0,panel_w,panel_h), 2, border_radius=20)
        
        # Bóng đổ panel
        shadow_panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(shadow_panel, (0, 0, 0, 150), (0,0,panel_w,panel_h), border_radius=20)
        screen.blit(shadow_panel, (cx-panel_w//2 + 10, 160 + 10))
        screen.blit(panel, (cx-panel_w//2, 160))
        
        # Tiêu đề game (nhịp thở + shadow sâu)
        scale = 1.0 + math.sin(self.anim_time*2)*0.03
        title = self.title_font.render("TANK BATTLE", True, (255, 220, 100))
        ns = (int(title.get_width()*scale), int(title.get_height()*scale))
        title = pygame.transform.scale(title, ns)
        
        shadow = self.title_font.render("TANK BATTLE", True, (0, 0, 0))
        shadow = pygame.transform.scale(shadow, ns)
        
        screen.blit(shadow, shadow.get_rect(center=(cx+4, 224)))
        screen.blit(title, title.get_rect(center=(cx, 220)))
        
        # Gạch chân xịn
        pygame.draw.line(screen, (255, 220, 100), (cx-150, 260), (cx+150, 260), 4)
        
        sub = self.subtitle_font.render("CHIẾN ĐẤU ĐỂ SINH TỒN", True, (200, 210, 220))
        screen.blit(sub, sub.get_rect(center=(cx, 290)))
        
        # Nút bấm 3D
        self.btn_start.draw(screen)
        self.btn_settings.draw(screen)
        self.btn_quit.draw(screen)
        
        # Version
        ver = self.small_font.render(f"Phiên bản {GAME_VERSION}", True, (120,130,140))
        screen.blit(ver, ver.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)))

    def handle_click(self, pos):
        if self.btn_start.is_clicked(pos): return "start"
        if self.btn_settings.is_clicked(pos): return "settings"
        if self.btn_quit.is_clicked(pos): return "quit"
        return ""
