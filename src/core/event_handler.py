import pygame
from typing import Dict, Tuple


class EventHandler:
    """Đọc bàn phím và chuột mỗi frame, lưu vào cache để các module khác truy vấn."""

    def __init__(self):
        self._keys = {}
        self._mouse_pos = (0, 0)
        self._mouse_pressed = False
        self._quit_requested = False
        self._events = []
        self._paused_pressed = False

    def update(self):
        """Gọi đầu mỗi frame để đọc tất cả input."""
        self._events = pygame.event.get()
        self._quit_requested = False
        for event in self._events:
            if event.type == pygame.QUIT:
                self._quit_requested = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._paused_pressed = True
        pressed = pygame.key.get_pressed()
        self._keys = {}
        for i in range(len(pressed)):
            if pressed[i]:
                self._keys[i] = True
        self._mouse_pos = pygame.mouse.get_pos()
        self._mouse_pressed = pygame.mouse.get_pressed()[0]

    def get_keys(self):
        return self._keys

    def is_key_pressed(self, key):
        return self._keys.get(key, False)

    def get_mouse_pos(self):
        return self._mouse_pos

    def is_mouse_pressed(self):
        return self._mouse_pressed

    def is_quit_requested(self):
        return self._quit_requested

    def is_pause_pressed(self):
        pressed = self._paused_pressed
        self._paused_pressed = False
        return pressed

    def get_events(self):
        return self._events
