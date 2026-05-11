"""
GameMap — Hệ thống quản lý và hiển thị bản đồ.

File này chịu trách nhiệm:
- Đọc file văn bản (.txt) và chuyển hóa thành dữ liệu các ô gạch (Tiles).
- Quản lý vị trí xuất phát (Spawn) của người chơi và kẻ địch.
- Kiểm tra va chạm giữa vật thể (xe tăng, đạn) với địa hình.
- Tối ưu hóa việc vẽ bản đồ (chỉ vẽ những ô đang xuất hiện trên màn hình).
"""

import pygame
from src.core.settings import TILE_SIZE, MAPS_DIR
from src.world.tile import Tile, KY_TU_TILE, LoaiTile


class GameMap:
    """
    Lớp chứa dữ liệu lưới ô vuông 2D của một màn chơi.
    """

    def __init__(self):
        """Khởi tạo một bản đồ trống."""
        self.tiles = []           # Mảng 2D chứa các đối tượng Tile: [hàng][cột]
        self.player_spawn = (0, 0) # Tọa độ pixel để đặt người chơi
        self.enemy_spawns = []    # Danh sách các tọa độ pixel để đặt kẻ địch
        self.width = 0            # Số lượng cột của bản đồ
        self.height = 0           # Số lượng hàng của bản đồ

    def load_from_file(self, filename):
        """
        Đọc tệp tin .txt và dựng nên bản đồ.
        """
        self.tiles = []
        self.enemy_spawns = []

        try:
            # Mở file với định dạng utf-8 để đọc các ký hiệu bản đồ
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            # Nếu không thấy file (VD: Level chưa được tạo), tự tạo map trống để tránh crash
            print(f"[Cảnh báo] Không tìm thấy bản đồ: {filename}")
            self._tao_mac_dinh()
            return

        # Làm sạch dữ liệu: Xóa các khoảng trắng thừa và dòng trống
        lines = [line.rstrip('\n').rstrip('\r') for line in lines]
        lines = [line for line in lines if line.strip()]
        if not lines:
            self._tao_mac_dinh()
            return

        # Xác định kích thước bản đồ
        self.height = len(lines)
        self.width = max(len(line) for line in lines)

        # Duyệt từng ký tự trong file text để tạo các ô gạch (Tile) tương ứng
        for row_idx, line in enumerate(lines):
            row_tiles = []
            for col_idx, ky_tu in enumerate(line):
                # Tra cứu thông tin loại gạch dựa trên ký tự (VD: '#' là tường, '.' là đất)
                info = KY_TU_TILE.get(ky_tu, KY_TU_TILE['.'])
                # Tạo đối tượng Tile
                tile = Tile(col_idx, row_idx, info["loai"], info["is_solid"])
                row_tiles.append(tile)

                # Nếu là ký tự 'T', ghi nhớ vị trí này làm điểm xuất phát cho người chơi
                if ky_tu == 'T':
                    self.player_spawn = tile.get_pixel_pos()
                # Nếu là ký tự 'E', thêm vào danh sách điểm xuất phát cho kẻ địch
                elif ky_tu == 'E':
                    self.enemy_spawns.append(tile.get_pixel_pos())

            # Nếu dòng này ngắn hơn chiều rộng tối đa, tự động lấp đầy bằng ô Đất
            while len(row_tiles) < self.width:
                tile = Tile(len(row_tiles), row_idx, LoaiTile.DIRT, False)
                row_tiles.append(tile)
            self.tiles.append(row_tiles)

        # Kỹ thuật Pre-bake: Tính toán sẵn ảnh nền cho các vật thể có độ trong suốt (như cây, thùng phuy)
        self._prebake_barrel_backgrounds()

    def _prebake_barrel_backgrounds(self):
        """
        Tối ưu hóa hình ảnh: Ghép ảnh nền địa hình vào dưới các vật thể.
        Giúp thùng phuy/cây cối trông tự nhiên hơn và không bị lỗi nền đen khi nổ.
        """
        for row in range(self.height):
            for col in range(self.width):
                tile = self.tiles[row][col]
                # Chỉ xử lý các ô là vật thể đặt lên trên nền (không phải bản thân cái nền)
                if tile.loai in (LoaiTile.BARREL, LoaiTile.SANDBAG, LoaiTile.TREE_LARGE, LoaiTile.TREE_SMALL):
                    # Lấy thông tin các ô xung quanh để đoán xem nền ở đây nên là gì (cỏ, cát hay đất)
                    neighbors = self._get_neighbors(row, col)
                    # Tạo ảnh nền giả lập
                    bg = tile._tao_anh_nen(neighbors)
                    tile.set_bg_image(bg)
                    
                    # Kết hợp: Vẽ vật thể đè lên ảnh nền vừa tạo
                    if tile.image:
                        new_img = bg.copy()
                        new_img.blit(tile.image, (0, 0))
                        tile.image = new_img # Lưu lại ảnh đã được kết hợp hoàn chỉnh

    def _get_neighbors(self, row, col):
        """Lấy danh sách 8 ô gạch lân cận xung quanh một tọa độ hàng, cột."""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue # Bỏ qua chính ô đó
                r, c = row + dr, col + dc
                # Kiểm tra biên bản đồ
                if 0 <= r < self.height and 0 <= c < self.width:
                    neighbors.append(self.tiles[r][c])
        return neighbors

    def _tao_mac_dinh(self):
        """Tạo ra một bản đồ cơ bản bao quanh bởi tường (Phòng hờ trường hợp lỗi file)."""
        self.width, self.height = 20, 10
        self.player_spawn = (3 * TILE_SIZE, 2 * TILE_SIZE)
        self.enemy_spawns = [(15 * TILE_SIZE, 7 * TILE_SIZE)]
        for row in range(self.height):
            row_tiles = []
            for col in range(self.width):
                # Viền ngoài là tường, bên trong là đất
                is_wall = (row == 0 or row == self.height - 1 or col == 0 or col == self.width - 1)
                tile = Tile(col, row, LoaiTile.WALL if is_wall else LoaiTile.DIRT, is_wall)
                row_tiles.append(tile)
            self.tiles.append(row_tiles)

    # ==========================================
    # LOGIC KIỂM TRA VA CHẠM
    # ==========================================

    def get_tile_at(self, pixel_x, pixel_y):
        """Chuyển đổi tọa độ pixel (VD: 128, 64) sang đối tượng Tile tại đó."""
        col = int(pixel_x // TILE_SIZE)
        row = int(pixel_y // TILE_SIZE)
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.tiles[row][col]
        return None

    def is_wall_at(self, pixel_x, pixel_y):
        """Kiểm tra xem tọa độ này có phải là tường KHÔNG thể bắn xuyên qua không."""
        tile = self.get_tile_at(pixel_x, pixel_y)
        if tile is None: return True # Ngoài bản đồ coi như tường cứng
        # Thùng phuy (Barrel) KHÔNG chặn đạn (để đạn bay vào làm nổ thùng)
        if tile.is_barrel(): return False
        return tile.is_blocking() # Trả về True nếu là Tường hoặc Bao cát

    def is_solid_at(self, pixel_x, pixel_y):
        """Kiểm tra xem tọa độ này có vật cản xe tăng không (Bao gồm cả thùng phuy)."""
        tile = self.get_tile_at(pixel_x, pixel_y)
        if tile is None: return True
        return tile.is_blocking() # Xe tăng bị chặn bởi Tường, Bao cát và cả Thùng phuy

    # ==========================================
    # CÁC HÀM TIỆN ÍCH
    # ==========================================

    def get_player_spawn(self):
        """Trả về tọa độ (x, y) để đặt người chơi."""
        return self.player_spawn

    def get_enemy_spawns(self):
        """Trả về danh sách các tọa độ (x, y) để đặt kẻ địch."""
        return self.enemy_spawns

    def get_pixel_width(self):
        """Tính tổng chiều rộng bản đồ theo đơn vị pixel."""
        return self.width * TILE_SIZE

    def get_pixel_height(self):
        """Tính tổng chiều cao bản đồ theo đơn vị pixel."""
        return self.height * TILE_SIZE

    # ==========================================
    # RENDER ĐỒ HỌA
    # ==========================================

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        Vẽ bản đồ lên màn hình (Kỹ thuật tối ưu Frustum Culling).
        Chỉ vẽ những ô gạch nằm trong tầm nhìn của Camera.
        """
        screen_w = screen.get_width()
        screen_h = screen.get_height()

        # Xác định phạm vi các hàng và cột nằm trong khung hình
        start_col = max(0, camera_x // TILE_SIZE)
        end_col = min(self.width, (camera_x + screen_w) // TILE_SIZE + 2)
        start_row = max(0, camera_y // TILE_SIZE)
        end_row = min(self.height, (camera_y + screen_h) // TILE_SIZE + 2)

        # Duyệt qua các ô trong phạm vi camera và vẽ chúng
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile = self.tiles[row][col]
                # Tọa độ vẽ = Tọa độ gốc - Độ lệch camera
                draw_x = col * TILE_SIZE - camera_x
                draw_y = row * TILE_SIZE - camera_y
                screen.blit(tile.image, (draw_x, draw_y))
