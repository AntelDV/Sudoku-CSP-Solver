import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import math
from typing import TYPE_CHECKING
import copy # Import copy để sửa lỗi

if TYPE_CHECKING:
    from src.controller.app_controller import AppController

class AnalysisPopup(ctk.CTkToplevel):
    def __init__(self, parent_view, controller: 'AppController', stats_bt: dict, stats_fc: dict, grid_data: list):
        super().__init__(parent_view)
        
        self.controller = controller
        self.stats_bt = stats_bt
        self.stats_fc = stats_fc
        self.grid_data = grid_data # Lưu lại đề bài để chạy MRV
        self.stats_mrv = None # Placeholder
        
        self.title("Báo cáo Phân tích So sánh (Đơn lẻ)")
        self.geometry("700x350") # Tăng chiều cao 1 chút
        self.after(50, self.grab_set) 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Khung chính
        self.grid_rowconfigure(1, weight=0) # Khung chân (footer)

        # Khung chính để chứa các cột
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        # Khung chân (footer) cho công tắc
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        
        self.mrv_switch = ctk.CTkSwitch(
            footer_frame, 
            text="Bao gồm FC+MRV (Hướng phát triển)", 
            font=ctk.CTkFont(size=12, slant="italic"),
            command=self._on_mrv_toggle
        )
        self.mrv_switch.pack(side="right")
        
        # Vẽ 2 cột mặc định
        self._draw_content()

    def _draw_content(self):
        """Vẽ lại nội dung của popup dựa trên việc self.stats_mrv có tồn tại hay không."""
        
        # Xóa nội dung cũ
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # 1. Khung cho BT (Luôn luôn có)
        khung_bt = ctk.CTkFrame(self.main_frame, fg_color=("#E9ECEF", "#343A40"))
        ctk.CTkLabel(khung_bt, text="Backtracking (Baseline)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.tao_label_ket_qua(khung_bt, "Thời gian thực thi", f"{self.stats_bt.get('execution_time_sec', 0):.6f} s")
        self.tao_label_ket_qua(khung_bt, "Số bước quay lui", f"{self.stats_bt.get('backtracks', 0):,}")
        self.tao_label_ket_qua(khung_bt, "Số nút đã duyệt", f"{self.stats_bt.get('nodes_visited', 0):,}")
        self.tao_label_ket_qua(khung_bt, "Số lượt cắt tỉa", "N/A")

        # 2. Khung cho FC (Luôn luôn có)
        khung_fc = ctk.CTkFrame(self.main_frame, fg_color=("#E9ECEF", "#343A40"))
        ctk.CTkLabel(khung_fc, text="Forward Checking (Cải tiến)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.tao_label_ket_qua(khung_fc, "Thời gian thực thi", f"{self.stats_fc.get('execution_time_sec', 0):.6f} s")
        self.tao_label_ket_qua(khung_fc, "Số bước quay lui", f"{self.stats_fc.get('backtracks', 0):,}")
        self.tao_label_ket_qua(khung_fc, "Số nút đã duyệt", f"{self.stats_fc.get('nodes_visited', 0):,}")
        self.tao_label_ket_qua(khung_fc, "Số lượt cắt tỉa", f"{self.stats_fc.get('prunes_made', 0):,}")
        
        # 3. KIỂM TRA XEM CÓ VẼ MRV KHÔNG
        if self.stats_mrv:
            # Mở rộng cửa sổ và cấu hình 3 cột
            self.geometry("1000x350")
            self.main_frame.grid_columnconfigure((0, 1, 2), weight=1)
            khung_bt.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
            khung_fc.grid(row=0, column=1, sticky="nsew", padx=5, pady=0)
            
            # 3. Khung cho MRV
            khung_mrv = ctk.CTkFrame(self.main_frame, fg_color=("#E9ECEF", "#343A40"), border_color="#0D6EFD", border_width=2)
            khung_mrv.grid(row=0, column=2, sticky="nsew", padx=(5, 0), pady=0)
            
            ctk.CTkLabel(khung_mrv, text="FC + MRV (Nâng cao)", font=ctk.CTkFont(size=16, weight="bold"), text_color="#38bdf8").pack(pady=10)
            self.tao_label_ket_qua(khung_mrv, "Thời gian thực thi", f"{self.stats_mrv.get('execution_time_sec', 0):.6f} s")
            self.tao_label_ket_qua(khung_mrv, "Số bước quay lui", f"{self.stats_mrv.get('backtracks', 0):,}")
            self.tao_label_ket_qua(khung_mrv, "Số nút đã duyệt", f"{self.stats_mrv.get('nodes_visited', 0):,}")
            self.tao_label_ket_qua(khung_mrv, "Số lượt cắt tỉa", f"{self.stats_mrv.get('prunes_made', 0):,}")
            
        else:
            # Thu hẹp cửa sổ và cấu hình 2 cột
            self.geometry("700x350")
            self.main_frame.grid_columnconfigure((0, 1), weight=1)
            self.main_frame.grid_columnconfigure(2, weight=0) # Cột 2 không dùng
            khung_bt.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
            khung_fc.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)

    def _on_mrv_toggle(self):
        """Xử lý sự kiện khi công tắc MRV được bật/tắt."""
        is_on = self.mrv_switch.get()
        
        if is_on:
            # Nếu chưa chạy MRV bao giờ, thì chạy
            if self.stats_mrv is None:
                self.mrv_switch.configure(state="disabled", text="Đang chạy MRV...")
                self.update_idletasks() # Cập nhật GUI
                
                # SỬA LỖI 3: Dùng deepcopy để đảm bảo chạy trên đề gốc
                _board, mrv_stats, _solved = self.controller._run_single_algo(
                    copy.deepcopy(self.grid_data), 'profiler_mrv', 'fc_mrv'
                )
                self.stats_mrv = mrv_stats
                
                self.mrv_switch.configure(state="normal", text="Bao gồm FC+MRV (Hướng phát triển)")
            
            # Vẽ lại giao diện (với 3 cột)
            self._draw_content()
            
        else:
            # SỬA LỖI 2: Xóa cache MRV khi tắt
            self.stats_mrv = None
            
            # Tắt -> Vẽ lại giao diện (với 2 cột)
            self._draw_content()

    def tao_label_ket_qua(self, parent, ten, gia_tri):
        khung = ctk.CTkFrame(parent, fg_color="transparent")
        khung.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(khung, text=f"{ten}:", font=ctk.CTkFont(size=14), text_color="gray").pack(side="left")
        lbl = ctk.CTkLabel(khung, text=gia_tri, font=ctk.CTkFont(size=14, weight="bold"), text_color="#F59E0B")
        lbl.pack(side="right")
        return lbl