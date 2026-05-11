"""
Enemy — Xe tăng địch với trí tuệ nhân tạo (AI).

File này quản lý toàn bộ hành vi của kẻ địch, bao gồm:
- Tự động tìm đường bằng thuật toán A*.
- Hệ thống trạng thái (Tuần tra, Đuổi bắt, Tấn công, Điều tra).
- Cơ chế phản xạ: Biết né đạn, biết truy đuổi khi bị bắn từ nơi ẩn nấp.
- Cân bằng độ khó: Máu, tốc độ và độ chính xác thay đổi theo cài đặt của người chơi.
"""

import math
import random
from enum import Enum
from src.entities.tank import Tank # Kế thừa từ lớp xe tăng cơ bản
from src.core.settings import TILE_SIZE
from src.ai.behavior import AStar # Thuật toán tìm đường

# Danh sách tên ngẫu nhiên để gán cho các con Bot
ENEMY_NAMES = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Fox", "Ghost", "Hunter", 
               "Iron", "Joker", "Killer", "Lion", "Maverick", "Ninja", "Omega", 
               "Phantom", "Raptor", "Shadow", "Titan", "Viper", "Wolf", "Zeus"]


class TrangThaiAI(Enum):
    """Định nghĩa các trạng thái tâm lý của máy."""
    PATROL = "patrol"           # Đi tuần tra ngẫu nhiên
    CHASE = "chase"             # Đuổi theo người chơi khi nhìn thấy
    ATTACK = "attack"           # Đứng lại bắn khi đủ gần
    FLEE = "flee"               # Chạy trốn khi máu quá thấp (Tính năng mở rộng)
    INVESTIGATE = "investigate"  # Đi kiểm tra vị trí cuối cùng nhìn thấy người chơi

class Enemy(Tank):
    """
    Lớp điều khiển xe tăng địch tự động.
    """

    # Bảng thông số kỹ thuật dựa trên 3 mức độ khó
    CAU_HINH = {
        "easy": { # Dễ: Địch yếu, chậm, bắn kém
            "health": 30, "speed": 100, "detect": 350, "shoot": 250,
            "aim": 0.5, "react": 1.0, "delay": 1.8, "search": 500
        },
        "normal": { # Bình thường: Cân bằng
            "health": 60, "speed": 140, "detect": 450, "shoot": 350,
            "aim": 0.35, "react": 0.6, "delay": 1.0, "search": 650
        },
        "hard": { # Khó: Địch trâu, nhanh, bắn cực chuẩn
            "health": 80, "speed": 180, "detect": 600, "shoot": 450,
            "aim": 0.15, "react": 0.3, "delay": 0.6, "search": 800
        },
    }

    def __init__(self, x, y, difficulty="normal"):
        """
        Khởi tạo xe tăng địch dựa trên tọa độ và độ khó được chọn.
        """
        # Lấy cấu hình tương ứng từ bảng CAU_HINH
        cfg = self.CAU_HINH.get(difficulty, self.CAU_HINH["normal"])
        # Gọi hàm khởi tạo của lớp cha Tank
        super().__init__(x=x, y=y, color="black", health=cfg["health"], speed=cfg["speed"])

        # Gán tên và lưu độ khó
        self.name = f"Bot {random.choice(ENEMY_NAMES)}"
        self.difficulty = difficulty
        
        # Thiết lập các chỉ số từ cấu hình
        self.detection_range = cfg["detect"]  # Tầm nhìn thấy player
        self.shoot_range = cfg["shoot"]       # Tầm có thể bắn
        self.aim_accuracy = cfg["aim"]        # Sai số khi ngắm (càng nhỏ càng chuẩn)
        self.reaction_time = cfg["react"]     # Độ trễ trước khi bắn (giây)
        self.shoot_delay = cfg["delay"]       # Tốc độ nạp đạn (giây)
        self.search_range = cfg["search"]     # Tầm tìm kiếm khi mất dấu
        self.patrol_change_time = 2.5         # Thời gian đổi hướng khi tuần tra

        # Quản lý trạng thái AI
        self.state = TrangThaiAI.PATROL
        self.last_known_pos = None   # Tọa độ cuối cùng của người chơi
        self.time_lost_player = 0.0  # Thời gian đã trôi qua kể từ khi mất dấu

        # Các biến phục vụ tuần tra (Patrol)
        self.patrol_dir = random.uniform(0, 2 * math.pi) # Hướng đi ngẫu nhiên
        self.patrol_timer = 0.0
        self.move_timer = 0.0
        self.move_duration = random.uniform(1.0, 3.0) # Thời gian đi trước khi dừng
        self.is_moving = True

        # Biến phục vụ chiến đấu (Combat)
        self.reaction_timer = 0.0
        self.locked_on = False  # Đã ngắm trúng đích chưa

        # Hệ thống phản xạ khi bị bắn
        self.last_health = cfg["health"]
        self.under_attack_timer = 0.0   # Đếm ngược thời gian bị tấn công
        self.attacker_dir = 0.0          # Hướng phát ra viên đạn

        # Cơ chế phát hiện kẹt vật cản
        self.prev_pos = (x, y)
        self.stuck_time = 0.0
        self.stuck_threshold = 0.5 # Sau 0.5s không nhúc nhích là bị kẹt

        # Cơ chế đi vòng (Flank) để tăng tính chiến thuật
        self.flank_offset = 0.0   # Góc đi lệch để bao vây
        self.flank_timer = 0.0

        # Cơ chế né đạn (Dodge)
        self.dodge_timer = 0.0
        self.dodge_dir = 0.0

    def update_ai(self, dt, player_pos, map_data, player_in_stealth=False):
        """
        Hàm cập nhật trí tuệ nhân tạo chính, chạy sau mỗi khung hình.
        """
        bullet_data = None
        # Tính khoảng cách thực tế đến người chơi
        kc = self.get_distance_to(player_pos[0], player_pos[1])

        # --- 1. PHÁT HIỆN BỊ TẤN CÔNG ---
        # Kiểm tra xem máu có bị tụt so với frame trước không
        just_hit = self.health < self.last_health
        if just_hit:
            self.under_attack_timer = 5.0  # Biết là đang bị bắn trong 5 giây tới
            self.last_known_pos = player_pos # Ghi nhớ vị trí kẻ tấn công
            self.attacker_dir = self.get_angle_to(player_pos[0], player_pos[1])
            # Thực hiện né sang ngang ngay lập tức
            self.dodge_timer = 0.8
            self.dodge_dir = random.choice([-1, 1]) * math.pi / 2
        self.last_health = self.health # Cập nhật lại mốc máu

        if self.under_attack_timer > 0:
            self.under_attack_timer -= dt
        under_attack = self.under_attack_timer > 0

        # --- 2. CƠ CHẾ NÉ ĐẠN (DODGE) ---
        if self.dodge_timer > 0:
            self.dodge_timer -= dt
            dodge_angle = self.attacker_dir + self.dodge_dir
            # Tính toán vị trí mới khi né
            tx = self.x + math.cos(dodge_angle) * self.speed * dt
            ty = self.y + math.sin(dodge_angle) * self.speed * dt
            # Nếu vị trí mới không kẹt tường thì mới di chuyển
            if not self._check_collision(tx, ty, map_data):
                self.x, self.y = tx, ty
                self._cap_nhat_rect()

        # --- 3. QUYẾT ĐỊNH TRẠNG THÁI (STATE MACHINE) ---
        if under_attack:
            # Nếu đang bị bắn: Chuyển sang tấn công hoặc truy đuổi
            self.state = TrangThaiAI.ATTACK if kc <= self.shoot_range else TrangThaiAI.INVESTIGATE
        elif player_in_stealth and not under_attack:
            # Nếu player đang tàng hình: Địch sẽ "mù", trừ khi ở quá gần (<80px)
            self.state = TrangThaiAI.ATTACK if kc < 80 else TrangThaiAI.PATROL
        elif kc < self.detection_range:
            # Nếu player trong tầm mắt: Đuổi hoặc Bắn
            self.state = TrangThaiAI.ATTACK if kc <= self.shoot_range else TrangThaiAI.CHASE
        else:
            # Nếu ngoài tầm mắt: Đi điều tra vị trí cũ hoặc đi tuần
            if self.last_known_pos and self.time_lost_player < 4.0:
                self.state = TrangThaiAI.INVESTIGATE
            else:
                self.state = TrangThaiAI.PATROL

        # --- 4. THỰC HIỆN HÀNH VI ---
        if self.state == TrangThaiAI.PATROL:
            self._patrol(dt, map_data)
            self.time_lost_player += dt
            self.last_known_pos = None
        elif self.state == TrangThaiAI.CHASE:
            self.last_known_pos = player_pos
            self.time_lost_player = 0
            self._chase(dt, player_pos, map_data)
        elif self.state == TrangThaiAI.ATTACK:
            self.last_known_pos = player_pos
            self.time_lost_player = 0
            # Trả về dữ liệu viên đạn nếu AI quyết định bắn
            bullet_data = self._attack(dt, player_pos, map_data)
        elif self.state == TrangThaiAI.INVESTIGATE:
            self._investigate(dt, player_pos, map_data, under_attack)

        # --- 5. XOAY NÒNG SÚNG ---
        # Chỉ xoay nòng khi đang trong trạng thái chiến đấu hoặc bị bắn
        if self.state in (TrangThaiAI.ATTACK, TrangThaiAI.CHASE) or under_attack:
            self.rotate_turret_to_target(player_pos[0], player_pos[1], dt)
        elif self.state == TrangThaiAI.INVESTIGATE and self.last_known_pos:
            self.rotate_turret_to_target(self.last_known_pos[0], self.last_known_pos[1], dt)

        # Bắn trả đũa khi bị tấn công bất ngờ
        if under_attack and bullet_data is None and self._should_shoot(player_pos, map_data):
            bullet_data = self.shoot()

        # --- 6. KIỂM TRA VÀ THOÁT KẸT ---
        self._check_stuck(dt, map_data)

        # Gọi hàm update của lớp cha để giảm cooldown bắn
        self.update(dt)
        return bullet_data

    def _patrol(self, dt, map_data):
        """Hành vi đi tuần tra ngẫu nhiên quanh bản đồ."""
        self.patrol_timer += dt
        self.move_timer += dt

        # Đổi hướng sau mỗi khoảng thời gian nhất định
        if self.patrol_timer >= self.patrol_change_time:
            self.patrol_timer = 0
            self.patrol_dir = random.uniform(0, 2 * math.pi)
            self.move_duration = random.uniform(1.0, 3.0)
            self.move_timer = 0
            self.is_moving = True

        # Xoay thân xe về hướng tuần tra đã chọn
        diff = self.patrol_dir - self.angle
        while diff > math.pi: diff -= 2 * math.pi
        while diff < -math.pi: diff += 2 * math.pi
        if abs(diff) > 0.1:
            if diff > 0: self.rotate_body_right(dt)
            else: self.rotate_body_left(dt)

        # Quét nòng súng qua lại (giống radar) để tăng vẻ cảnh giác
        scan = self.angle + math.sin(self.patrol_timer * 2) * 0.5
        self.rotate_turret_to_angle(scan, dt)

        # Thực hiện di chuyển tiến lên
        if self.is_moving and self.move_timer < self.move_duration:
            tx = self.x + math.cos(self.angle) * self.speed * dt
            ty = self.y + math.sin(self.angle) * self.speed * dt
            if not self._check_collision(tx, ty, map_data):
                self.move_forward(dt)
            else:
                # Nếu gặp tường khi tuần tra, tìm hướng khác ngay
                self._avoid_obstacle(dt, map_data)
        else:
            # Nghỉ 1 giây sau khi đi xong một đoạn
            self.is_moving = False
            if self.move_timer >= self.move_duration + 1.0:
                self.move_timer = 0
                self.is_moving = True

    def _chase(self, dt, player_pos, map_data):
        """Hành vi đuổi theo người chơi có tính toán góc đi vòng (Flank)."""
        self.flank_timer += dt
        if self.flank_timer > 3.0:
            self.flank_timer = 0
            # Ngẫu nhiên chọn góc lệch để không đi thẳng vào họng súng của người chơi
            self.flank_offset = random.choice([-1, 1]) * random.uniform(0.3, 0.8)

        kc = self.get_distance_to(player_pos[0], player_pos[1])
        if kc < self.shoot_range * 0.5:
            # Nếu đã gần: Đi vòng lệch sang một bên
            angle = self.get_angle_to(player_pos[0], player_pos[1]) + self.flank_offset
            fx = self.x + math.cos(angle) * kc * 0.5
            fy = self.y + math.sin(angle) * kc * 0.5
            self._move_to(fx, fy, dt, map_data)
        else:
            # Nếu còn xa: Đuổi thẳng tới vị trí người chơi
            self._move_to(player_pos[0], player_pos[1], dt, map_data)

    def _attack(self, dt, player_pos, map_data):
        """Hành vi tấn công: Vừa di chuyển giữ khoảng cách vừa bắn."""
        # Luôn xoay nòng về phía mục tiêu
        self.rotate_turret_to_target(player_pos[0], player_pos[1], dt)
        angle_to = self.get_angle_to(player_pos[0], player_pos[1])
        diff = abs(angle_to - self.turret_angle)
        while diff > math.pi: diff -= 2 * math.pi
        aimed = abs(diff) < self.aim_accuracy  # Đã ngắm trúng trong sai số cho phép

        # Xoay thân xe theo hướng nòng để sẵn sàng di chuyển hoặc lùi
        body_diff = self.turret_angle - self.angle
        while body_diff > math.pi: body_diff -= 2 * math.pi
        while body_diff < -math.pi: body_diff += 2 * math.pi
        if abs(body_diff) > math.pi / 6:
            if body_diff > 0: self.rotate_body_right(dt)
            else: self.rotate_body_left(dt)

        # Kiểm tra xem có vật cản (tường) che khuất mục tiêu không
        has_los = self._has_line_of_sight(player_pos[0], player_pos[1], map_data)

        bullet = None
        # Chỉ bắn khi ngắm chuẩn, có đường đạn thông thoáng và qua thời gian phản xạ
        if aimed and has_los:
            if not self.locked_on:
                self.reaction_timer += dt
                if self.reaction_timer >= self.reaction_time:
                    self.locked_on = True
                    self.reaction_timer = 0
            if self.locked_on:
                bullet = self.shoot()
                if bullet: self.locked_on = False
        else:
            self.reaction_timer = 0
            self.locked_on = False

        # --- LOGIC DI CHUYỂN KHI CHIẾN ĐẤU ---
        kc = self.get_distance_to(player_pos[0], player_pos[1])
        opt = self.shoot_range * 0.6  # Khoảng cách bắn tối ưu

        if not has_los:
            # Bị khuất: Tìm đường bằng A* để đuổi theo
            self._move_to(player_pos[0], player_pos[1], dt, map_data)
        elif kc < opt * 0.4:
            # Quá gần: Lùi lại để tránh bị húc
            self.move_backward(dt)
        elif kc > opt * 1.3:
            # Quá xa: Tiến lên cho tới tầm bắn
            self.move_forward(dt)
        else:
            # Khoảng cách đẹp: Thực hiện di chuyển ngang (Strafe) để khó bị bắn trúng
            strafe = angle_to + math.pi / 2 * (1 if self.flank_offset > 0 else -1)
            sx = self.x + math.cos(strafe) * self.speed * 0.4 * dt
            sy = self.y + math.sin(strafe) * self.speed * 0.4 * dt
            if not self._check_collision(sx, sy, map_data):
                self.x, self.y = sx, sy
                self._cap_nhat_rect()

        return bullet

    def _investigate(self, dt, player_pos, map_data, under_attack):
        """Đi tới vị trí cuối cùng nhìn thấy mục tiêu để tìm kiếm."""
        if under_attack:
            # Nếu đang bị bắn thì mặc kệ, xông thẳng vào chỗ có đạn phát ra
            self._move_to(player_pos[0], player_pos[1], dt, map_data)
            return

        if self.last_known_pos:
            dist = self.get_distance_to(self.last_known_pos[0], self.last_known_pos[1])
            if dist < 40:
                # Đã tới nơi mà vẫn không thấy thì đứng đợi một lúc rồi đi tuần
                self.last_known_pos = None
                self.time_lost_player += dt
                if self.time_lost_player > 6.0: self.state = TrangThaiAI.PATROL
            else:
                # Vẫn đang trên đường tới vị trí cuối cùng
                self._move_to(self.last_known_pos[0], self.last_known_pos[1], dt, map_data)
        else:
            self.state = TrangThaiAI.PATROL

    def _move_to(self, tx, ty, dt, map_data):
        """
        Di chuyển thông minh sử dụng thuật toán A* để lách qua tường.
        """
        target_x, target_y = tx, ty
        
        # Nếu đường thẳng tới đích bị chặn bởi tường
        if not self._has_line_of_sight(tx, ty, map_data):
            if not hasattr(self, 'astar'): self.astar = AStar(map_data)
            self.astar.map_data = map_data
            
            # Tìm danh sách các điểm đi (waypoint) ngắn nhất
            path = self.astar.find_path(self.x, self.y, tx, ty)
            
            # Chọn điểm thứ 2 trong danh sách (điểm kế tiếp) làm đích tạm thời
            if path and len(path) > 1:
                target_x, target_y = path[1]
        
        # Tính toán xoay thân xe về phía đích tạm thời
        angle = self.get_angle_to(target_x, target_y)
        diff = angle - self.angle
        while diff > math.pi: diff -= 2 * math.pi
        while diff < -math.pi: diff += 2 * math.pi

        if abs(diff) > 0.1:
            if diff > 0: self.rotate_body_right(dt)
            else: self.rotate_body_left(dt)

        # Chỉ tiến khi đã xoay thân xe tương đối đúng hướng
        if abs(diff) < math.pi / 3:
            nx = self.x + math.cos(self.angle) * self.speed * dt
            ny = self.y + math.sin(self.angle) * self.speed * dt
            if not self._check_collision(nx, ny, map_data):
                self.move_forward(dt)
            else:
                # Nếu bất ngờ gặp vật cản nhỏ, dùng cơ chế né chướng ngại vật
                self._avoid_obstacle(dt, map_data)

    def _avoid_obstacle(self, dt, map_data):
        """Thử xoay 12 hướng khác nhau để tìm đường thoát kẹt."""
        angles_to_try = [math.pi/4, -math.pi/4, math.pi/2, -math.pi/2, math.pi, 0]
        for offset in angles_to_try:
            test_angle = self.angle + offset
            tx = self.x + math.cos(test_angle) * self.speed * dt
            ty = self.y + math.sin(test_angle) * self.speed * dt
            if not self._check_collision(tx, ty, map_data):
                self.angle = test_angle
                self.x, self.y = tx, ty
                self._cap_nhat_rect()
                return
        self.patrol_dir = random.uniform(0, 2 * math.pi)

    def _check_collision(self, x, y, map_data):
        """Kiểm tra xem vị trí mới có đè lên tường/thùng phuy không."""
        if map_data is None: return False
        # Dùng Hitbox hơi nhỏ hơn kích thước thật để máy dễ lách qua khe hẹp
        hw = self.width // 2 - 4   
        hh = self.height // 2 - 4
        # Kiểm tra 8 điểm quanh xe để đảm bảo không dính tường
        points = [(x-hw, y-hh), (x+hw, y-hh), (x-hw, y+hh), (x+hw, y+hh), (x, y-hh), (x, y+hh), (x-hw, y), (x+hw, y)]
        for px, py in points:
            if map_data.is_solid_at(px, py): return True
        return False

    def _check_stuck(self, dt, map_data):
        """Phát hiện kẹt khi tọa độ không thay đổi trong thời gian dài."""
        dist = math.sqrt((self.x - self.prev_pos[0])**2 + (self.y - self.prev_pos[1])**2)
        if dist < 1.0: self.stuck_time += dt
        else: self.stuck_time = 0
        self.prev_pos = (self.x, self.y)

        if self.stuck_time > self.stuck_threshold:
            self.stuck_time = 0
            self._avoid_obstacle(dt, map_data)

    def _has_line_of_sight(self, tx, ty, map_data):
        """Sử dụng kỹ thuật Raycasting để xem có tường che giữa máy và mục tiêu không."""
        if not map_data: return True
        dx, dy = tx - self.x, ty - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0: return True
        
        # Nhảy từng bước 16 pixel dọc theo đường thẳng để kiểm tra
        steps = int(dist / 16)
        for i in range(1, steps):
            check_x = self.x + (dx / dist) * (i * 16)
            check_y = self.y + (dy / dist) * (i * 16)
            if map_data.is_solid_at(check_x, check_y): return False
        return True

    def _should_shoot(self, player_pos, map_data):
        """Tổng hợp các điều kiện để quyết định có bấm nút bắn hay không."""
        kc = self.get_distance_to(player_pos[0], player_pos[1])
        if kc > self.shoot_range: return False
        angle = self.get_angle_to(player_pos[0], player_pos[1])
        diff = abs(angle - self.turret_angle)
        while diff > math.pi: diff -= 2 * math.pi
        if abs(diff) > self.aim_accuracy: return False
        return self._has_line_of_sight(player_pos[0], player_pos[1], map_data)

    def reset(self, x, y, difficulty=None):
        """Đưa xe tăng địch về trạng thái sạch sẽ ban đầu."""
        self.x, self.y = x, y
        self.angle = 0.0
        self.turret_angle = 0.0
        self.alive = True
        self.health = self.max_health
        self.last_health = self.max_health
        self.state = TrangThaiAI.PATROL
        self.last_known_pos = None
        self.time_lost_player = 0.0
        self.shoot_cooldown = 0.0
        self.stuck_time = 0.0
        self.under_attack_timer = 0.0
        self._cap_nhat_rect()
