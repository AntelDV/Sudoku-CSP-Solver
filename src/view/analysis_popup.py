import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import math

class AnalysisPopup(ctk.CTkToplevel):
    def __init__(self, parent_view, stats_bt: dict, stats_fc: dict):
        super().__init__(parent_view)
        self.stats_bt = stats_bt
        self.stats_fc = stats_fc
        
        self.title("Báo cáo Phân tích So sánh")
        self.geometry("700x300") 
        self.after(50, self.grab_set) 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        khung_chinh = ctk.CTkFrame(self, fg_color="transparent")
        khung_chinh.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        self.tao_tab_thong_ke(khung_chinh)

    def tao_tab_thong_ke(self, parent_frame):
        """Tạo nội dung cho tab Thống kê."""
        parent_frame.grid_columnconfigure((0, 1), weight=1)
        
        # 1. Khung cho BT
        khung_bt = ctk.CTkFrame(parent_frame, fg_color=("#E9ECEF", "#343A40"))
        khung_bt.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=10)
        ctk.CTkLabel(khung_bt, text="Backtracking (Baseline)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.tao_label_ket_qua(khung_bt, "Thời gian thực thi", f"{self.stats_bt.get('execution_time_sec', 0):.6f} s")
        self.tao_label_ket_qua(khung_bt, "Số bước quay lui", f"{self.stats_bt.get('backtracks', 0):,}")
        self.tao_label_ket_qua(khung_bt, "Số nút đã duyệt", f"{self.stats_bt.get('nodes_visited', 0):,}")
        self.tao_label_ket_qua(khung_bt, "Số lượt cắt tỉa", "N/A")

        # 2. Khung cho FC
        khung_fc = ctk.CTkFrame(parent_frame, fg_color=("#E9ECEF", "#343A40"))
        khung_fc.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=10)
        ctk.CTkLabel(khung_fc, text="Forward Checking (Cải tiến)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.tao_label_ket_qua(khung_fc, "Thời gian thực thi", f"{self.stats_fc.get('execution_time_sec', 0):.6f} s")
        self.tao_label_ket_qua(khung_fc, "Số bước quay lui", f"{self.stats_fc.get('backtracks', 0):,}")
        self.tao_label_ket_qua(khung_fc, "Số nút đã duyệt", f"{self.stats_fc.get('nodes_visited', 0):,}")
        self.tao_label_ket_qua(khung_fc, "Số lượt cắt tỉa", f"{self.stats_fc.get('prunes_made', 0):,}")

    def tao_label_ket_qua(self, parent, ten, gia_tri):
        khung = ctk.CTkFrame(parent, fg_color="transparent")
        khung.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(khung, text=f"{ten}:", font=ctk.CTkFont(size=14), text_color="gray").pack(side="left")
        lbl = ctk.CTkLabel(khung, text=gia_tri, font=ctk.CTkFont(size=14, weight="bold"), text_color="#F59E0B")
        lbl.pack(side="right")
        return lbl