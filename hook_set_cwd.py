"""
Runtime hook — Tank Battle
Đổi thư mục làm việc sang sys._MEIPASS khi chạy trong bundle PyInstaller,
để các đường dẫn tương đối ("assets/...", "maps/...") vẫn hoạt động.
"""
import os
import sys

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # Đang chạy từ bundle PyInstaller
    os.chdir(sys._MEIPASS)
