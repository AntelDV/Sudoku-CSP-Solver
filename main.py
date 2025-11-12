import tkinter as tk
import sys
import os

try:
    import customtkinter as ctk
except ImportError:
    print("LỖI: Chưa cài thư viện customtkinter.")
    print("Vui lòng chạy: pip install customtkinter")
    sys.exit(1)

from src.view.main_window import MainView
from src.view.analysis_popup import AnalysisPopup 
from src.controller.app_controller import AppController
from src.model.sudoku_board import SudokuBoard
from src.model import algorithms
from src.model import visualizer_bt
from src.model import visualizer_fc
from src.model import profiler_bt
from src.model import profiler_fc

def main():
    """Hàm chính khởi chạy ứng dụng MVC."""
    
    ctk.set_appearance_mode("dark")  
    ctk.set_default_color_theme("blue") 
    
    model = {
        'SudokuBoard': SudokuBoard,
        'algorithms': algorithms,
        'visualizer_bt': visualizer_bt,
        'visualizer_fc': visualizer_fc,
        'profiler_bt': profiler_bt,
        'profiler_fc': profiler_fc,
    }
    
    root = ctk.CTk()
    root.geometry("1000x700") 
    root.title("Công cụ Phân tích Thuật toán Sudoku (Đồ án TTNT)")
    root.resizable(True, True) 
    

    controller = AppController(model, AnalysisPopup) 
    view = MainView(root, controller)
    view.pack(fill="both", expand=True) 
    
    controller.set_view(view)
    root.mainloop()

if __name__ == "__main__":
    main()