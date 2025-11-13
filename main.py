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
from src.view.batch_analysis_popup import BatchAnalysisPopup 
from src.controller.app_controller import AppController
from src.model.sudoku_board import SudokuBoard
from src.model import algorithms
from src.model import algorithms_mrv # Thêm MRV solve
from src.model import visualizer_bt
from src.model import visualizer_fc
from src.model import profiler_bt
from src.model import profiler_fc
from src.model import profiler_mrv # Thêm MRV profile

def main():
    """Hàm chính khởi chạy ứng dụng MVC."""
    
    ctk.set_appearance_mode("dark")  
    ctk.set_default_color_theme("blue") 
    
    model = {
        'SudokuBoard': SudokuBoard,
        'algorithms': algorithms,
        'algorithms_mrv': algorithms_mrv, # Thêm
        'visualizer_bt': visualizer_bt,
        'visualizer_fc': visualizer_fc,
        'profiler_bt': profiler_bt,
        'profiler_fc': profiler_fc,
        'profiler_mrv': profiler_mrv, # Thêm
    }
    
    root = ctk.CTk()
    root.geometry("1020x720") 
    root.title("Ứng dụng CSP vào giải Sudoku")
    root.resizable(True, True) 
    
    root.minsize(1020, 720)
    
    # Truyền cả 2 lớp Popup vào Controller
    controller = AppController(model, AnalysisPopup, BatchAnalysisPopup) 
    view = MainView(root, controller)
    view.pack(fill="both", expand=True) 
    
    controller.set_view(view)
    root.mainloop()

if __name__ == "__main__":
    main()