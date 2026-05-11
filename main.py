"""
Tank Battle — Điểm vào chương trình chính.
"""

# Nhập lớp Game từ module src.core.game
from src.core.game import Game


def main():
    """
    Hàm khởi tạo chính của chương trình.
    """
    # Tạo một instance (đối tượng) của lớp Game
    game = Game()
    
    # Gọi phương thức run() để bắt đầu vòng lặp game (Game Loop)
    game.run()


# Kiểm tra xem file có được chạy trực tiếp hay không
if __name__ == "__main__":
    # Nếu đúng, gọi hàm main()
    main()
