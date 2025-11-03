# File: main.py
# (CẬP NHẬT: Kích thước cửa sổ mới cho layout 2 cột)

import tkinter as tk
import sys
import os

try:
    import customtkinter as ctk
except ImportError:
    print("LỖI: Chưa cài thư viện customtkinter.")
    print("Vui lòng chạy: pip install customtkinter")
    sys.exit(1)

# Thêm đường dẫn `src` để import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    from src.view.main_window import MainView
    from src.controller.app_controller import AppController
    from src.model.sudoku_board import SudokuBoard
    from src.model import algorithms
except ImportError as e:
    print(f"LỖI IMPORT: {e}")
    sys.exit(1)


def main():
    """Hàm chính khởi chạy ứng dụng MVC."""
    
    ctk.set_appearance_mode("dark")  
    ctk.set_default_color_theme("blue") 
    
    # 1. Khởi tạo các lớp Model
    model = {
        'SudokuBoard': SudokuBoard,
        'algorithms': algorithms
    }
    
    # 2. Khởi tạo Root CTk
    root = ctk.CTk()
    
    # --- THAY ĐỔI KÍCH THƯỚC ---
    root.geometry("1000x700") # Rộng hơn cho 2 cột
    root.title("Công cụ Phân tích Thuật toán Sudoku (Đồ án TTNT)")
    root.resizable(False, False) # Vẫn khóa cứng để đảm bảo "hoàn hảo"
    # -----------------------------

    # 3. Khởi tạo Bộ điều khiển
    controller = AppController(model)
    
    # 4. Khởi tạo View (MainView giờ là CTkFrame)
    view = MainView(root, controller)
    view.pack(fill="both", expand=True) 
    
    # 5. Truyền View vào cho Controller
    controller.set_view(view)
    
    # 6. Chạy vòng lặp
    root.mainloop()

if __name__ == "__main__":
    main()