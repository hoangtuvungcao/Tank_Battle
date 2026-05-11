import pygame
import math
from src.core.font import get_font
from src.core.settings import (SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG_MENU, COLOR_WHITE,
    COLOR_GRAY, COLOR_DARK_GRAY, COLOR_GREEN, COLOR_YELLOW, MUSIC_VOLUME, SFX_VOLUME)
from src.ui.button import Button


class SettingsMenu:
    def __init__(self, music_vol=MUSIC_VOLUME, sfx_vol=SFX_VOLUME, difficulty="normal", fullscreen=False):
        self.music_volume = music_vol
        self.sfx_volume = sfx_vol
        self.difficulty = difficulty
        self.fullscreen = fullscreen
        self.font = get_font(28)
        self.title_font = get_font(46, bold=True)
        self.small_font = get_font(20)
        self.back_button = Button(SCREEN_WIDTH//2-140, SCREEN_HEIGHT-100, 280, 60, "QUAY LẠI", color=(100, 100, 100), hover_color=(140, 140, 140))
        cx = SCREEN_WIDTH // 2
        
        # Cấu hình hạt bụi 3D
        import random
        self.particles = [{"x": random.randint(0, SCREEN_WIDTH), 
                           "y": random.randint(0, SCREEN_HEIGHT), 
                           "z": random.uniform(0.5, 2.0),
                           "speed": random.uniform(10, 30)} for _ in range(100)]
                           
        self._slider_music = pygame.Rect(cx-150, 260, 300, 20)
        self._slider_sfx = pygame.Rect(cx-150, 350, 300, 20)
        self._drag_music = self._drag_sfx = False
        self._diff_btns = {
            "easy": pygame.Rect(cx-200, 450, 120, 50),
            "normal": pygame.Rect(cx-60, 450, 120, 50),
            "hard": pygame.Rect(cx+80, 450, 120, 50),
        }
        self._fs_rect = pygame.Rect(cx-20, 540, 40, 40)
        self.anim_time = 0.0

    def update(self, mouse_pos, dt=0.0):
        self.back_button.update(mouse_pos)
        self.anim_time += dt

    def _draw_bg(self, screen):
        screen.fill((10, 15, 20))
        
        # Lưới 3D chạy dọc
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
            dx = x - cx
            pygame.draw.line(screen, (20, 60, 30), (cx, SCREEN_HEIGHT // 2), (cx + dx * 3, SCREEN_HEIGHT), 1)

        # Vẽ particles
        for p in self.particles:
            p["y"] -= p["speed"] * 0.016
            if p["y"] < 0:
                p["y"] = SCREEN_HEIGHT
                import random
                p["x"] = random.randint(0, SCREEN_WIDTH)
            
            if "surf" not in p:
                size = max(1, int(3 / p["z"]))
                alpha = max(50, min(255, int(255 / p["z"])))
                psurf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(psurf, (150, 255, 150, alpha), (size, size), size)
                p["surf"] = psurf
            screen.blit(p["surf"], (p["x"], p["y"]))

    def draw(self, screen):
        self._draw_bg(screen)
        cx = SCREEN_WIDTH // 2
        
        # Panel Glassmorphism 3D
        panel_w, panel_h = 560, 500
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 25, 35, 200), (0,0,panel_w,panel_h), border_radius=20)
        pygame.draw.rect(panel, (100, 120, 150, 100), (0,0,panel_w,panel_h), 2, border_radius=20)
        
        shadow_panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(shadow_panel, (0, 0, 0, 150), (0,0,panel_w,panel_h), border_radius=20)
        screen.blit(shadow_panel, (cx-panel_w//2 + 10, 120 + 10))
        screen.blit(panel, (cx-panel_w//2, 120))
        
        # Tiêu đề
        t = self.title_font.render("CÀI ĐẶT", True, (255, 255, 255))
        ts = self.title_font.render("CÀI ĐẶT", True, (0, 0, 0))
        screen.blit(ts, ts.get_rect(center=(cx+3, 73)))
        screen.blit(t, t.get_rect(center=(cx, 70)))
        
        self._label(screen, "Âm lượng nhạc:", 220)
        self._slider(screen, self._slider_music, self.music_volume)
        
        self._label(screen, "Âm lượng hiệu ứng:", 310)
        self._slider(screen, self._slider_sfx, self.sfx_volume)
        
        self._label(screen, "Độ khó:", 410)
        names = {"easy":"Dễ","normal":"Thường","hard":"Khó"}
        for k, r in self._diff_btns.items():
            is_sel = self.difficulty == k
            bg_c = (40, 160, 40) if is_sel else (60, 70, 80)
            
            # Shadow 3D
            pygame.draw.rect(screen, (0,0,0,100), r.move(2, 4), border_radius=10)
            # Nền nút
            pygame.draw.rect(screen, tuple(max(0, c-40) for c in bg_c), r.move(0, 3), border_radius=10)
            pygame.draw.rect(screen, bg_c, r if not is_sel else r.move(0, 2), border_radius=10)
            # Viền
            border_c = (255, 255, 255) if is_sel else (100, 110, 120)
            pygame.draw.rect(screen, border_c, r if not is_sel else r.move(0, 2), 2, border_radius=10)
            
            text_surf = self.font.render(names[k], True, COLOR_WHITE)
            screen.blit(text_surf, text_surf.get_rect(center=(r.centerx, r.centery + (2 if is_sel else 0))))
            
        self._label(screen, "Toàn màn hình:", 545)
        
        # Checkbox 3D
        pygame.draw.rect(screen, (0,0,0,100), self._fs_rect.move(2, 3), border_radius=6)
        pygame.draw.rect(screen, (50, 60, 70), self._fs_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_WHITE, self._fs_rect, 2, border_radius=6)
        if self.fullscreen:
            pygame.draw.rect(screen, (40, 200, 40), self._fs_rect.inflate(-10,-10), border_radius=4)
            
        self.back_button.draw(screen)

    def _label(self, screen, text, y):
        shadow = self.font.render(text, True, (0, 0, 0))
        text_s = self.font.render(text, True, (200, 210, 220))
        screen.blit(shadow, (SCREEN_WIDTH//2-250 + 2, y + 2))
        screen.blit(text_s, (SCREEN_WIDTH//2-250, y))

    def _slider(self, screen, rect, value):
        # Nền rãnh trượt 3D
        pygame.draw.rect(screen, (30, 40, 50), rect, border_radius=10)
        pygame.draw.rect(screen, (10, 15, 20), rect, 2, border_radius=10)
        
        # Thanh trượt màu
        fill_rect = pygame.Rect(rect.x, rect.y, int(rect.width*value), rect.height)
        if fill_rect.width > 0:
            pygame.draw.rect(screen, (60, 180, 60), fill_rect, border_radius=10)
            pygame.draw.rect(screen, (100, 220, 100), fill_rect.inflate(-4,-4), border_radius=8)
            
        # Nút kéo (thumb)
        kx = rect.x + int(rect.width * value)
        pygame.draw.circle(screen, (0, 0, 0, 100), (kx+2, rect.centery+3), 16)
        pygame.draw.circle(screen, (220, 220, 220), (kx, rect.centery), 16)
        pygame.draw.circle(screen, (255, 255, 255), (kx, rect.centery), 14)
        pygame.draw.circle(screen, (100, 100, 100), (kx, rect.centery), 6)
        
        val_text = self.small_font.render(f"{int(value*100)}%", True, (255, 220, 100))
        screen.blit(val_text, (rect.right+20, rect.y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self._slider_music.collidepoint(pos):
                self._drag_music = True
                return "click"
            elif self._slider_sfx.collidepoint(pos):
                self._drag_sfx = True
                return "click"
            for k, r in self._diff_btns.items():
                if r.collidepoint(pos):
                    self.difficulty = k
                    return "click"
            if self._fs_rect.collidepoint(pos):
                self.fullscreen = not self.fullscreen
                return "click"
            if self.back_button.is_clicked(pos): return "back"
        elif event.type == pygame.MOUSEBUTTONUP:
            self._drag_music = self._drag_sfx = False
        elif event.type == pygame.MOUSEMOTION:
            if self._drag_music:
                self.music_volume = max(0, min(1, (event.pos[0]-self._slider_music.x)/self._slider_music.width))
            elif self._drag_sfx:
                self.sfx_volume = max(0, min(1, (event.pos[0]-self._slider_sfx.x)/self._slider_sfx.width))
        return ""
