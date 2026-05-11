"""Module AI Controller - Trí tuệ bầy đàn (Swarm Intelligence).

Quản lý tất cả xe tăng địch cùng lúc để tạo ra các chiến thuật nhóm thông minh
như: bao vây (surround), tản ra (spread), và tập kích (flank).
"""

import math

class AIController:
    """Bộ điều khiển trung tâm cho tất cả xe tăng địch."""
    
    def __init__(self, map_data):
        self.map_data = map_data
        self.tactics_timer = 0.0

    def update_swarm(self, enemies, player, dt):
        """Cập nhật chiến thuật bầy đàn mỗi frame.
        
        Args:
            enemies: Danh sách các đối tượng Enemy đang sống
            player: Đối tượng Player
            dt: Delta time
        """
        if not player or not player.is_alive():
            return

        self.tactics_timer += dt
        
        # Cập nhật lại góc tấn công cho từng kẻ địch mỗi 2 giây
        # để đảm bảo chúng bao vây người chơi từ nhiều hướng khác nhau
        if self.tactics_timer > 2.0 and len(enemies) > 1:
            self.tactics_timer = 0.0
            
            # Tính toán góc bao vây đều nhau (360 độ chia cho số lượng địch)
            angle_step = (2 * math.pi) / len(enemies)
            base_angle = math.atan2(player.y - enemies[0].y, player.x - enemies[0].x)
            
            for i, enemy in enumerate(enemies):
                # Mỗi kẻ địch sẽ cố gắng đi vòng (flank) theo một góc riêng biệt
                target_flank_angle = base_angle + (i * angle_step)
                
                # Cập nhật thông số flank cho từng AI để không đi chồng lên nhau
                enemy.flank_offset = target_flank_angle

        # Xử lý tránh va chạm lẫn nhau (Separation)
        for i, enemy in enumerate(enemies):
            for j, other in enumerate(enemies):
                if i != j:
                    dist = enemy.get_distance_to(other.x, other.y)
                    # Nếu 2 xe tăng địch đứng quá gần nhau (dưới 60 pixel)
                    if dist < 60 and dist > 0:
                        # Lực đẩy tản ra
                        push_angle = math.atan2(enemy.y - other.y, enemy.x - other.x)
                        enemy.x += math.cos(push_angle) * 20 * dt
                        enemy.y += math.sin(push_angle) * 20 * dt
                        enemy._cap_nhat_rect()
