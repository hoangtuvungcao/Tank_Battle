"""
Player — Xe tăng do người chơi điều khiển.

Lớp này kế thừa từ lớp Tank và bổ sung các tính năng riêng biệt:
- Xử lý điều khiển từ bàn phím.
- Quản lý hệ thống tàng hình (Stealth) khi đi vào bụi rậm.
- Theo dõi các thống kê chiến đấu như số mạng tiêu diệt, độ chính xác.
"""

import pygame  # Thư viện đồ họa chính dùng để xử lý hình ảnh, âm thanh và nhập liệu của trò chơi
import math  # Thư viện toán học dùng để tính góc, vector và phép quay hình
from src.entities.tank import Tank  # Nhập lớp cha để lớp Player có thể kế thừa các hành vi chung của xe tăng
from src.core.settings import (  # Nhập các hằng số cấu hình cho người chơi từ file settings
    PLAYER_HEALTH,  # Máu tối đa của người chơi
    PLAYER_SPEED,  # Tốc độ di chuyển của người chơi
    PLAYER_ROTATION_SPEED,  # Tốc độ quay thân xe của người chơi
    PLAYER_TURRET_SPEED,  # Tốc độ quay nòng súng của người chơi
    PLAYER_SHOOT_DELAY,  # Thời gian chờ giữa lần bắn của người chơi
    TILE_SIZE  # Kích thước mỗi ô bản đồ để xác định vị trí trên map
)
from src.world.collision import Collision  # Nhập lớp xử lý va chạm để xe tăng không đi xuyên qua tường và vật cản


class Player(Tank):  # Khai báo lớp Player kế thừa từ lớp Tank để dùng các chức năng cơ bản của xe tăng
    """
    Xe tăng của người chơi — Sử dụng WASD để di chuyển và SPACE để bắn.
    """

    def __init__(self, x=0, y=0, color="green"):  # Khởi tạo đối tượng người chơi với vị trí ban đầu, màu sắc và các thông số cơ bản
        """
        Khởi tạo người chơi với các chỉ số ưu việt hơn so với kẻ địch.
        """
        super().__init__(x=x, y=y, color=color, health=PLAYER_HEALTH, speed=PLAYER_SPEED)  # Gọi hàm khởi tạo của lớp cha để thiết lập các thuộc tính chung của xe tăng

        self.name = "Bạn"  # Gán tên hiển thị cho người chơi trên màn hình

        self.rotation_speed = PLAYER_ROTATION_SPEED  # Ghi đè tốc độ quay thân xe bằng giá trị riêng của người chơi
        self.turret_rotation_speed = PLAYER_TURRET_SPEED  # Ghi đè tốc độ quay nòng súng bằng giá trị riêng của người chơi
        self.shoot_delay = PLAYER_SHOOT_DELAY  # Ghi đè thời gian chờ giữa các lần bắn bằng giá trị riêng của người chơi

        self.kills = 0  # Khởi tạo số kẻ địch đã tiêu diệt bằng 0
        self.shots_fired = 0  # Khởi tạo tổng số lần bắn bằng 0
        self.shots_hit = 0  # Khởi tạo số lần bắn trúng mục tiêu bằng 0

        self.in_stealth = False  # Khởi tạo trạng thái tàng hình là tắt ban đầu

    def handle_input(self, keys, mouse_pos, dt, map_data, cam_x=0, cam_y=0):  # Xử lý toàn bộ đầu vào từ người chơi để điều khiển xe tăng
        """
        Xử lý các phím bấm từ người chơi để điều khiển xe tăng.
        """
        old_x, old_y = self.x, self.y  # Lưu vị trí cũ trước khi di chuyển để có thể khôi phục nếu va chạm

        dx, dy = 0.0, 0.0  # Khởi tạo vector di chuyển theo trục X và Y
        if keys.get(pygame.K_w) or keys.get(pygame.K_UP):  # Nếu người chơi nhấn phím W hoặc phím mũi tên lên
            dy -= 1  # Giảm giá trị trục Y để xe đi lên trên màn hình
        if keys.get(pygame.K_s) or keys.get(pygame.K_DOWN):  # Nếu người chơi nhấn phím S hoặc phím mũi tên xuống
            dy += 1  # Tăng giá trị trục Y để xe đi xuống dưới màn hình
        if keys.get(pygame.K_a) or keys.get(pygame.K_LEFT):  # Nếu người chơi nhấn phím A hoặc phím mũi tên trái
            dx -= 1  # Giảm giá trị trục X để xe đi sang trái
        if keys.get(pygame.K_d) or keys.get(pygame.K_RIGHT):  # Nếu người chơi nhấn phím D hoặc phím mũi tên phải
            dx += 1  # Tăng giá trị trục X để xe đi sang phải

        if dx != 0 or dy != 0:  # Nếu có ít nhất một phím điều hướng đang được nhấn
            length = math.sqrt(dx * dx + dy * dy)  # Tính độ dài vector di chuyển để chuẩn hóa tốc độ khi đi chéo
            self.x += (dx / length) * self.speed * dt  # Cập nhật vị trí X của xe theo hướng di chuyển và thời gian khung hình
            self.y += (dy / length) * self.speed * dt  # Cập nhật vị trí Y của xe theo hướng di chuyển và thời gian khung hình

            target_angle = math.atan2(dy, dx)  # Tính góc hướng di chuyển dựa trên vector đầu vào
            diff = target_angle - self.angle  # Tính khoảng chênh lệch giữa góc hiện tại và góc mục tiêu
            while diff > math.pi:  # Nếu góc chênh lệch vượt quá nửa vòng thì điều chỉnh lại về phạm vi chuẩn
                diff -= 2 * math.pi  # Giảm góc đi một vòng đầy để giữ giá trị trong khoảng hợp lệ
            while diff < -math.pi:  # Nếu góc chênh lệch nhỏ hơn âm nửa vòng thì điều chỉnh lại về phạm vi chuẩn
                diff += 2 * math.pi  # Tăng góc lên một vòng đầy để giữ giá trị trong khoảng hợp lệ

            if abs(diff) > math.pi / 2:  # Nếu góc lệch quá lớn thì quay xe ngay lập tức về hướng mới
                self.angle = target_angle  # Gán góc thân xe bằng góc mục tiêu để đổi hướng nhanh
            else:  # Nếu góc lệch không quá lớn thì quay xe mượt mà hơn
                max_rot = math.radians(self.rotation_speed * 1.5) * dt  # Tính góc quay tối đa cho khung hình hiện tại
                if abs(diff) < max_rot:  # Nếu chênh lệch nhỏ hơn mức quay cho phép thì đặt ngay về mục tiêu
                    self.angle = target_angle  # Gán góc thân xe bằng góc mục tiêu
                else:  # Nếu vẫn còn cách xa mục tiêu thì quay từng bước cho mượt
                    self.angle += math.copysign(max_rot, diff)  # Thêm một bước quay có dấu phù hợp với hướng lệch

            self._cap_nhat_rect()  # Cập nhật khung va chạm sau khi thay đổi vị trí và góc quay của xe

        Collision.resolve_tank_wall(self, map_data, old_x, old_y)  # Gọi thuật toán va chạm trượt để xe không bị kẹt vào tường

        self.turret_angle = self.angle  # Giữ nòng súng luôn nhìn theo hướng của thân xe

        tile = map_data.get_tile_at(self.x, self.y) if map_data else None  # Lấy thông tin ô bản đồ mà xe đang đứng để kiểm tra địa hình
        self.in_stealth = (tile is not None and tile.loai in ["tree_small", "tree_large"])  # Nếu xe đứng trên bụi cây thì bật trạng thái tàng hình

    def handle_shoot(self):  # Gọi hàm bắn và cập nhật thống kê bắn của người chơi
        """
        Khai hỏa và ghi nhận thống kê bắn.
        """
        data = self.shoot()  # Gọi hàm bắn của lớp cha để tạo ra một viên đạn mới
        if data:  # Nếu việc bắn thành công và không bị chặn bởi thời gian hồi chiêu
            self.shots_fired += 1  # Tăng số lần bắn lên 1
        return data  # Trả về dữ liệu viên đạn vừa bắn nếu có

    def add_kill(self):  # Tăng số mạng tiêu diệt của người chơi lên 1
        """Ghi nhận khi người chơi tiêu diệt được một kẻ địch."""
        self.kills += 1  # Tăng biến đếm số kẻ địch đã tiêu diệt lên 1

    def add_hit(self):  # Tăng số lần bắn trúng mục tiêu của người chơi lên 1
        """Ghi nhận khi một viên đạn của người chơi bắn trúng xe tăng địch."""
        self.shots_hit += 1  # Tăng biến đếm số phát bắn trúng lên 1

    def get_stats(self):  # Tổng hợp và trả về các thống kê chiến đấu của người chơi
        """
        Trả về bảng thống kê thành tích của người chơi để hiển thị lên HUD.
        """
        acc = 0  # Khởi tạo tỷ lệ chính xác bằng 0 trước khi tính toán
        if self.shots_fired > 0:  # Chỉ tính tỷ lệ bắn trúng nếu người chơi đã bắn ít nhất 1 phát
            acc = round(self.shots_hit / self.shots_fired * 100, 1)  # Tính phần trăm bắn trúng và làm tròn tới 1 chữ số thập phân
        return {  # Trả về một dictionary chứa các số liệu thống kê
            "kills": self.kills,  # Số kẻ địch đã tiêu diệt
            "shots_fired": self.shots_fired,  # Tổng số lần bắn
            "shots_hit": self.shots_hit,  # Số lần bắn trúng
            "accuracy": acc  # Tỷ lệ chính xác tính theo phần trăm
        }

    def draw(self, screen, cam_x=0, cam_y=0):  # Vẽ xe tăng người chơi lên màn hình theo vị trí camera
        """
        Vẽ xe tăng người chơi với hiệu ứng mờ nếu đang tàng hình.
        """
        if not self.alive:  # Nếu xe tăng đã chết thì không vẽ nữa
            return  # Dừng hàm ngay lập tức

        sx = self.x - cam_x  # Tính tọa độ X trên màn hình bằng cách trừ vị trí camera
        sy = self.y - cam_y  # Tính tọa độ Y trên màn hình bằng cách trừ vị trí camera

        alpha = 120 if self.in_stealth else 255  # Nếu đang ở chế độ stealth thì làm ảnh mờ, còn không thì giữ rõ nét

        rotated_body = pygame.transform.rotate(self.body_image, -math.degrees(self.angle))  # Xoay ảnh thân xe theo góc hiện tại
        if alpha < 255:  # Nếu đang ở chế độ stealth thì tạo bản sao ảnh để áp dụng độ trong suốt
            rotated_body = rotated_body.copy()  # Tạo bản sao ảnh thân xe để không làm ảnh hưởng đến ảnh gốc
            rotated_body.set_alpha(alpha)  # Đặt mức độ trong suốt cho ảnh đã xoay
        body_rect = rotated_body.get_rect(center=(int(sx), int(sy)))  # Tạo khung hình chữ nhật để đặt ảnh thân xe đúng vị trí
        screen.blit(rotated_body, body_rect)  # Vẽ thân xe lên màn hình

        rotated_turret = pygame.transform.rotate(self.turret_image, -math.degrees(self.turret_angle))  # Xoay ảnh nòng súng theo góc hiện tại
        if alpha < 255:  # Nếu đang ở chế độ stealth thì làm mờ nòng súng theo cùng cách
            rotated_turret = rotated_turret.copy()  # Tạo bản sao ảnh nòng súng để giữ ảnh gốc nguyên vẹn
            rotated_turret.set_alpha(alpha)  # Đặt mức độ trong suốt cho ảnh nòng súng

        offset_dist = 15  # Khoảng cách nòng súng cần nhô ra khỏi trung tâm thân xe
        tx = sx + math.cos(self.turret_angle) * offset_dist  # Tính tọa độ X của nòng súng trên màn hình
        ty = sy + math.sin(self.turret_angle) * offset_dist  # Tính tọa độ Y của nòng súng trên màn hình

        turret_rect = rotated_turret.get_rect(center=(int(tx), int(ty)))  # Tạo khung hình chữ nhật để đặt ảnh nòng súng đúng vị trí
        screen.blit(rotated_turret, turret_rect)  # Vẽ nòng súng lên màn hình

    def reset(self, x, y):  # Hồi sinh lại người chơi về vị trí mới sau khi chết hoặc bắt đầu màn mới
        """
        Hồi sinh người chơi (gọi khi bắt đầu màn mới hoặc sau khi chết).
        """
        self.x = x  # Đặt lại tọa độ X của người chơi khi hồi sinh
        self.y = y  # Đặt lại tọa độ Y của người chơi khi hồi sinh
        self.angle = 0.0  # Đặt lại góc quay thân xe về 0 độ
        self.turret_angle = 0.0  # Đặt lại góc quay nòng súng về 0 độ
        self.alive = True  # Kích hoạt lại trạng thái sống của người chơi
        self.health = self.max_health  # Hồi đầy máu cho người chơi
        self.shoot_cooldown = 0.0  # Reset thời gian nạp đạn về 0
        self._cap_nhat_rect()  # Cập nhật lại khung va chạm sau khi reset
