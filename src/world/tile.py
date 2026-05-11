"""
Tile — Đơn vị cấu tạo nên bản đồ (64x64 pixel).

Mỗi ô gạch (Tile) trong game không chỉ là một hình ảnh đơn thuần mà còn chứa các thuộc tính:
- Vật lý: Có cho xe tăng đi qua không? (is_solid)
- Chiến thuật: Có cho phép tàng hình không? (stealth)
- Tương tác: Có thể bị bắn nổ không? (Thùng phuy)
- Thẩm mỹ: Tự động tính toán ảnh nền để bản đồ trông liền mạch.
"""

import pygame
from src.core.settings import TILE_SIZE, ENVIRONMENT_IMAGES_DIR, OBSTACLE_IMAGES_DIR


# ==========================================
# ĐỊNH NGHĨA CÁC LOẠI ĐỊA HÌNH
# ==========================================
class LoaiTile:
    DIRT = "dirt"              # Đất: Đi qua bình thường
    GRASS = "grass"            # Cỏ: Đi qua bình thường
    SAND = "sand"              # Cát: Đi qua bình thường
    WALL = "wall"              # Tường: Chặn mọi thứ
    TREE_LARGE = "tree_large"  # Cây cổ thụ: Tàng hình, đi qua được
    TREE_SMALL = "tree_small"  # Bụi cây: Tàng hình, đi qua được
    BARREL = "barrel"          # Thùng phuy: Chặn xe, có thể nổ
    SANDBAG = "sandbag"        # Bao cát: Chặn mọi thứ (không nổ)


# ==========================================
# QUY ƯỚC KÝ TỰ TRONG FILE MAP.TXT
# ==========================================
KY_TU_TILE = {
    '#': {"loai": LoaiTile.WALL, "is_solid": True},       # Tường gạch
    '.': {"loai": LoaiTile.DIRT, "is_solid": False},      # Đất nâu
    'T': {"loai": LoaiTile.DIRT, "is_solid": False},      # Spawn người chơi (trên nền đất)
    'E': {"loai": LoaiTile.DIRT, "is_solid": False},      # Spawn kẻ địch (trên nền đất)
    'B': {"loai": LoaiTile.BARREL, "is_solid": True},     # Thùng phuy xanh (nổ lan)
    'S': {"loai": LoaiTile.SANDBAG, "is_solid": True},    # Bao cát phòng thủ
    'G': {"loai": LoaiTile.GRASS, "is_solid": False},     # Thảm cỏ xanh
    'A': {"loai": LoaiTile.SAND, "is_solid": False},      # Nền cát vàng
    'L': {"loai": LoaiTile.TREE_LARGE, "is_solid": False}, # Cây lớn (Cho phép chui vào ẩn nấp)
    'l': {"loai": LoaiTile.TREE_SMALL, "is_solid": False}, # Bụi cây nhỏ (Tàng hình)
}

# Ánh xạ từ loại Tile sang đường dẫn file ảnh tương ứng
_LOAI_ANH = {
    LoaiTile.DIRT: f"{ENVIRONMENT_IMAGES_DIR}/dirt.png",
    LoaiTile.GRASS: f"{ENVIRONMENT_IMAGES_DIR}/grass.png",
    LoaiTile.SAND: f"{ENVIRONMENT_IMAGES_DIR}/sand.png",
    LoaiTile.WALL: None, # Vẽ bằng code nếu là tường
    LoaiTile.TREE_LARGE: f"{ENVIRONMENT_IMAGES_DIR}/treeLarge.png",
    LoaiTile.TREE_SMALL: f"{ENVIRONMENT_IMAGES_DIR}/treeSmall.png",
    LoaiTile.BARREL: f"{OBSTACLE_IMAGES_DIR}/barrelGreen_up.png",
    LoaiTile.SANDBAG: f"{OBSTACLE_IMAGES_DIR}/sandbagBeige.png",
}

# Màu sắc dự phòng (Fallback) nếu không tải được file ảnh
_MAU_TILE = {
    LoaiTile.WALL: (60, 60, 60),
    LoaiTile.DIRT: (160, 120, 80),
    LoaiTile.GRASS: (80, 160, 80),
    LoaiTile.SAND: (210, 180, 120),
    LoaiTile.TREE_LARGE: (40, 100, 40),
    LoaiTile.TREE_SMALL: (50, 120, 50),
    LoaiTile.BARREL: (100, 140, 60),
    LoaiTile.SANDBAG: (180, 160, 120),
}


class Tile:
    """
    Một ô vuông gạch trên bản đồ.
    """

    def __init__(self, col, row, loai, is_solid=False):
        """Khởi tạo một ô gạch tại tọa độ hàng/cột nhất định."""
        self.col = col           # Chỉ số cột
        self.row = row           # Chỉ số hàng
        self.loai = loai         # Tên loại (dirt, wall...)
        self.is_solid = is_solid # Có chặn xe tăng không
        self.destroyed = False   # Trạng thái đã nổ (dùng cho thùng phuy)
        self.image = self._tai_hinh_anh() # Hình ảnh hiển thị
        self._bg_image = None    # Ảnh nền (dùng khi thùng nổ để lộ nền đất bên dưới)

    def _tai_hinh_anh(self):
        """Tải hình ảnh từ bộ nhớ và áp dụng các hiệu ứng đồ họa."""
        duong_dan = _LOAI_ANH.get(self.loai)
        if duong_dan:
            try:
                # Load ảnh gốc
                anh = pygame.image.load(duong_dan).convert_alpha()
                anh = pygame.transform.scale(anh, (TILE_SIZE, TILE_SIZE))
                
                # --- HIỆU ỨNG VIỀN (Outline) ---
                # Tạo viền mờ cho các vật thể để chúng nổi bật hơn trên nền đất
                if self.loai in (LoaiTile.BARREL, LoaiTile.SANDBAG, LoaiTile.TREE_LARGE):
                    bordered = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    mask = pygame.mask.from_surface(anh)
                    outline = mask.to_surface(setcolor=(255, 255, 255, 100), unsetcolor=(0, 0, 0, 0))
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                        bordered.blit(outline, (dx, dy))
                    bordered.blit(anh, (0, 0))
                    anh = bordered
                    
                return anh
            except (pygame.error, FileNotFoundError):
                pass

        # --- TỰ VẼ NẾU THIẾU ẢNH (Fallback) ---
        mau = _MAU_TILE.get(self.loai, (160, 120, 80))
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surface.fill(mau)

        if self.loai == LoaiTile.WALL:
            # Vẽ vân gạch cho tường
            pygame.draw.rect(surface, (40, 40, 40), (0, 0, TILE_SIZE, TILE_SIZE), 2)
            for i in range(0, TILE_SIZE, 16):
                offset = 8 if (i // 16) % 2 else 0
                for j in range(offset, TILE_SIZE, 32):
                    pygame.draw.rect(surface, (50, 50, 50), (j, i, 30, 14), 1)
        elif self.loai == LoaiTile.TREE_LARGE:
            # Vẽ cây cổ thụ đơn giản bằng vòng tròn
            pygame.draw.rect(surface, (60, 40, 20), (28, 32, 8, 32))
            pygame.draw.circle(surface, (40, 120, 40), (32, 24), 16)
        return surface

    def is_blocking(self):
        """Kiểm tra xem ô này có đang chặn xe tăng không."""
        if self.destroyed: return False # Nếu thùng nổ rồi thì không chặn nữa
        return self.is_solid

    def is_barrel(self):
        """Kiểm tra đây có phải thùng phuy chưa nổ không."""
        return self.loai == LoaiTile.BARREL and not self.destroyed

    def set_bg_image(self, bg_image):
        """Lưu lại ảnh nền của ô này (VD: đất hoặc cỏ dưới chân cái thùng)."""
        self._bg_image = bg_image

    def destroy(self, surrounding_tiles=None):
        """
        Thực hiện phá hủy ô gạch (Chỉ áp dụng cho Thùng phuy).
        """
        if self.loai == LoaiTile.BARREL and not self.destroyed:
            self.destroyed = True
            self.is_solid = False # Cho phép xe đi qua sau khi nổ

            # Thay thế ảnh thùng phuy bằng ảnh nền để bản đồ liền mạch
            if self._bg_image:
                self.image = self._bg_image
            else:
                self.image = self._tao_anh_nen(surrounding_tiles)
            return True
        return False

    def _tao_anh_nen(self, surrounding_tiles=None):
        """
        Thuật toán thông minh tự động tính toán màu nền.
        Nếu nổ một cái thùng, nó sẽ nhìn sang các ô bên cạnh để đoán xem 
        nên tô màu gì cho ô gạch này (Cỏ hay Cát).
        """
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        default_color = _MAU_TILE.get(LoaiTile.GRASS, (80, 160, 80))
        surface.fill(default_color)

        if surrounding_tiles:
            colors = []
            for tile in surrounding_tiles:
                if not hasattr(tile, 'loai') or tile.loai == LoaiTile.BARREL:
                    continue
                # Lấy màu từ danh sách hàng xóm
                mau = _MAU_TILE.get(tile.loai, None)
                if mau: colors.append(mau)

            if colors:
                # Tính trung bình màu của các ô xung quanh (trừ tường)
                non_wall = [c for c in colors if c != _MAU_TILE.get(LoaiTile.WALL)]
                use_colors = non_wall if non_wall else colors
                avg = [sum(c[i] for c in use_colors) // len(use_colors) for i in range(3)]
                surface.fill(avg)

                # Thêm hiệu ứng hạt nhiễu (Noise) cho nền trông tự nhiên hơn
                import random
                for i in range(0, TILE_SIZE, 8):
                    for j in range(0, TILE_SIZE, 8):
                        if (i + j) % 16 == 0:
                            v = (max(0, min(255, avg[0] + random.randint(-5, 5))),
                                 max(0, min(255, avg[1] + random.randint(-5, 5))),
                                 max(0, min(255, avg[2] + random.randint(-5, 5))))
                            pygame.draw.rect(surface, v, (i, j, 8, 8))
        return surface

    def get_pixel_pos(self):
        """Tính toán tọa độ pixel tại tâm của ô gạch này."""
        return (self.col * TILE_SIZE + TILE_SIZE // 2,
                self.row * TILE_SIZE + TILE_SIZE // 2)
