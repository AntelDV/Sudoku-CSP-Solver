import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.controller.app_controller import AppController

class AnalysisPopup(ctk.CTkToplevel):

    def __init__(self, parent_view, controller: 'AppController', stats_bt: dict, stats_fc: dict, stats_mrv: dict):
        """
        Khởi tạo cửa sổ so sánh 3 thuật toán.
        Nhận vào 3 bộ số liệu ngay từ đầu.
        """
        super().__init__(parent_view)
        
        self.controller = controller
        self.stats_bt = stats_bt
        self.stats_fc = stats_fc
        self.stats_mrv = stats_mrv
        
        self.title("Phân tích So sánh Hiệu năng (3 Thuật toán)")
        self.geometry("1050x380") # Mở rộng chiều ngang để chứa 3 cột

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) 

        # Khung chính
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        # Vẽ nội dung
        self._draw_content()
        
        self.after(100, self._safe_grab_set)

    def _safe_grab_set(self):
        try:
            if self.winfo_exists():
                self.grab_set()
        except tk.TclError:
            pass

    def _draw_content(self):
        # Cấu hình 3 cột đều nhau
        self.main_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # --- CỘT 1: BACKTRACKING ---
        khung_bt = ctk.CTkFrame(self.main_frame, fg_color=("#E9ECEF", "#343A40"))
        khung_bt.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(khung_bt, text="Backtracking (Baseline)", font=ctk.CTkFont(size=16, weight="bold"), text_color="#E74C3C").pack(pady=(15, 10))
        self.tao_label_ket_qua(khung_bt, "Thời gian", f"{self.stats_bt.get('execution_time_sec', 0):.6f} s")
        self.tao_label_ket_qua(khung_bt, "Bước quay lui", f"{self.stats_bt.get('backtracks', 0):,}")
        self.tao_label_ket_qua(khung_bt, "Nút đã duyệt", f"{self.stats_bt.get('nodes_visited', 0):,}")
        self.tao_label_ket_qua(khung_bt, "Cắt tỉa", "N/A")

        # --- CỘT 2: FORWARD CHECKING ---
        khung_fc = ctk.CTkFrame(self.main_frame, fg_color=("#E9ECEF", "#343A40"))
        khung_fc.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(khung_fc, text="Forward Checking", font=ctk.CTkFont(size=16, weight="bold"), text_color="#3498DB").pack(pady=(15, 10))
        self.tao_label_ket_qua(khung_fc, "Thời gian", f"{self.stats_fc.get('execution_time_sec', 0):.6f} s")
        self.tao_label_ket_qua(khung_fc, "Bước quay lui", f"{self.stats_fc.get('backtracks', 0):,}")
        self.tao_label_ket_qua(khung_fc, "Nút đã duyệt", f"{self.stats_fc.get('nodes_visited', 0):,}")
        self.tao_label_ket_qua(khung_fc, "Cắt tỉa", f"{self.stats_fc.get('prunes_made', 0):,}")

        # --- CỘT 3: FC + MRV ---
        khung_mrv = ctk.CTkFrame(self.main_frame, fg_color=("#E9ECEF", "#343A40"), border_color="#28a745", border_width=2)
        khung_mrv.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(khung_mrv, text="FC + MRV (Tối ưu)", font=ctk.CTkFont(size=16, weight="bold"), text_color="#28a745").pack(pady=(15, 10))
        self.tao_label_ket_qua(khung_mrv, "Thời gian", f"{self.stats_mrv.get('execution_time_sec', 0):.6f} s")
        self.tao_label_ket_qua(khung_mrv, "Bước quay lui", f"{self.stats_mrv.get('backtracks', 0):,}")
        self.tao_label_ket_qua(khung_mrv, "Nút đã duyệt", f"{self.stats_mrv.get('nodes_visited', 0):,}")
        self.tao_label_ket_qua(khung_mrv, "Cắt tỉa", f"{self.stats_mrv.get('prunes_made', 0):,}")

    def tao_label_ket_qua(self, parent, ten, gia_tri):
        """Tạo một dòng thông tin."""
        khung = ctk.CTkFrame(parent, fg_color="transparent")
        khung.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(khung, text=f"{ten}:", font=ctk.CTkFont(size=14), text_color="gray").pack(side="left")
        lbl = ctk.CTkLabel(khung, text=gia_tri, font=ctk.CTkFont(size=14, weight="bold"), text_color="#F59E0B")
        lbl.pack(side="right")
        return lbl