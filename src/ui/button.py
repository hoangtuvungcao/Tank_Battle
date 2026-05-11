import pygame
from src.core.font import get_font
from src.core.settings import COLOR_WHITE, COLOR_GRAY, COLOR_DARK_GRAY


class Button:
    def __init__(self, x, y, width, height, text="", image=None,
                 color=COLOR_DARK_GRAY, hover_color=COLOR_GRAY,
                 text_color=COLOR_WHITE, font_size=36):
        self.text = text
        self.image = image
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.rect = pygame.Rect(x, y, width, height)
        self.font = get_font(font_size)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
            return

        # Tạo hiệu ứng nổi 3D: Tính toán các thông số
        is_pressed = pygame.mouse.get_pressed()[0] and self.is_hovered
        off_y = 4 if is_pressed else (-2 if self.is_hovered else 0)
        
        # Bóng đổ lớn phía sau
        shadow_rect = self.rect.move(3, 8)
        pygame.draw.rect(screen, (0, 0, 0, 70), shadow_rect, border_radius=12)
        
        # Lớp nền đáy (darker) tạo độ dày 3D
        bottom_rect = self.rect.move(0, 4)
        bottom_color = tuple(max(0, c - 60) for c in self.color)
        pygame.draw.rect(screen, bottom_color, bottom_rect, border_radius=12)

        # Lớp nút bấm (top layer)
        btn_rect = self.rect.move(0, off_y)
        bg = tuple(min(c+40, 255) for c in self.hover_color) if self.is_hovered else self.color
        
        # Thân nút với màu nền 
        pygame.draw.rect(screen, bg, btn_rect, border_radius=12)
        
        # Viền nút rực rỡ và dày hơn để nổi bật
        border_color = (255, 255, 200) if self.is_hovered else tuple(min(255, c + 80) for c in bg)
        border_thickness = 3 if self.is_hovered else 2
        pygame.draw.rect(screen, border_color, btn_rect, border_thickness, border_radius=12)
        
        # Hiệu ứng ánh sáng bên trong nút (inner highlight) sáng hơn một chút
        highlight_rect = btn_rect.inflate(-4, -4)
        pygame.draw.rect(screen, (255, 255, 255, 40), highlight_rect, border_radius=10)

        # Vẽ text với độ tương phản cao
        if self.text:
            text_color = self.text_color if not self.is_hovered else (255, 255, 255)
            ts = self.font.render(self.text, True, text_color)
            
            # Đổ bóng đen đậm cho text để dễ đọc trên mọi nền màu
            shadow_ts = self.font.render(self.text, True, (0, 0, 0))
            screen.blit(shadow_ts, shadow_ts.get_rect(center=(btn_rect.centerx + 2, btn_rect.centery + 3)))
            
            screen.blit(ts, ts.get_rect(center=btn_rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
