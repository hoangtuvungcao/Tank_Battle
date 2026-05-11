"""Module Hành vi AI (AI Behavior) - Tích hợp thuật toán tìm đường A* (A-Star).

Thuật toán A* giúp xe tăng địch tìm được đường đi ngắn nhất đến vị trí của người chơi
thông qua mê cung các bức tường và chướng ngại vật, thay vì chỉ đâm sầm vào tường.
"""

import math
import heapq

class AStar:
    """Lớp triển khai thuật toán tìm đường A*."""
    
    def __init__(self, map_data):
        # Lưu trữ bản đồ game để kiểm tra va chạm
        self.map_data = map_data
        # Kích thước mỗi ô (tile) trên bản đồ
        self.tile_size = 64

    def _get_neighbors(self, node):
        """Tìm các ô lân cận (Trên, Dưới, Trái, Phải, Chéo) có thể đi được."""
        # Khởi tạo danh sách các ô lân cận
        neighbors = []
        # Tọa độ ô hiện tại
        col, row = node
        # Các hướng di chuyển (Cột, Dòng): 4 hướng thẳng và 4 hướng chéo
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
        
        # Duyệt qua từng hướng
        for dc, dr in directions:
            # Tọa độ lân cận mới
            nc, nr = col + dc, row + dr
            # Kiểm tra xem tọa độ mới có nằm trong giới hạn bản đồ không
            if 0 <= nc < self.map_data.width and 0 <= nr < self.map_data.height:
                # Kiểm tra xem ô đó có phải là vật cản cứng (solid) không
                if not self.map_data.tiles[nr][nc].is_blocking():
                    # Nếu đi chéo, kiểm tra xem có bị vướng góc tường không (để không đi xuyên tường)
                    if dc != 0 and dr != 0:
                        if self.map_data.tiles[row][nc].is_blocking() or self.map_data.tiles[nr][col].is_blocking():
                            continue # Bị vướng góc, bỏ qua ô chéo này
                    # Nếu hợp lệ, thêm vào danh sách lân cận
                    neighbors.append((nc, nr))
        # Trả về danh sách lân cận
        return neighbors

    def find_path(self, start_x, start_y, target_x, target_y):
        """Tìm đường đi ngắn nhất từ Start đến Target.
        
        Args:
            start_x, start_y: Tọa độ pixel hiện tại của AI
            target_x, target_y: Tọa độ pixel của người chơi
            
        Returns:
            Danh sách các điểm (x, y) pixel tạo thành đường đi, hoặc None nếu không có đường.
        """
        # Chuyển đổi tọa độ pixel thành tọa độ lưới (Grid) để thuật toán tính toán nhanh hơn
        start_node = (int(start_x // self.tile_size), int(start_y // self.tile_size))
        target_node = (int(target_x // self.tile_size), int(target_y // self.tile_size))

        # Nếu đang đứng trùng ô với mục tiêu, không cần tìm đường
        if start_node == target_node:
            return []

        # Frontier là hàng đợi ưu tiên (Priority Queue), lưu các node cần duyệt
        # Cấu trúc: (chi phí_f, tọa_độ_node)
        frontier = []
        heapq.heappush(frontier, (0, start_node))
        
        # Came_from lưu dấu vết đường đi (Node B được đi tới từ Node A)
        came_from = {start_node: None}
        
        # Cost_so_far lưu chi phí (G-cost) từ điểm bắt đầu đến điểm hiện tại
        cost_so_far = {start_node: 0}

        # Vòng lặp chính của thuật toán A*
        while frontier:
            # Lấy ra node có chi phí F nhỏ nhất để duyệt
            current = heapq.heappop(frontier)[1]

            # Nếu đã đến được mục tiêu, dừng việc tìm kiếm
            if current == target_node:
                break

            # Duyệt qua các ô lân cận của node hiện tại
            for next_node in self._get_neighbors(current):
                # Tính chi phí di chuyển: đi chéo tốn nhiều chi phí hơn (1.414) so với đi thẳng (1)
                move_cost = 1.414 if current[0] != next_node[0] and current[1] != next_node[1] else 1.0
                # Tính tổng chi phí G (từ Start -> Current -> Next)
                new_cost = cost_so_far[current] + move_cost

                # Nếu ô này chưa được duyệt, hoặc tìm được đường đi mới ngắn hơn đường cũ
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    # Cập nhật chi phí G mới
                    cost_so_far[next_node] = new_cost
                    # Tính chi phí H (Heuristic) - Khoảng cách đường chim bay từ Next đến Target
                    priority = new_cost + math.hypot(target_node[0] - next_node[0], target_node[1] - next_node[1])
                    # Đưa node mới vào hàng đợi để chờ duyệt tiếp
                    heapq.heappush(frontier, (priority, next_node))
                    # Ghi nhớ đường đi để sau này truy xuất ngược lại
                    came_from[next_node] = current

        # Nếu không tìm thấy đường đi tới target
        if target_node not in came_from:
            return None

        # Truy xuất ngược từ Target về Start để tạo thành đường đi hoàn chỉnh
        current = target_node
        path = []
        # Lặp cho đến khi quay về điểm bắt đầu
        while current != start_node:
            # Chuyển đổi tọa độ lưới trở lại thành tọa độ pixel ở trung tâm ô
            px = current[0] * self.tile_size + self.tile_size // 2
            py = current[1] * self.tile_size + self.tile_size // 2
            path.append((px, py))
            # Lùi về node trước đó
            current = came_from[current]
            
        # Đảo ngược danh sách vì chúng ta vừa truy xuất từ Target về Start
        path.reverse()
        # Trả về đường đi
        return path
