"""
Collision — Hệ thống xử lý vật lý và va chạm.

File này chứa "trọng tài" của game, quyết định xem:
- Xe tăng có được phép đi qua một ô hay không.
- Viên đạn có bị biến mất khi chạm tường hay không.
- Cơ chế Va chạm trượt (Sliding) giúp game mượt mà hơn.
"""

import pygame


class Collision:
    """
    Tập hợp các phương thức tĩnh (static methods) để xử lý va chạm.
    """

    @staticmethod
    def tank_vs_map(tank_rect, map_data):
        """
        Kiểm tra xem hình chữ nhật của xe tăng có đè lên vật cản nào không.
        
        Sử dụng is_solid_at: Thùng phuy (Barrel) được tính là vật cản cứng với xe tăng.
        """
        if map_data is None:
            return False
            
        # Kiểm tra 4 góc của xe tăng để đảm bảo không góc nào lọt vào tường
        corners = [
            (tank_rect.left, tank_rect.top),         # Góc trên bên trái
            (tank_rect.right - 1, tank_rect.top),    # Góc trên bên phải
            (tank_rect.left, tank_rect.bottom - 1),  # Góc dưới bên trái
            (tank_rect.right - 1, tank_rect.bottom - 1), # Góc dưới bên phải
        ]
        
        for cx, cy in corners:
            # Nếu bất kỳ góc nào chạm vào ô cứng (Wall, Sandbag, Barrel...)
            if map_data.is_solid_at(cx, cy):
                return True # Có va chạm
        return False # An toàn

    @staticmethod
    def bullet_vs_map(bullet_x, bullet_y, map_data):
        """
        Kiểm tra va chạm giữa viên đạn và bản đồ.
        
        Sử dụng is_wall_at: Khác với xe tăng, đạn có thể bay XUYÊN QUA thùng phuy.
        """
        if map_data is None:
            return False
        # Chỉ trả về True nếu đạn chạm vào Tường hoặc Bao cát (vật cản đạn)
        return map_data.is_wall_at(bullet_x, bullet_y)

    @staticmethod
    def rect_vs_rect(rect1, rect2):
        """Kiểm tra va chạm giữa hai hình chữ nhật bất kỳ (VD: đạn với xe)."""
        return rect1.colliderect(rect2)

    @staticmethod
    def tank_vs_tank(tank1_rect, tank2_rect):
        """Kiểm tra xem hai xe tăng có đâm sầm vào nhau không."""
        return tank1_rect.colliderect(tank2_rect)

    @staticmethod
    def resolve_tank_wall(tank, map_data, old_x, old_y):
        """
        Thuật toán Va chạm trượt (Sliding Collision Resolution).
        Giúp xe tăng không bị dính chặt vào tường khi đi chéo.
        """
        # 1. Cập nhật khung va chạm tại vị trí mới (vị trí vừa di chuyển xong)
        tank._cap_nhat_rect()
        
        # Nếu ở vị trí mới KHÔNG có va chạm, ta không cần làm gì cả, giữ nguyên vị trí.
        if not Collision.tank_vs_map(tank.get_rect(), map_data):
            return

        # Lưu lại tọa độ "mong muốn" (tọa độ đang bị kẹt)
        new_x, new_y = tank.x, tank.y

        # --- THỬ NGHIỆM TRỤC Y (Trượt dọc) ---
        # Giả định: Ta chỉ trả lại tọa độ X về cũ, giữ nguyên tọa độ Y mới
        tank.x = old_x
        tank._cap_nhat_rect()
        # Nếu bây giờ hết kẹt -> Nghĩa là xe có thể trượt dọc theo bức tường
        if not Collision.tank_vs_map(tank.get_rect(), map_data):
            return  # Kết thúc, xe đã trượt thành công theo trục Y

        # --- THỬ NGHIỆM TRỤC X (Trượt ngang) ---
        # Giả định: Ta trả lại tọa độ Y về cũ, dùng tọa độ X mới
        tank.x = new_x # Lấy lại X mới
        tank.y = old_y # Trả Y về cũ
        tank._cap_nhat_rect()
        # Nếu hết kẹt -> Xe có thể trượt ngang dọc theo bờ tường
        if not Collision.tank_vs_map(tank.get_rect(), map_data):
            return  # Kết thúc, xe đã trượt thành công theo trục X

        # --- TRƯỜNG HỢP KẸT CỨNG (Cả 2 trục đều không thoát) ---
        # Trả xe về hoàn toàn tọa độ cũ (vị trí an toàn trước khi di chuyển)
        tank.x = old_x
        tank.y = old_y
        tank._cap_nhat_rect()
