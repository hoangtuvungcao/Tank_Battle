import pygame
from src.core.font import get_font
from src.core.settings import (SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG_MENU, COLOR_WHITE,
    COLOR_GRAY, COLOR_DARK_GRAY, COLOR_GREEN, COLOR_YELLOW, TANK_COLORS, TANK_COLOR_NAMES, TANK_IMAGES_DIR)


class TankSelectMenu:
    def __init__(self, selected_color="green"):
        self.selected_color = selected_color
        self.font = get_font(28)
        self.title_font = get_font(42, bold=True)
        self.small_font = get_font(20)
        self.tank_previews = {}
        self._load()
        cw, ch, sp = 180, 240, 20
        tw = len(TANK_COLORS)*cw + (len(TANK_COLORS)-1)*sp
        sx = (SCREEN_WIDTH-tw)//2
        self.card_rects = {}
        for i, c in enumerate(TANK_COLORS):
            self.card_rects[c] = pygame.Rect(sx+i*(cw+sp), 250, cw, ch)
        self.start_rect = pygame.Rect(SCREEN_WIDTH//2-120, SCREEN_HEIGHT-100, 240, 55)
        self.back_rect = pygame.Rect(SCREEN_WIDTH//2-120, SCREEN_HEIGHT-170, 240, 50)

    def _load(self):
        colors_map = {"green":(0,200,0),"blue":(0,0,200),"beige":(200,180,140),"black":(50,50,50)}
        for c in TANK_COLORS:
            try:
                # Tạo surface kết hợp thân và nòng (chiều cao 120 để nòng nhô ra ngoài)
                combined = pygame.Surface((96, 120), pygame.SRCALPHA)
                
                # Load thân
                img = pygame.image.load(f"{TANK_IMAGES_DIR}/tank{c.capitalize()}.png").convert_alpha()
                img = pygame.transform.scale(img, (96, 96))
                
                # Load nòng
                turret = pygame.image.load(f"{TANK_IMAGES_DIR}/barrel{c.capitalize()}.png").convert_alpha()
                turret = pygame.transform.scale(turret, (32, 80))
                
                # Vẽ nòng ở trên cùng để nhô ra
                combined.blit(turret, (32, 0))
                # Vẽ thân thấp xuống
                combined.blit(img, (0, 24))
                
                self.tank_previews[c] = combined
            except:
                s = pygame.Surface((96, 120), pygame.SRCALPHA)
                m = colors_map.get(c, (200,200,0))
                pygame.draw.rect(s, m, (16, 40, 64, 64), border_radius=8)
                pygame.draw.rect(s, (255,255,255), (16, 40, 64, 64), 2, border_radius=8)
                pygame.draw.rect(s, m, (36, 0, 24, 60))
                self.tank_previews[c] = s

    def update(self, mouse_pos):
        pass

    def draw(self, screen):
        screen.fill(COLOR_BG_MENU)
        cx = SCREEN_WIDTH//2
        screen.blit(self.title_font.render("CHỌN XE TĂNG",True,COLOR_WHITE),
                     self.title_font.render("CHỌN XE TĂNG",True,COLOR_WHITE).get_rect(center=(cx,100)))
        screen.blit(self.small_font.render("Chọn màu xe tăng của bạn",True,COLOR_GRAY),
                     self.small_font.render("Chọn màu xe tăng của bạn",True,COLOR_GRAY).get_rect(center=(cx,150)))
        for c in TANK_COLORS:
            r = self.card_rects[c]
            sel = c == self.selected_color
            bg = (60,80,60) if sel else (40,40,60)
            pygame.draw.rect(screen, bg, r, border_radius=12)
            bc = COLOR_GREEN if sel else COLOR_GRAY
            pygame.draw.rect(screen, bc, r, 3 if sel else 1, border_radius=12)
            p = self.tank_previews.get(c)
            if p: screen.blit(p, p.get_rect(center=(r.centerx, r.y+90)))
            n = TANK_COLOR_NAMES.get(c, c)
            screen.blit(self.font.render(n,True,COLOR_WHITE),
                         self.font.render(n,True,COLOR_WHITE).get_rect(center=(r.centerx, r.bottom-50)))
            if sel:
                screen.blit(self.font.render("✓",True,COLOR_GREEN),
                             self.font.render("✓",True,COLOR_GREEN).get_rect(center=(r.centerx,r.bottom-20)))
        mp = pygame.mouse.get_pos()
        sc = (0,180,0) if self.start_rect.collidepoint(mp) else COLOR_DARK_GRAY
        pygame.draw.rect(screen, sc, self.start_rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_WHITE, self.start_rect, 2, border_radius=10)
        screen.blit(self.font.render("BẮT ĐẦU CHƠI",True,COLOR_WHITE),
                     self.font.render("BẮT ĐẦU CHƠI",True,COLOR_WHITE).get_rect(center=self.start_rect.center))
        bc2 = (100,100,120) if self.back_rect.collidepoint(mp) else COLOR_DARK_GRAY
        pygame.draw.rect(screen, bc2, self.back_rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_GRAY, self.back_rect, 1, border_radius=8)
        screen.blit(self.font.render("Quay lại",True,COLOR_WHITE),
                     self.font.render("Quay lại",True,COLOR_WHITE).get_rect(center=self.back_rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for c, r in self.card_rects.items():
                if r.collidepoint(event.pos):
                    self.selected_color = c
                    return "select"
            if self.start_rect.collidepoint(event.pos): return "start"
            if self.back_rect.collidepoint(event.pos): return "back"
        return ""
