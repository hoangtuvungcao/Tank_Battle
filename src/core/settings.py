"""
Settings — Hằng số cấu hình toàn bộ game Tank Battle.

Đây là nơi tập trung tất cả các thông số điều chỉnh game.
Việc tách biệt hằng số giúp dễ dàng cân bằng game (Game Balance) mà không cần can thiệp sâu vào logic code.
"""

# ==========================================
# CẤU HÌNH MÀN HÌNH
# ==========================================
SCREEN_WIDTH = 1024       # Độ phân giải chiều ngang của cửa sổ game (pixel)
SCREEN_HEIGHT = 768       # Độ phân giải chiều dọc của cửa sổ game (pixel)
FPS = 60                  # Số khung hình trên mỗi giây (Frame Per Second)
FULLSCREEN = False        # Mặc định không để chế độ toàn màn hình khi khởi động

# ==========================================
# THÔNG SỐ BẢN ĐỒ
# ==========================================
TILE_SIZE = 64            # Kích thước của một ô vuông địa hình (pixel). Mọi ảnh địa hình phải là 64x64.
MAP_COLS = 20             # Số lượng cột tối thiểu của bản đồ
MAP_ROWS = 10             # Số lượng hàng tối thiểu của bản đồ

# ==========================================
# THÔNG SỐ XE TĂNG CHUNG (Mặc định)
# ==========================================
TANK_SPEED = 200.0              # Tốc độ di chuyển tiến/lùi (pixel trên giây)
TANK_ROTATION_SPEED = 180.0     # Tốc độ xoay thân xe (độ trên giây)
TURRET_ROTATION_SPEED = 270.0   # Tốc độ xoay nòng súng độc lập (độ trên giây)
TANK_WIDTH = 48                 # Chiều rộng vật lý của xe tăng (hitbox)
TANK_HEIGHT = 48                # Chiều cao vật lý của xe tăng (hitbox)
TANK_MAX_HEALTH = 100           # Lượng máu tối đa mặc định
TANK_SHOOT_DELAY = 0.3          # Thời gian nạp đạn (giây)

# ==========================================
# THÔNG SỐ ĐẠN (Bullet)
# ==========================================
BULLET_SPEED = 400.0       # Tốc độ bay của viên đạn (pixel trên giây)
BULLET_DAMAGE = 25          # Lượng máu trừ đi khi trúng một viên đạn
BULLET_MAX_DISTANCE = 600.0 # Tầm bắn tối đa của đạn trước khi tự biến mất
BULLET_RADIUS = 4           # Kích thước va chạm của viên đạn

# ==========================================
# THÔNG SỐ RIÊNG CHO NGƯỜI CHƠI (Player)
# ==========================================
PLAYER_HEALTH = 150         # Máu người chơi (Cao hơn để tăng độ bền)
PLAYER_SPEED = 250.0        # Tốc độ di chuyển nhanh hơn để dễ né đạn
PLAYER_ROTATION_SPEED = 200.0 # Khả năng xoay chuyển linh hoạt hơn
PLAYER_TURRET_SPEED = 300.0  # Tốc độ xoay nòng súng cực nhanh
PLAYER_SHOOT_DELAY = 0.25    # Tốc độ bắn nhanh hơn địch một chút
PLAYER_LIVES = 3             # Số mạng (hồi sinh) cho phép trong một lượt chơi
RESPAWN_DELAY = 2.0          # Thời gian chờ (giây) trước khi xe mới xuất hiện
RESPAWN_INVINCIBLE = 2.0     # Thời gian bất tử (giây) sau khi vừa hồi sinh để tránh bị bắn ngay

# ==========================================
# THÔNG SỐ RIÊNG CHO KẺ ĐỊCH (Enemy)
# ==========================================
ENEMY_HEALTH = 100           # Máu địch ở mức cơ bản
ENEMY_SPEED = 200.0          # Tốc độ địch ở mức trung bình
ENEMY_SHOOT_DELAY = 0.5      # Địch nạp đạn lâu hơn người chơi

# ==========================================
# BẢNG MÀU RGB (Red, Green, Blue)
# ==========================================
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (200, 0, 0)
COLOR_GREEN = (0, 200, 0)
COLOR_BLUE = (0, 0, 200)
COLOR_YELLOW = (255, 255, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_DARK_GRAY = (64, 64, 64)
COLOR_LIGHT_GRAY = (192, 192, 192)
COLOR_BEIGE = (200, 180, 140)
COLOR_BROWN = (139, 90, 43)
COLOR_SAND = (210, 180, 120)
COLOR_BG_MENU = (30, 30, 50)    # Màu nền tối cho Menu chính

# ==========================================
# QUẢN LÝ ĐƯỜNG DẪN TÀI NGUYÊN (Assets Path)
# ==========================================
ASSETS_DIR = "assets"           # Thư mục chứa tài nguyên gốc
IMAGES_DIR = f"{ASSETS_DIR}/images" # Thư mục chứa toàn bộ ảnh
SOUNDS_DIR = f"{ASSETS_DIR}/sounds" # Thư mục chứa toàn bộ âm thanh
MAPS_DIR = "maps"               # Thư mục chứa các file cấu trúc bản đồ (.txt)

# Các thư mục con của ảnh
TANK_IMAGES_DIR = f"{IMAGES_DIR}/tanks"
BULLET_IMAGES_DIR = f"{IMAGES_DIR}/bullets"
ENVIRONMENT_IMAGES_DIR = f"{IMAGES_DIR}/environment"
OBSTACLE_IMAGES_DIR = f"{IMAGES_DIR}/obstacles"
SMOKE_IMAGES_DIR = f"{IMAGES_DIR}/smoke"
UI_IMAGES_DIR = f"{IMAGES_DIR}/ui"

# ==========================================
# THÔNG SỐ GIAO DIỆN (HUD)
# ==========================================
HUD_MARGIN = 10              # Khoảng cách từ mép màn hình đến các phần tử UI
HEALTH_BAR_WIDTH = 200       # Chiều rộng của thanh máu trên HUD
HEALTH_BAR_HEIGHT = 20       # Chiều cao của thanh máu trên HUD
MINIMAP_SIZE = 150           # Kích thước tối đa của bản đồ nhỏ
MINIMAP_ALPHA = 180          # Độ trong suốt của Minimap (0 là biến mất, 255 là đặc)

# ==========================================
# THÔNG SỐ HIỆU ỨNG (Particle Effects)
# ==========================================
PARTICLE_LIFETIME = 0.8         # Thời gian tồn tại của khói/nổ (giây)
EXPLOSION_PARTICLE_COUNT = 8    # Số lượng mảnh vụn bắn ra khi có vụ nổ

# ==========================================
# CÀI ĐẶT ÂM THANH
# ==========================================
MUSIC_VOLUME = 1.0    # Âm lượng nhạc nền mặc định (100%)
SFX_VOLUME = 1.0      # Âm lượng hiệu ứng mặc định (100%)

# Định nghĩa đường dẫn chi tiết cho từng file âm thanh
MUSIC_MENU = f"{SOUNDS_DIR}/menu_music.wav"       
MUSIC_GAME = f"{SOUNDS_DIR}/game_music.wav"       
SFX_SHOOT = f"{SOUNDS_DIR}/shoot.wav"             
SFX_EXPLOSION = f"{SOUNDS_DIR}/explosion.wav"     
SFX_HIT = f"{SOUNDS_DIR}/hit.wav"                 
SFX_BUTTON = f"{SOUNDS_DIR}/button_click.wav"     
SFX_LEVEL_UP = f"{SOUNDS_DIR}/level_up.wav"       
SFX_PLAYER_DIE = f"{SOUNDS_DIR}/player_die.wav"   
SFX_RESPAWN = f"{SOUNDS_DIR}/respawn.wav"         
SFX_ENEMY_HIT = f"{SOUNDS_DIR}/enemy_hit.wav"     
SFX_PLAYER_HIT = f"{SOUNDS_DIR}/player_hit.wav"   
SFX_VICTORY = f"{SOUNDS_DIR}/victory.wav"         

# ==========================================
# CẤU HÌNH TIẾN TRÌNH GAME
# ==========================================
MAX_LEVEL = 10                   # Số lượng màn chơi tối đa có sẵn
LEVEL_TRANSITION_DURATION = 2.0  # Thời gian hiển thị chữ "MÀN X" khi qua cửa

# ==========================================
# TÙY CHỌN XE TĂNG
# ==========================================
# Danh sách các màu xe tăng người chơi có thể chọn ở Menu
TANK_COLORS = ["green", "blue", "beige", "black"]
# Tên hiển thị tương ứng với mã màu
TANK_COLOR_NAMES = {
    "green": "Xanh Lá",
    "blue": "Xanh Dương",
    "beige": "Vàng Nhạt",
    "black": "Đen"
}

# ==========================================
# THÔNG TIN PHIÊN BẢN
# ==========================================
GAME_TITLE = "Tank Battle"
GAME_VERSION = "2.0"
