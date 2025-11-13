import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import math
from typing import TYPE_CHECKING
import copy 

if TYPE_CHECKING:
    from src.controller.app_controller import AppController

class AnalysisPopup(ctk.CTkToplevel):

    def __init__(self, parent_view, controller: 'AppController', stats_bt: dict, stats_fc: dict, grid_data: list):
        """
        Khởi tạo cửa sổ popup.
        
        :param parent_view: Cửa sổ View cha (MainView).
        :param controller: Đối tượng AppController.
        :param stats_bt: Dictionary số liệu của Backtracking.
        :param stats_fc: Dictionary số liệu của Forward Checking.
        :param grid_data: Ma trận 9x9 của đề bài, dùng để chạy MRV.
        """
        super().__init__(parent_view)
        
        self.controller = controller
        self.stats_bt = stats_bt
        self.stats_fc = stats_fc
        self.grid_data = grid_data 
        self.stats_mrv = None 
        
        self.title("Báo cáo Phân tích So sánh (Đơn lẻ)")
        self.geometry("700x350") 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=0) 

        # Khung chính để chứa các cột so sánh
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        # Khung chân (footer) cho nút gạt MRV
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        
        self.mrv_switch = ctk.CTkSwitch(
            footer_frame, 
            text="Bao gồm FC+MRV (Hướng phát triển)", 
            font=ctk.CTkFont(size=12, slant="italic"),
            command=self._on_mrv_toggle
        )
        self.mrv_switch.pack(side="right")
        
        # Vẽ 2 cột mặc định (BT và FC)
        self._draw_content()
        
        # Gọi grab_set an toàn sau khi cửa sổ đã hiển thị
        self.after(100, self._safe_grab_set)

    def _safe_grab_set(self):
        """Gọi grab_set một cách an toàn sau khi cửa sổ đã sẵn sàng."""
        try:
            if self.winfo_exists():
                self.grab_set()
        except tk.TclError:
            # Bỏ qua lỗi nếu cửa sổ bị đóng trước khi grab kịp
            pass

    def _draw_content(self):
        # Xóa nội dung cũ 
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # 1. Khung cho Backtracking (Baseline)
        khung_bt = ctk.CTkFrame(self.main_frame, fg_color=("#E9ECEF", "#343A40"))
        ctk.CTkLabel(khung_bt, text="Backtracking (Baseline)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.tao_label_ket_qua(khung_bt, "Thời gian thực thi", f"{self.stats_bt.get('execution_time_sec', 0):.6f} s")
        self.tao_label_ket_qua(khung_bt, "Số bước quay lui", f"{self.stats_bt.get('backtracks', 0):,}")
        self.tao_label_ket_qua(khung_bt, "Số nút đã duyệt", f"{self.stats_bt.get('nodes_visited', 0):,}")
        self.tao_label_ket_qua(khung_bt, "Số lượt cắt tỉa", "N/A")

        # 2. Khung cho Forward Checking (Cải tiến)
        khung_fc = ctk.CTkFrame(self.main_frame, fg_color=("#E9ECEF", "#343A40"))
        ctk.CTkLabel(khung_fc, text="Forward Checking (Cải tiến)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.tao_label_ket_qua(khung_fc, "Thời gian thực thi", f"{self.stats_fc.get('execution_time_sec', 0):.6f} s")
        self.tao_label_ket_qua(khung_fc, "Số bước quay lui", f"{self.stats_fc.get('backtracks', 0):,}")
        self.tao_label_ket_qua(khung_fc, "Số nút đã duyệt", f"{self.stats_fc.get('nodes_visited', 0):,}")
        self.tao_label_ket_qua(khung_fc, "Số lượt cắt tỉa", f"{self.stats_fc.get('prunes_made', 0):,}")
        
        # Lấy trạng thái Bật/Tắt của nút gạt
        is_on = self.mrv_switch.get()
        
        # 3. Kiểm tra xem có cần vẽ cột MRV không
        if self.stats_mrv and is_on:
            # Cấu hình cho 3 cột
            self.geometry("1000x350")
            self.main_frame.grid_columnconfigure((0, 1, 2), weight=1)
            khung_bt.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
            khung_fc.grid(row=0, column=1, sticky="nsew", padx=5, pady=0)
            
            # 3. Khung cho FC + MRV (Nâng cao)
            khung_mrv = ctk.CTkFrame(self.main_frame, fg_color=("#E9ECEF", "#343A40"), border_color="#0D6EFD", border_width=2)
            khung_mrv.grid(row=0, column=2, sticky="nsew", padx=(5, 0), pady=0)
            
            ctk.CTkLabel(khung_mrv, text="FC + MRV (Nâng cao)", font=ctk.CTkFont(size=16, weight="bold"), text_color="#38bdf8").pack(pady=10)
            self.tao_label_ket_qua(khung_mrv, "Thời gian thực thi", f"{self.stats_mrv.get('execution_time_sec', 0):.6f} s")
            self.tao_label_ket_qua(khung_mrv, "Số bước quay lui", f"{self.stats_mrv.get('backtracks', 0):,}")
            self.tao_label_ket_qua(khung_mrv, "Số nút đã duyệt", f"{self.stats_mrv.get('nodes_visited', 0):,}")
            self.tao_label_ket_qua(khung_mrv, "Số lượt cắt tỉa", f"{self.stats_mrv.get('prunes_made', 0):,}")
            
        else:
            # Cấu hình cho 2 cột
            self.geometry("700x350")
            self.main_frame.grid_columnconfigure((0, 1), weight=1)
            self.main_frame.grid_columnconfigure(2, weight=0) 
            khung_bt.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
            khung_fc.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)

    def _on_mrv_toggle(self):
        is_on = self.mrv_switch.get()
        
        if is_on:
            # Nếu bật và chưa có dữ liệu, thì chạy thuật toán MRV
            if self.stats_mrv is None:
                self.mrv_switch.configure(state="disabled", text="Đang chạy MRV...")
                self.update_idletasks()
                
                # Gọi Controller để chạy thuật toán
                _board, mrv_stats, _solved = self.controller._run_single_algo(
                    copy.deepcopy(self.grid_data), 'profiler_mrv', 'fc_mrv'
                )
                self.stats_mrv = mrv_stats
                
                self.mrv_switch.configure(state="normal", text="Bao gồm FC+MRV (Hướng phát triển)")
            
            # Vẽ lại giao diện (sẽ hiển thị 3 cột)
            self._draw_content()
            
        else:
            self._draw_content()

    def tao_label_ket_qua(self, parent, ten, gia_tri):
        """Tạo một cặp (Tên: Giá trị) trong cột."""
        khung = ctk.CTkFrame(parent, fg_color="transparent")
        khung.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(khung, text=f"{ten}:", font=ctk.CTkFont(size=14), text_color="gray").pack(side="left")
        lbl = ctk.CTkLabel(khung, text=gia_tri, font=ctk.CTkFont(size=14, weight="bold"), text_color="#F59E0B")
        lbl.pack(side="right")
        return lbl