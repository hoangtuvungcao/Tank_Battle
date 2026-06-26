"""
Tank — Lớp cơ sở cho tất cả xe tăng trong game.

File này chứa logic quan trọng nhất về việc xe tăng di chuyển như thế nào,
xoay nòng ra sao, và làm thế nào để vẽ hình ảnh xe lên màn hình một cách chính xác nhất.
"""

import pygame  # Thư viện đồ họa chính dùng để vẽ hình ảnh, tạo hình chữ nhật và xử lý màn hình
import math  # Thư viện toán học dùng để tính góc, khoảng cách, vector và phép quay
from src.core.settings import (  # Nhập các hằng số cấu hình cho xe tăng từ file settings
    TANK_WIDTH,  # Chiều rộng của xe tăng theo thiết kế game
    TANK_HEIGHT,  # Chiều cao của xe tăng theo thiết kế game
    TANK_SPEED,  # Tốc độ di chuyển mặc định của xe tăng
    TANK_ROTATION_SPEED,  # Tốc độ quay thân xe theo đơn vị độ/giây
    TURRET_ROTATION_SPEED,  # Tốc độ quay nòng súng theo đơn vị độ/giây
    TANK_MAX_HEALTH,  # Máu tối đa mặc định của xe tăng
    TANK_SHOOT_DELAY,  # Thời gian chờ giữa hai lần bắn
    TANK_IMAGES_DIR,  # Đường dẫn thư mục chứa ảnh của xe tăng
    BULLET_SPEED,  # Tốc độ bay của đạn
    BULLET_DAMAGE,  # Sát thương của mỗi viên đạn
    TILE_SIZE  # Kích thước mỗi ô bản đồ để tính vị trí tương ứng
)


class Tank:  # Định nghĩa lớp cơ sở chung cho mọi xe tăng trong trò chơi
    """
    Lớp cha định nghĩa mọi hành vi chung của xe tăng (cả của người chơi và máy).
    """

    def __init__(self, x=0, y=0, color="green", health=100, speed=200.0):  # Khởi tạo một đối tượng xe tăng với vị trí, màu sắc, máu và tốc độ
        """
        Khởi tạo các thông số ban đầu cho xe tăng.
        """
        self.x = float(x)  # Lưu tọa độ X dưới dạng số thực để di chuyển mượt mà hơn
        self.y = float(y)  # Lưu tọa độ Y dưới dạng số thực để di chuyển mượt mà hơn
        self.color = color  # Ghi nhớ màu sắc của xe tăng để chọn đúng hình ảnh và màu sắc

        self.angle = 0.0  # Khởi tạo góc quay của thân xe bằng 0 radian
        self.turret_angle = 0.0  # Khởi tạo góc quay của nòng súng bằng 0 radian

        self.speed = speed  # Gán tốc độ di chuyển cho xe tăng
        self.rotation_speed = TANK_ROTATION_SPEED  # Gán tốc độ quay thân xe từ file cấu hình
        self.turret_rotation_speed = TURRET_ROTATION_SPEED  # Gán tốc độ quay nòng súng từ file cấu hình

        self.health = health  # Gán giá trị máu hiện tại cho xe tăng
        self.max_health = health  # Gán giá trị máu tối đa bằng máu ban đầu
        self.alive = True  # Đánh dấu xe tăng đang còn sống
        self.name = "Tank"  # Đặt tên mặc định cho xe tăng

        self.shoot_cooldown = 0.0  # Khởi tạo bộ đếm thời gian chờ để bắn tiếp
        self.shoot_delay = TANK_SHOOT_DELAY  # Gán khoảng thời gian giữa hai lần bắn

        self.width = TANK_WIDTH  # Gán chiều rộng hình ảnh và va chạm của xe tăng
        self.height = TANK_HEIGHT  # Gán chiều cao hình ảnh và va chạm của xe tăng
        self.rect = pygame.Rect(0, 0, self.width, self.height)  # Tạo một khung hình chữ nhật dùng để kiểm tra va chạm
        self.rect.center = (int(self.x), int(self.y))  # Đặt trung tâm hình chữ nhật tại vị trí hiện tại của xe tăng

        self.body_image = None  # Khởi tạo biến lưu ảnh thân xe với giá trị trống
        self.turret_image = None  # Khởi tạo biến lưu ảnh nòng súng với giá trị trống
        self._tai_hinh_anh()  # Gọi hàm tải ảnh ngay sau khi khởi tạo xe tăng

    def _tai_hinh_anh(self):  # Tải và chuẩn bị tất cả hình ảnh cần thiết cho xe tăng
        """Tải và chuẩn bị hình ảnh xe tăng từ bộ nhớ."""
        cap_color = self.color.capitalize()  # Chuyển màu sang dạng chữ hoa đầu để khớp tên file ảnh

        try:  # Bắt đầu khối thử tải ảnh thân xe từ file
            body = pygame.image.load(f"{TANK_IMAGES_DIR}/tank{cap_color}.png").convert_alpha()  # Tải hình ảnh thân xe có nền trong suốt
            body = pygame.transform.scale(body, (self.width, self.height))  # Đổi kích thước ảnh thân xe cho đúng với kích thước xe tăng
            self.body_image = pygame.transform.rotate(body, -90)  # Xoay ảnh thân xe để đúng hướng ban đầu của game
        except (pygame.error, FileNotFoundError):  # Nếu không tìm thấy file ảnh thì dùng hình vẽ thay thế
            self.body_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)  # Tạo một bề mặt hình ảnh trong suốt để vẽ thay thế
            bang_mau = {"green": (0, 180, 0), "blue": (0, 0, 180), "beige": (180, 160, 120), "black": (60, 60, 60)}  # Bảng màu dự phòng cho các màu xe tăng
            pygame.draw.rect(self.body_image, bang_mau.get(self.color, (0, 180, 0)), (4, 4, self.width - 8, self.height - 8), border_radius=4)  # Vẽ một hình chữ nhật màu làm thân xe nếu ảnh gốc không tồn tại

        try:  # Bắt đầu khối thử tải ảnh nòng súng từ file
            turret = pygame.image.load(f"{TANK_IMAGES_DIR}/barrel{cap_color}.png").convert_alpha()  # Tải hình ảnh nòng súng có nền trong suốt
            turret = pygame.transform.scale(turret, (16, 40))  # Đổi kích thước nòng súng cho vừa vặn với xe tăng
            self.turret_image = pygame.transform.rotate(turret, -90)  # Xoay nòng súng để đúng hướng ban đầu
        except (pygame.error, FileNotFoundError):  # Nếu không tìm thấy file ảnh thì dùng hình vẽ thay thế
            self.turret_image = pygame.Surface((40, 16), pygame.SRCALPHA)  # Tạo bề mặt hình ảnh trong suốt cho nòng súng thay thế
            bang_mau = {"green": (0, 150, 0), "blue": (0, 0, 150), "beige": (150, 130, 100), "black": (40, 40, 40)}  # Bảng màu dự phòng cho nòng súng
            pygame.draw.rect(self.turret_image, bang_mau.get(self.color, (0, 150, 0)), (0, 2, 40, 12))  # Vẽ một thanh hình chữ nhật màu làm nòng súng nếu ảnh không có

        try:  # Bắt đầu khối thử tải ảnh bánh xích từ file
            tracks = pygame.image.load(f"{TANK_IMAGES_DIR}/tracksLarge.png").convert_alpha()  # Tải hình ảnh bánh xích có nền trong suốt
            tracks = pygame.transform.scale(tracks, (self.width, self.height))  # Đổi kích thước ảnh bánh xích cho đúng với xe tăng
            self.tracks_image = pygame.transform.rotate(tracks, -90)  # Xoay ảnh bánh xích sao cho khớp với hướng xe tăng
        except (pygame.error, FileNotFoundError):  # Nếu không đọc được ảnh thì đặt giá trị trống
            self.tracks_image = None  # Gán None cho bánh xích nếu ảnh không tồn tại

    def _cap_nhat_rect(self):  # Đồng bộ khung hình chữ nhật va chạm với vị trí thực của xe tăng
        """Đồng bộ hóa hình chữ nhật va chạm với tọa độ thực tế của xe."""
        self.rect.center = (int(self.x), int(self.y))  # Đặt trung tâm của rect tại vị trí hiện tại của xe tăng

    def get_rect(self):  # Trả về khung chữ nhật va chạm để các module khác dùng
        """Cung cấp hình chữ nhật va chạm cho các module khác (va chạm tường, đạn)."""
        return self.rect  # Trả về đối tượng rect đang dùng cho kiểm tra va chạm

    def update(self, dt):  # Cập nhật trạng thái của xe tăng sau mỗi khung hình
        """Cập nhật logic của xe tăng sau mỗi khung hình."""
        if self.shoot_cooldown > 0:  # Nếu thời gian chờ bắn vẫn còn thì giảm dần
            self.shoot_cooldown -= dt  # Giảm cooldown theo thời gian đã trôi qua
        self._cap_nhat_rect()  # Cập nhật lại rect sau khi thay đổi vị trí hoặc trạng thái

    def move_forward(self, dt):  # Di chuyển xe tăng về phía trước theo hướng hiện tại
        """Tiến về phía trước dựa theo góc xoay hiện tại của thân xe."""
        self.x += math.cos(self.angle) * self.speed * dt  # Cập nhật tọa độ X theo hướng hiện tại và tốc độ
        self.y += math.sin(self.angle) * self.speed * dt  # Cập nhật tọa độ Y theo hướng hiện tại và tốc độ
        self._cap_nhat_rect()  # Cập nhật lại rect sau khi di chuyển

    def move_backward(self, dt):  # Di chuyển xe tăng lùi về phía sau với tốc độ thấp hơn
        """Lùi về phía sau (tốc độ lùi chỉ bằng 60% tốc độ tiến)."""
        self.x -= math.cos(self.angle) * self.speed * 0.6 * dt  # Cập nhật X khi lùi theo hướng ngược lại
        self.y -= math.sin(self.angle) * self.speed * 0.6 * dt  # Cập nhật Y khi lùi theo hướng ngược lại
        self._cap_nhat_rect()  # Cập nhật lại rect sau khi lùi

    def rotate_body_left(self, dt):  # Xoay thân xe sang trái
        """Xoay thân xe sang bên trái."""
        self.angle -= math.radians(self.rotation_speed) * dt  # Giảm góc quay của thân xe theo tốc độ quay

    def rotate_body_right(self, dt):  # Xoay thân xe sang phải
        """Xoay thân xe sang bên phải."""
        self.angle += math.radians(self.rotation_speed) * dt  # Tăng góc quay của thân xe theo tốc độ quay

    def rotate_turret_to_angle(self, target_angle, dt):  # Xoay nòng súng về một góc mục tiêu cụ thể
        """Xoay nòng súng về phía một góc xác định một cách mượt mà."""
        diff = target_angle - self.turret_angle  # Tính chênh lệch góc giữa mục tiêu và góc hiện tại
        while diff > math.pi:  # Nếu chênh lệch vượt quá nửa vòng thì giảm xuống
            diff -= 2 * math.pi  # Điều chỉnh góc về phạm vi ngắn nhất
        while diff < -math.pi:  # Nếu chênh lệch nhỏ hơn âm nửa vòng thì tăng lên
            diff += 2 * math.pi  # Điều chỉnh góc về phạm vi ngắn nhất

        max_rot = math.radians(self.turret_rotation_speed) * dt  # Tính góc tối đa nòng súng có thể quay trong khung hình này
        if abs(diff) < max_rot:  # Nếu chênh lệch nhỏ hơn mức quay tối đa thì đưa thẳng về mục tiêu
            self.turret_angle = target_angle  # Gán góc nòng súng bằng góc mục tiêu
        elif diff > 0:  # Nếu mục tiêu nằm bên phải so với góc hiện tại thì quay phải
            self.turret_angle += max_rot  # Tăng góc nòng súng một bước
        else:  # Nếu mục tiêu nằm bên trái thì quay trái
            self.turret_angle -= max_rot  # Giảm góc nòng súng một bước

    def rotate_turret_to_target(self, target_x, target_y, dt):  # Xoay nòng súng về hướng một điểm mục tiêu trên màn hình
        """Xoay nòng súng về phía tọa độ mục tiêu một cách mượt mà."""
        desired = math.atan2(target_y - self.y, target_x - self.x)  # Tính góc cần quay để nhìn thẳng vào điểm mục tiêu
        diff = desired - self.turret_angle  # Tính chênh lệch giữa góc mục tiêu và góc hiện tại
        while diff > math.pi:  # Nếu chênh lệch vượt quá nửa vòng thì chỉnh lại
            diff -= 2 * math.pi  # Giảm chênh lệch về khoảng gần nhất
        while diff < -math.pi:  # Nếu chênh lệch nhỏ hơn âm nửa vòng thì chỉnh lại
            diff += 2 * math.pi  # Tăng chênh lệch về khoảng gần nhất

        max_rot = math.radians(self.turret_rotation_speed) * dt  # Tính góc xoay tối đa của nòng súng trong khung hình
        if abs(diff) < max_rot:  # Nếu chênh lệch nhỏ thì gán thẳng về góc mục tiêu
            self.turret_angle = desired  # Gán góc nòng súng bằng góc tính được
        elif diff > 0:  # Nếu mục tiêu ở phía bên phải thì quay phải
            self.turret_angle += max_rot  # Tăng góc nòng súng lên
        else:  # Nếu mục tiêu ở phía bên trái thì quay trái
            self.turret_angle -= max_rot  # Giảm góc nòng súng xuống

    def shoot(self):  # Thực hiện bắn một viên đạn từ nòng súng
        """Thực hiện bắn đạn."""
        if self.shoot_cooldown > 0:  # Nếu vẫn đang trong thời gian chờ thì không bắn
            return None  # Trả về None để báo rằng lần bắn bị chặn

        self.shoot_cooldown = self.shoot_delay  # Đặt lại thời gian chờ sau khi bắn thành công

        muzzle_dist = 30  # Khoảng cách từ tâm xe đến đầu nòng súng để tạo điểm xuất phát đạn
        bx = self.x + math.cos(self.turret_angle) * muzzle_dist  # Tính tọa độ X ban đầu của viên đạn
        by = self.y + math.sin(self.turret_angle) * muzzle_dist  # Tính tọa độ Y ban đầu của viên đạn

        return {  # Trả về dữ liệu mô tả viên đạn vừa bắn
            "x": bx,  # Tọa độ X bắt đầu của viên đạn
            "y": by,  # Tọa độ Y bắt đầu của viên đạn
            "angle": self.turret_angle,  # Hướng bay của viên đạn
            "speed": BULLET_SPEED,  # Tốc độ bay của viên đạn
            "damage": BULLET_DAMAGE,  # Sát thương gây ra khi trúng mục tiêu
            "owner": self  # Ghi nhận chủ sở hữu để đạn không tự bắn trúng mình
        }

    def take_damage(self, damage):  # Xử lý khi xe tăng bị trúng đạn hoặc sát thương
        """Trừ máu khi xe tăng bị trúng đạn hoặc dính sát thương nổ."""
        self.health -= damage  # Giảm máu hiện tại theo sát thương nhận vào
        if self.health <= 0:  # Nếu máu giảm về 0 hoặc thấp hơn thì xe chết
            self.health = 0  # Đảm bảo máu không âm
            self.alive = False  # Đánh dấu xe tăng đã ngừng hoạt động

    def is_alive(self):  # Kiểm tra xem xe tăng còn sống hay không
        """Kiểm tra trạng thái sinh mạng."""
        return self.alive and self.health > 0  # Trả về True nếu còn sống và máu còn dương

    def get_distance_to(self, tx, ty):  # Tính khoảng cách từ xe tăng đến một điểm cho trước
        """Tính khoảng cách đường chim bay đến một điểm bất kỳ."""
        return math.sqrt((self.x - tx) ** 2 + (self.y - ty) ** 2)  # Dùng công thức khoảng cách Euclid giữa hai điểm

    def get_angle_to(self, tx, ty):  # Tính góc cần quay để nhìn thẳng vào một điểm cho trước
        """Tính góc cần xoay để nhìn thẳng vào một điểm bất kỳ."""
        return math.atan2(ty - self.y, tx - self.x)  # Tính góc hướng từ xe tới điểm mục tiêu

    def draw(self, screen, cam_x=0, cam_y=0):  # Vẽ toàn bộ xe tăng lên màn hình theo vị trí camera
        """Vẽ toàn bộ thành phần xe tăng lên màn hình."""
        if not self.alive:  # Nếu xe đã chết thì không vẽ nữa
            return  # Dừng hàm ngay lập tức

        sx = self.x - cam_x  # Tính tọa độ X trên màn hình sau khi trừ vị trí camera
        sy = self.y - cam_y  # Tính tọa độ Y trên màn hình sau khi trừ vị trí camera

        if getattr(self, 'tracks_image', None):  # Nếu có ảnh bánh xích thì vẽ trước
            rotated_tracks = pygame.transform.rotate(self.tracks_image, -math.degrees(self.angle))  # Xoay ảnh bánh xích theo góc thân xe
            tracks_rect = rotated_tracks.get_rect(center=(int(sx), int(sy)))  # Tạo khung hình chữ nhật cho bánh xích để đặt đúng vị trí
            screen.blit(rotated_tracks, tracks_rect)  # Vẽ bánh xích lên màn hình

        rotated_body = pygame.transform.rotate(self.body_image, -math.degrees(self.angle))  # Xoay ảnh thân xe theo góc hiện tại
        body_rect = rotated_body.get_rect(center=(int(sx), int(sy)))  # Tạo khung hình chữ nhật cho thân xe
        screen.blit(rotated_body, body_rect)  # Vẽ thân xe lên màn hình

        rotated_turret = pygame.transform.rotate(self.turret_image, -math.degrees(self.turret_angle))  # Xoay ảnh nòng súng theo góc hiện tại
        offset_dist = 15  # Khoảng cách nòng súng cần nhô ra so với tâm thân xe
        tx = sx + math.cos(self.turret_angle) * offset_dist  # Tính tọa độ X của nòng súng trên màn hình
        ty = sy + math.sin(self.turret_angle) * offset_dist  # Tính tọa độ Y của nòng súng trên màn hình
        turret_rect = rotated_turret.get_rect(center=(int(tx), int(ty)))  # Tạo khung hình chữ nhật cho nòng súng
        screen.blit(rotated_turret, turret_rect)  # Vẽ nòng súng lên màn hình

        bar_w = 40  # Độ rộng của thanh máu
        bar_h = 5  # Độ cao của thanh máu
        bx = int(sx - bar_w / 2)  # Tính tọa độ X bắt đầu của thanh máu
        by = int(sy - self.height / 2 - 15)  # Tính tọa độ Y bắt đầu của thanh máu
        pygame.draw.rect(screen, (0, 0, 0), (bx - 1, by - 1, bar_w + 2, bar_h + 2))  # Vẽ viền đen quanh thanh máu
        pygame.draw.rect(screen, (200, 0, 0), (bx, by, bar_w, bar_h))  # Vẽ phần nền đỏ của thanh máu
        if self.health > 0:  # Chỉ vẽ phần máu hiện tại nếu xe vẫn còn máu
            ratio = self.health / self.max_health  # Tính tỷ lệ máu còn lại
            hp_w = int(bar_w * ratio)  # Tính chiều rộng phần máu còn lại
            c = (0, 200, 0) if ratio > 0.5 else (255, 150, 0) if ratio > 0.25 else (255, 0, 0)  # Chọn màu thanh máu theo tỷ lệ còn lại
            if hp_w > 0:  # Chỉ vẽ phần máu còn lại nếu nó có kích thước dương
                pygame.draw.rect(screen, c, (bx, by, hp_w, bar_h))  # Vẽ phần máu hiện tại lên thanh máu

        if hasattr(self, 'name') and self.name:  # Nếu xe có tên và tên đó không rỗng thì hiển thị tên
            from src.core.font import get_font  # Nhập hàm lấy font từ module font
            font = get_font(14)  # Chọn font có kích thước 14 pixel
            name_surf = font.render(self.name, True, (255, 255, 255))  # Tạo ảnh chữ tên xe tăng với màu trắng
            shadow = font.render(self.name, True, (0, 0, 0))  # Tạo bản sao chữ tên có màu đen để làm bóng đổ
            name_rect = name_surf.get_rect(midbottom=(int(sx), by - 2))  # Tạo khung chữ để đặt tên đúng vị trí trên màn hình
            screen.blit(shadow, name_rect.move(1, 1))  # Vẽ bóng đổ của tên trước
            screen.blit(name_surf, name_rect)  # Vẽ tên xe lên màn hình

    def get_stats(self):  # Trả về dữ liệu thống kê mặc định cho xe tăng
        """Trả về dữ liệu thống kê mặc định (Sẽ được Player ghi đè)."""
        return {"kills": 0, "shots_fired": 0, "shots_hit": 0, "accuracy": 0}  # Trả về một bảng thống kê rỗng mặc định
