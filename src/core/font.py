import pygame
import os

_EMBEDDED_FONT = "assets/DejaVuSans.ttf"
_cache = {}
_default_font_path = None


def _find_font_path():
    """Tìm font hỗ trợ tiếng Việt nhúng trong project."""
    if os.path.exists(_EMBEDDED_FONT):
        return _EMBEDDED_FONT
    return None


def get_font(size, bold=False):
    """Lấy font hỗ trợ tiếng Việt có dấu.

    Tham số:
        size: Cỡ font (pixel)
        bold: In đậm hay không

    Trả về:
        pygame.font.Font đã sẵn sàng dùng
    """
    global _default_font_path
    key = (size, bold)
    if key in _cache:
        return _cache[key]
    if _default_font_path is None:
        _default_font_path = _find_font_path()
    if _default_font_path:
        try:
            font = pygame.font.Font(_default_font_path, size)
            if bold:
                bold_path = _default_font_path.replace(".ttf", "-Bold.ttf")
                if os.path.exists(bold_path):
                    font = pygame.font.Font(bold_path, size)
            _cache[key] = font
            return font
        except pygame.error:
            pass
    font = pygame.font.Font(None, size)
    _cache[key] = font
    return font
