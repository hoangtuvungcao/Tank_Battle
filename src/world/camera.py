import pygame
from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Camera:
    """Camera theo dõi player, tính offset để vẽ bản đồ lớn."""

    def __init__(self, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height
        self.offset_x = 0.0
        self.offset_y = 0.0

    def update(self, target_x, target_y):
        self.offset_x = target_x - SCREEN_WIDTH / 2
        self.offset_y = target_y - SCREEN_HEIGHT / 2
        max_x = max(0, self.map_width - SCREEN_WIDTH)
        max_y = max(0, self.map_height - SCREEN_HEIGHT)
        self.offset_x = max(0, min(self.offset_x, max_x))
        self.offset_y = max(0, min(self.offset_y, max_y))

    def apply(self, world_x, world_y):
        return (world_x - self.offset_x, world_y - self.offset_y)

    def apply_rect(self, world_rect):
        return pygame.Rect(world_rect.x - self.offset_x, world_rect.y - self.offset_y,
                           world_rect.width, world_rect.height)

    def is_on_screen(self, world_x, world_y, margin=64):
        sx, sy = self.apply(world_x, world_y)
        return (-margin <= sx <= SCREEN_WIDTH + margin and
                -margin <= sy <= SCREEN_HEIGHT + margin)
