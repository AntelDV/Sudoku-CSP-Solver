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
from src.model import visualizer_bt
from src.model import visualizer_fc
from src.model import visualizer_mrv  # <--- THÊM MỚI Ở ĐÂY
from src.model import profiler_bt
from src.model import profiler_fc
from src.model import profiler_mrv 

def main():

    # Cấu hình giao diện CustomTkinter
    ctk.set_appearance_mode("dark")  
    ctk.set_default_color_theme("blue") 
    
    model = {
        'SudokuBoard': SudokuBoard,
        'algorithms': algorithms,
        'visualizer_bt': visualizer_bt,
        'visualizer_fc': visualizer_fc,
        'visualizer_mrv': visualizer_mrv, # <--- THÊM MỚI VÀO DICTIONARY
        'profiler_bt': profiler_bt,
        'profiler_fc': profiler_fc,
        'profiler_mrv': profiler_mrv,
    }
    
    root = ctk.CTk()
    root.geometry("1020x720") 
    root.title("Ứng dụng CSP vào giải Sudoku")
    root.resizable(True, True) 
    root.minsize(1020, 720)
    
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    controller = AppController(model, AnalysisPopup, BatchAnalysisPopup, base_dir) 

    view = MainView(root, controller)
    view.pack(fill="both", expand=True) 
    controller.set_view(view)
    root.mainloop()

if __name__ == "__main__":
    main()