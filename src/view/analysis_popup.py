import tkinter as tk
import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.controller.app_controller import AppController

class AnalysisPopup(ctk.CTkToplevel):

    def __init__(self, parent_view, controller: 'AppController', stats_bt: dict, stats_fc: dict, stats_mrv: dict, stats_dlx: dict):
        super().__init__(parent_view)
        
        self.controller = controller
        self.stats_bt = stats_bt
        self.stats_fc = stats_fc
        self.stats_mrv = stats_mrv
        self.stats_dlx = stats_dlx 
        
        self.title("Phân tích So sánh Hiệu năng (4 Thuật toán)")
        self.geometry("1100x650") 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) 

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        self._draw_content()        
        self.after(100, self._safe_grab_set)

    def _safe_grab_set(self):
        try:
            if self.winfo_exists(): self.grab_set()
        except tk.TclError: pass

    def _draw_content(self):
        self.main_frame.grid_columnconfigure((0, 1), weight=1)
        self.main_frame.grid_rowconfigure((0, 1), weight=1)
        
        self._create_card(0, 0, "1. Backtracking", "#E74C3C", self.stats_bt, "backtracks")
        self._create_card(0, 1, "2. Forward Checking", "#3498DB", self.stats_fc, "prunes_made")
        self._create_card(1, 0, "3. FC + MRV (Heuristic)", "#28a745", self.stats_mrv, "prunes_made")
        
        self._create_card(1, 1, "4. Dancing Links (DLX)", "#F1C40F", self.stats_dlx, "nodes_visited", highlight=True)

    def _create_card(self, r, c, title, color, stats, extra_key, highlight=False):
        border_col = color if highlight else None
        border_w = 2 if highlight else 0
        
        frame = ctk.CTkFrame(self.main_frame, fg_color=("#E9ECEF", "#343A40"), border_color=border_col, border_width=border_w)
        frame.grid(row=r, column=c, sticky="nsew", padx=8, pady=8)
        
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=color).pack(pady=(15, 10))
        
        self.tao_label(frame, "Thời gian", f"{stats.get('execution_time_sec', 0):.6f} s")
        
        if extra_key == "backtracks":
            self.tao_label(frame, "Số bước lùi", f"{stats.get('backtracks', 0):,}")
            self.tao_label(frame, "Nút đã duyệt", f"{stats.get('nodes_visited', 0):,}")
        elif extra_key == "prunes_made":
            self.tao_label(frame, "Số bước lùi", f"{stats.get('backtracks', 0):,}")
            self.tao_label(frame, "Cắt tỉa", f"{stats.get('prunes_made', 0):,}")
        elif extra_key == "nodes_visited": 
            self.tao_label(frame, "Số lần Cover", f"{stats.get('nodes_visited', 0):,}")
            self.tao_label(frame, "Trạng thái", "Exact Cover")

    def tao_label(self, parent, ten, gia_tri):
        khung = ctk.CTkFrame(parent, fg_color="transparent")
        khung.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(khung, text=f"{ten}:", font=ctk.CTkFont(size=14), text_color="gray").pack(side="left")
        ctk.CTkLabel(khung, text=gia_tri, font=ctk.CTkFont(size=14, weight="bold"), text_color="#F59E0B").pack(side="right")