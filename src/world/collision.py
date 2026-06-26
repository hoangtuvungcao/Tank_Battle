"""
Collision — Hệ thống xử lý vật lý và va chạm.

File này chứa "trọng tài" của game, quyết định xem:
- Xe tăng có được phép đi qua một ô hay không.
- Viên đạn có bị biến mất khi chạm tường hay không.
- Cơ chế Va chạm trượt (Sliding) giúp game mượt mà hơn.
"""

import pygame  # Import thư viện pygame để sử dụng các lớp hình chữ nhật và phép kiểm tra va chạm cơ bản


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
        if map_data is None:  # Nếu bản đồ chưa được tạo thì bỏ qua kiểm tra va chạm
            return False  # Trả về False để báo rằng không có va chạm

        # Lấy tâm của hình chữ nhật xe tăng để kiểm tra các điểm xung quanh
        mid_x = tank_rect.centerx  # Tọa độ X của tâm xe tăng
        mid_y = tank_rect.centery  # Tọa độ Y của tâm xe tăng
        points = [  # Tạo danh sách các điểm kiểm tra để phủ kín toàn bộ vùng xe tăng
            (tank_rect.left, tank_rect.top),             # Góc trên trái của xe tăng
            (tank_rect.right - 1, tank_rect.top),        # Góc trên phải của xe tăng
            (tank_rect.left, tank_rect.bottom - 1),      # Góc dưới trái của xe tăng
            (tank_rect.right - 1, tank_rect.bottom - 1), # Góc dưới phải của xe tăng
            (mid_x, tank_rect.top),                      # Điểm giữa trên của xe tăng
            (mid_x, tank_rect.bottom - 1),               # Điểm giữa dưới của xe tăng
            (tank_rect.left, mid_y),                     # Điểm giữa trái của xe tăng
            (tank_rect.right - 1, mid_y),                # Điểm giữa phải của xe tăng
        ]

        for cx, cy in points:  # Duyệt qua từng điểm để kiểm tra xem có chạm vật cản hay không
            if map_data.is_solid_at(cx, cy):  # Nếu một điểm nào đó rơi vào ô cứng
                return True  # Trả về True để báo có va chạm
        return False  # Nếu không điểm nào chạm cản thì trả về False

    @staticmethod
    def bullet_vs_map(bullet_x, bullet_y, map_data):
        """
        Kiểm tra va chạm giữa viên đạn và bản đồ.

        Sử dụng is_wall_at: Khác với xe tăng, đạn có thể bay xuyên qua thùng phuy.
        """
        if map_data is None:  # Nếu bản đồ chưa tồn tại thì không kiểm tra đạn
            return False  # Trả về False vì không có va chạm

        # Chỉ trả về True nếu viên đạn chạm vào tường hoặc bao cát
        return map_data.is_wall_at(bullet_x, bullet_y)  # Gọi hàm kiểm tra vật cản của bản đồ

    @staticmethod
    def rect_vs_rect(rect1, rect2):
        """Kiểm tra va chạm giữa hai hình chữ nhật bất kỳ, ví dụ đạn với xe tăng."""
        return rect1.colliderect(rect2)  # Sử dụng phương thức có sẵn của pygame để kiểm tra giao nhau

    @staticmethod
    def tank_vs_tank(tank1_rect, tank2_rect):
        """Kiểm tra xem hai xe tăng có va chạm trực tiếp với nhau không."""
        return tank1_rect.colliderect(tank2_rect)  # Kiểm tra hai hình chữ nhật có chồng lên nhau hay không

    @staticmethod
    def resolve_tank_wall(tank, map_data, old_x, old_y):
        """
        Thuật toán Va chạm trượt (Sliding Collision Resolution).
        Giúp xe tăng không bị dính chặt vào tường khi đi chéo.
        """
        # Cập nhật khung va chạm tại vị trí mới sau khi xe di chuyển
        tank._cap_nhat_rect()

        # Nếu ở vị trí mới không có va chạm thì giữ nguyên vị trí và kết thúc
        if not Collision.tank_vs_map(tank.get_rect(), map_data):
            return

        # Lưu lại tọa độ mong muốn trước khi thử điều chỉnh lại vị trí
        new_x, new_y = tank.x, tank.y

        # Thử nghiệm trục Y: giữ nguyên Y mới, đưa X về vị trí cũ
        tank.x = old_x  # Đặt lại hoành độ về vị trí cũ
        tank._cap_nhat_rect()  # Cập nhật lại khung va chạm sau khi thay đổi

        # Nếu ở trạng thái này không còn va chạm thì xe có thể trượt dọc theo tường
        if not Collision.tank_vs_map(tank.get_rect(), map_data):
            return  # Kết thúc vì xe đã trượt thành công theo trục Y

        # Thử nghiệm trục X: giữ nguyên X mới, đưa Y về vị trí cũ
        tank.x = new_x  # Khôi phục lại hoành độ mới
        tank.y = old_y  # Đặt tung độ về vị trí cũ
        tank._cap_nhat_rect()  # Cập nhật lại khung va chạm sau khi thay đổi

        # Nếu ở trạng thái này không còn va chạm thì xe có thể trượt ngang theo tường
        if not Collision.tank_vs_map(tank.get_rect(), map_data):
            return  # Kết thúc vì xe đã trượt thành công theo trục X

        # Trường hợp bị kẹt cứng ở cả hai trục: đưa xe quay về vị trí cũ an toàn
        tank.x = old_x  # Khôi phục lại hoành độ ban đầu
        tank.y = old_y  # Khôi phục lại tung độ ban đầu
        tank._cap_nhat_rect()  # Cập nhật lại khung va chạm cuối cùng
