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
from src.model import visualizer_mrv
from src.model import profiler_bt
from src.model import profiler_fc
from src.model import profiler_mrv 
from src.model import solver_dlx 

def main():

    # Cấu hình giao diện CustomTkinter
    ctk.set_appearance_mode("dark")  
    ctk.set_default_color_theme("blue") 
    
    # Đóng gói các module Model để chuyển cho Controller
    model = {
        'SudokuBoard': SudokuBoard,
        'algorithms': algorithms,
        'visualizer_bt': visualizer_bt,
        'visualizer_fc': visualizer_fc,
        'visualizer_mrv': visualizer_mrv, 
        'profiler_bt': profiler_bt,
        'profiler_fc': profiler_fc,
        'profiler_mrv': profiler_mrv,
        'solver_dlx': solver_dlx,
    }
    
    root = ctk.CTk()
    
    root.geometry("1280x850") 
    root.title("Ứng dụng CSP vào giải Sudoku")
    root.resizable(True, True) 
    root.minsize(1100, 750) 
    
    # Xác định đường dẫn gốc 
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # Khởi tạo Controller
    controller = AppController(model, AnalysisPopup, None, base_dir) 

    # Khởi tạo View chính
    view = MainView(root, controller)
    view.pack(fill="both", expand=True) 
    
    # Kết nối View và Controller
    controller.set_view(view)
    
    root.mainloop()

if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
    
    
    
    

    
    
   