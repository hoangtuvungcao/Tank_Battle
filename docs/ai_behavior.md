# CHI TIẾT HÀNH VI TRÍ TUỆ NHÂN TẠO (AI BEHAVIOR)

Hệ thống AI trong Tank Battle được thiết kế theo mô hình **Finite State Machine (FSM)** kết hợp với thuật toán tìm đường **A***.

## 1. CÁC TRẠNG THÁI CỦA AI

### PATROL (Tuần tra)
- **Kích hoạt**: Khi không phát hiện người chơi và không bị tấn công.
- **Hành vi**:
  - Di chuyển ngẫu nhiên trên bản đồ.
  - Tự động né tránh chướng ngại vật bằng cách thử 12 hướng khác nhau nếu bị kẹt.
  - Liên tục quét nòng súng (Radar sweep) để dò tìm dấu hiệu của người chơi.

### CHASE (Truy đuổi)
- **Kích hoạt**: Khi phát hiện người chơi trong tầm nhìn (Detection Range).
- **Hành vi**:
  - Sử dụng thuật toán A* để tìm đường ngắn nhất lách qua tường.
  - Áp dụng cơ chế **Flanking**: Không đi thẳng vào người chơi mà hơi lệch sang một bên để bao vây.

### ATTACK (Tấn công)
- **Kích hoạt**: Khi người chơi ở trong tầm bắn (Shoot Range) và có đường đạn thông thoáng (Line of Sight).
- **Hành vi**:
  - **Strafe**: Di chuyển ngang để né đạn của người chơi.
  - **Giữ khoảng cách**: Tự động lùi lại nếu người chơi quá gần hoặc tiến lên nếu quá xa.
  - **Reaction Time**: Có một khoảng trễ nhỏ trước khi bắn để mô phỏng phản xạ của con người.

### INVESTIGATE (Điều tra)
- **Kích hoạt**: Khi người chơi biến mất (đi vào bụi cây hoặc ra ngoài tầm nhìn) hoặc khi bị bắn từ nơi ẩn nấp.
- **Hành vi**:
  - Di chuyển đến vị trí cuối cùng nhìn thấy người chơi.
  - Nếu đến nơi vẫn không thấy, AI sẽ đứng quan sát một lúc trước khi quay lại trạng thái Tuần tra.

### DODGE (Phản xạ né đạn)
- **Cơ chế đặc biệt**: Kích hoạt ngay lập tức khi máu bị sụt giảm.
- **Hành vi**: Bẻ lái 90 độ so với hướng của người chơi để né loạt đạn tiếp theo.

## 2. CÂN BẰNG ĐỘ KHÓ (DIFFICULTY SCALING)

| Thông số | Dễ (Easy) | Bình thường (Normal) | Khó (Hard) |
| :--- | :--- | :--- | :--- |
| Máu (HP) | 30 | 60 | 80 |
| Tốc độ di chuyển | 100 | 140 | 180 |
| Tầm nhìn (px) | 350 | 450 | 600 |
| Tầm bắn (px) | 250 | 350 | 450 |
| Độ trễ phản xạ (s) | 1.0 | 0.6 | 0.3 |
| Độ chính xác ngắm | Thấp | Trung bình | Tuyệt đối |

---
*Tài liệu này giúp bạn hiểu cách AI suy nghĩ để có thể điều chỉnh độ khó game một cách hợp lý nhất.*
