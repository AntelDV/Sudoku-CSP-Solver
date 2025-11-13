import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from src.controller.app_controller import AppController

# --- Các hằng số Cấu hình Giao diện ---
KICH_THUOC_LUOI = 9
KICH_THUOC_O = 60 

MAU_O_BINH_THUONG = ("#FFFFFF", "#FFFFFF") 
MAU_O_GOC_FG = ("#D0D0D0", "#D0D0D0")      
MAU_O_GOC_TEXT = ("#000000", "#000000") 
MAU_O_GIAI_TEXT = ("#000000", "#000000") 

MAU_VIEN_3x3 = ("#000000", "#000000") 
MAU_VIEN_LUOI = ("#000000", "#000000") 
MAU_O_LOI = "#E74C3C" 

# Cấu hình màu sắc cho Chế độ Trực quan hóa (Demo)
MAU_NEN_THU = "#28a745"       
MAU_CHU_THU = "#FFFFFF"       
MAU_NEN_QUAY_LUI = "#E74C3C" 
MAU_CHU_QUAY_LUI = "#FFFFFF"  
MAU_VIEN_HANG_XOM = "#0052cc" 
MAU_VIEN_KHOI_PHUC = "#6a7075" 


class MainView(ctk.CTkFrame):
 
    def __init__(self, root: ctk.CTk, controller: 'AppController'):
        """
        Khởi tạo MainView.
        
        :param root: Đối tượng CTk (cửa sổ gốc) của ứng dụng.
        :param controller: Đối tượng AppController.
        """
        super().__init__(root, fg_color="#0d1b2a") 
        self.root = root
        self.controller = controller
        
        # Dictionary lưu trữ 81 ô Entry 
        self.cac_o_nhap = {} 
        self.algo_var = ctk.StringVar() 
        
        # Các thành phần (widgets) sẽ được cập nhật
        self.lbl_puzzle_info = None
        self.switch_demo_mode = None
        self.slider_demo_speed = None
        self.lbl_demo_stats = None 
        
        self.btn_load_file = None
        self.btn_csv_easy = None
        self.btn_csv_medium = None
        self.btn_csv_hard = None
        self.btn_csv_extreme = None
        
        self.btn_giai = None
        self.btn_sosanh = None
        self.btn_xoa = None
        self.btn_batch_analysis = None 
        
        self.khung_ket_qua_nhanh = None
        self.lbl_fast_solve_time = None
        self.lbl_fast_solve_backtracks = None
        
        # Lệnh kiểm tra hợp lệ cho ô Entry (chỉ cho phép 1-9)
        self.vcmd = (self.root.register(self.kiem_tra_nhap_lieu), '%P')
        
        self.khoi_tao_giao_dien()

    def kiem_tra_nhap_lieu(self, gia_tri_moi):
        """Chỉ cho phép nhập 1 chữ số (1-9)."""
        if len(gia_tri_moi) > 1: return False
        if gia_tri_moi == "": return True
        return gia_tri_moi.isdigit() and '1' <= gia_tri_moi <= '9'

    def khoi_tao_giao_dien(self):
        """Khởi tạo và sắp xếp bố cục (layout) của ứng dụng."""
        self.grid_columnconfigure(0, weight=1, minsize=600) # Cột lưới Sudoku
        self.grid_columnconfigure(1, minsize=380)          # Cột điều khiển
        self.grid_rowconfigure(0, weight=1)
        
        # 1. Khung Lưới
        khung_luoi = ctk.CTkFrame(self, fg_color="transparent")
        khung_luoi.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.tao_khung_luoi_sudoku(khung_luoi)
        
        # 2. Khung Điều khiển
        khung_dieu_khien = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        khung_dieu_khien.grid(row=0, column=1, sticky="nsew")

        khung_controls_inner = ctk.CTkFrame(khung_dieu_khien, fg_color="transparent", corner_radius=0)
        khung_controls_inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tao_khung_dieu_khien(khung_controls_inner)

    def tao_khung_luoi_sudoku(self, parent):
        """Tạo lưới 9x9 gồm 81 ô Entry."""
        khung_container = ctk.CTkFrame(parent, fg_color="transparent")
        khung_container.pack(expand=True)
        
        self.cac_o_nhap = {}
        # Lặp 3x3 (tạo các khối lớn)
        for khoi_hang in range(3):
            for khoi_cot in range(3):
                khung_3x3 = ctk.CTkFrame(khung_container, fg_color=MAU_VIEN_3x3[0], corner_radius=0)
                khung_3x3.grid(row=khoi_hang, column=khoi_cot, padx=(3,0), pady=(3,0))
                
                # Lặp 3x3 (tạo các ô nhỏ bên trong)
                for o_hang in range(3):
                    for o_cot in range(3):
                        hang_toan_cuc = (khoi_hang * 3) + o_hang
                        cot_toan_cuc = (khoi_cot * 3) + o_cot
                        
                        o_nhap_lieu = ctk.CTkEntry(
                            khung_3x3, 
                            width=KICH_THUOC_O,  
                            height=KICH_THUOC_O, 
                            font=ctk.CTkFont(size=24, weight="bold"), 
                            justify="center",
                            corner_radius=0, 
                            border_width=1,
                            fg_color=MAU_O_BINH_THUONG[0],
                            text_color=MAU_O_GIAI_TEXT[0], 
                            border_color = MAU_VIEN_LUOI[0], 
                            validate="key", 
                            validatecommand=self.vcmd,
                        )
                        
                        o_nhap_lieu.grid(
                            row=o_hang, column=o_cot, 
                            padx=(1,0), pady=(1,0) 
                        )
                        # Lưu ô vào dictionary để truy cập sau
                        self.cac_o_nhap[(hang_toan_cuc, cot_toan_cuc)] = o_nhap_lieu
                        
                        # Gán sự kiện (nhả phím) cho Controller
                        o_nhap_lieu.bind(
                            "<KeyRelease>", 
                            lambda event, r=hang_toan_cuc, c=cot_toan_cuc: 
                                self.controller.handle_grid_modified(event, r, c)
                        )

    
    def tao_khung_dieu_khien(self, parent):
        """Tạo cột điều khiển bên phải (gồm các nút, slider, ...)."""
        
        # Tiêu đề và Nút Cài đặt 
        khung_tieu_de = ctk.CTkFrame(parent, fg_color="transparent")
        khung_tieu_de.pack(fill="x", pady=(10, 5))
        khung_tieu_de.grid_columnconfigure(0, weight=1)
        khung_tieu_de.grid_columnconfigure(1, weight=0)
        
        ctk.CTkLabel(
            khung_tieu_de, 
            text="SUDOKU SOLVER", 
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#38bdf8"
        ).grid(row=0, column=0, sticky="ew", padx=(45, 0))
        
        self.btn_batch_analysis = ctk.CTkButton(
            khung_tieu_de,
            text="⚙️", 
            font=ctk.CTkFont(size=24),
            width=35,
            height=35,
            fg_color="transparent",
            hover_color="#475569"
        )
        self.btn_batch_analysis.grid(row=0, column=1, sticky="e", padx=(0, 20))
        
        # Tạo các nhóm widget con
        self.tao_khung_nap_de(parent)
        ctk.CTkFrame(parent, height=2, fg_color="#334155").pack(fill="x", padx=0, pady=10)

        self.tao_khung_hanh_dong(parent)
        ctk.CTkFrame(parent, height=2, fg_color="#334155").pack(fill="x", padx=0, pady=10)

        self.tao_khung_che_do_demo(parent)
        
        # Gán tất cả các lệnh (command) của widget cho Controller
        self.set_controller_references()
        # Cấu hình widget Demo (ẩn/hiện)
        self.toggle_demo_widgets()
        # Đặt trạng thái ban đầu (vô hiệu hóa) cho các nút
        self.set_buttons_state_on_load()


    def tao_khung_nap_de(self, parent):
        """Tạo nhóm widget 'Nạp Dữ liệu'."""
        khung_nap = ctk.CTkFrame(parent, fg_color="transparent")
        khung_nap.pack(fill="x", pady=5)
        
        self.btn_load_file = ctk.CTkButton(
            khung_nap,
            text="📁 NẠP DỮ LIỆU",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#0D6EFD", hover_color="#0A58CA", 
            height=32 
        )
        
        self.btn_load_file.pack(pady=4)
        self.lbl_puzzle_info = ctk.CTkLabel(
            khung_nap,
            text="Chưa nạp đề bài nào",
            font=ctk.CTkFont(size=13, slant="italic"),
            text_color="#94a3b8",
            wraplength=300 
        )
        self.lbl_puzzle_info.pack(fill="x", pady=5)
        
        # Các nút lấy đề từ CSV
        khung_kho = ctk.CTkFrame(khung_nap, fg_color="transparent")
        khung_kho.pack(pady=5)
        khung_kho.grid_columnconfigure((0, 1), weight=1)
        
        self.btn_csv_easy = ctk.CTkButton(
            khung_kho, text="Lấy Đề Dễ",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#28a745", hover_color="#32CD32",
            text_color="#FFFFFF",
            height=28
        )
        self.btn_csv_easy.grid(row=0, column=0, padx=(0, 3), pady=2)
        
        self.btn_csv_medium = ctk.CTkButton(
            khung_kho, text="Lấy Đề Trung Bình",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#FFC107", hover_color="#FFD700", 
            text_color="#000000",
            height=28
        )
        self.btn_csv_medium.grid(row=0, column=1, padx=(3, 0), pady=2)
        
        self.btn_csv_hard = ctk.CTkButton(
            khung_kho, text="Lấy Đề Khó",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#E74C3C", hover_color="#EC7063",
            text_color="#FFFFFF",
            height=28
        )
        self.btn_csv_hard.grid(row=1, column=0, padx=(0, 3), pady=2)
        
        self.btn_csv_extreme = ctk.CTkButton(
            khung_kho, text="Lấy Đề Siêu Khó",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#8E44AD", hover_color="#A569BD",
            text_color="#FFFFFF",
            height=28
        )
        self.btn_csv_extreme.grid(row=1, column=1, padx=(3, 0), pady=2)
        
    def tao_khung_hanh_dong(self, parent):
        """Tạo nhóm widget 'Hành động' (Chọn thuật toán, Giải, So sánh, Xóa)."""
        khung_hanh_dong = ctk.CTkFrame(parent, fg_color="transparent")
        khung_hanh_dong.pack(fill="x", pady=5)
        
        # ComboBox chọn thuật toán
        self.algo_var.set('Backtracking (Baseline)') 
        combo_fast_solve = ctk.CTkComboBox(
            khung_hanh_dong,
            variable=self.algo_var, 
            font=ctk.CTkFont(size=13),
            values=['Backtracking (Baseline)', 
                    'Forward Checking (Cải tiến)',
                    'FC + MRV (Nâng cao)'], 
            state="readonly",
            height=30,
            width=220
        )
        combo_fast_solve.pack(pady=(5, 5))

        # Khung chứa 3 nút: Giải, So sánh, Xóa
        khung_nut_hanh_dong = ctk.CTkFrame(khung_hanh_dong, fg_color="transparent")
        khung_nut_hanh_dong.pack()

        self.btn_giai = ctk.CTkButton(
            khung_nut_hanh_dong, text="⚡ GIẢI",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#28a745", hover_color="#32CD32", 
            text_color="#FFFFFF", height=35,
            width=105
        )
        self.btn_giai.grid(row=0, column=0, padx=(0, 3))
        
        self.btn_sosanh = ctk.CTkButton(
            khung_nut_hanh_dong, text="📊 SO SÁNH", 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#8E44AD", hover_color="#A569BD", 
            text_color="#FFFFFF", height=35,
            width=105
        )
        self.btn_sosanh.grid(row=0, column=1, padx=3)

        self.btn_xoa = ctk.CTkButton(
            khung_nut_hanh_dong, text="✕ XÓA",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#E74C3C", hover_color="#EC7063", 
            text_color="#FFFFFF", height=35,
            width=105
        )
        self.btn_xoa.grid(row=0, column=2, padx=(3, 0))
        
        # Khung (ẩn) để hiển thị kết quả 'Giải nhanh'
        self.khung_ket_qua_nhanh = ctk.CTkFrame(khung_hanh_dong, fg_color="transparent")
        
        self.lbl_fast_solve_time = ctk.CTkLabel(
            self.khung_ket_qua_nhanh, 
            text="Thời gian: 0.00s", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#3498DB"
        )
        self.lbl_fast_solve_time.pack(pady=(10, 2))
        
        self.lbl_fast_solve_backtracks = ctk.CTkLabel(
            self.khung_ket_qua_nhanh, 
            text="Số bước lui: 0", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#F59E0B"
        )
        self.lbl_fast_solve_backtracks.pack(pady=(2, 5))

    def show_fast_solve_stats(self, stats: dict):
        """Hiển thị thống kê (Thời gian, Bước lui) của chế độ 'Giải nhanh'."""
        time_val = stats.get('execution_time_sec', 0)
        backtracks_val = stats.get('backtracks', 0)
        
        self.lbl_fast_solve_time.configure(text=f"Thời gian thực thi: {time_val:.6f} s")
        self.lbl_fast_solve_backtracks.configure(text=f"Số bước quay lui: {backtracks_val:,}")
        
        self.khung_ket_qua_nhanh.pack(fill="x", pady=(5,0))

    def clear_fast_solve_stats(self):
        """Ẩn thống kê của chế độ 'Giải nhanh'."""
        self.khung_ket_qua_nhanh.pack_forget()

    def tao_khung_che_do_demo(self, parent):
        """Tạo nhóm widget 'Chế độ Demo' (Nút gạt, Slider tốc độ)."""
        
        khung_demo = ctk.CTkFrame(parent, fg_color="transparent")
        khung_demo.pack(fill="x", pady=10)
        
        self.switch_demo_mode = ctk.CTkSwitch(
            khung_demo, text="Bật Demo Trực Quan Hóa", 
            font=ctk.CTkFont(size=13, weight="bold"),
            onvalue=True, offvalue=False, text_color="#e2e8f0",
            command=self.toggle_demo_widgets
        )
        self.switch_demo_mode.pack(pady=5, padx=10, anchor="w")
        
        self.slider_demo_speed = ctk.CTkSlider(khung_demo)
        self.slider_demo_speed.set(0.2) 
        self.slider_demo_speed.pack(pady=(10, 5))
        
        self.lbl_demo_stats = ctk.CTkLabel(
            khung_demo, text="Số bước lui: 0", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#F59E0B"
        )
        self.lbl_demo_stats.pack(pady=5)
        
    def toggle_demo_widgets(self):
        """Xử lý sự kiện Bật/Tắt nút gạt Demo (ẩn/hiện slider và đổi tên nút)."""
        is_on = self.switch_demo_mode.get()
        if is_on:
            self.slider_demo_speed.pack(pady=(10, 5))
            self.lbl_demo_stats.pack(pady=5)
            self.btn_giai.configure(text="▶ BẮT ĐẦU DEMO") 
        else:
            self.slider_demo_speed.pack_forget()
            self.lbl_demo_stats.pack_forget()
            self.btn_giai.configure(text="⚡ GIẢI") 
    
    def set_controller_references(self):
        """Gán tất cả các hàm xử lý sự kiện (command) cho Controller."""
        self.btn_load_file.configure(command=self.controller.handle_load_file)
        self.btn_csv_easy.configure(command=lambda: self.controller.handle_get_csv_puzzle('easy'))
        self.btn_csv_medium.configure(command=lambda: self.controller.handle_get_csv_puzzle('medium'))
        self.btn_csv_hard.configure(command=lambda: self.controller.handle_get_csv_puzzle('hard'))
        self.btn_csv_extreme.configure(command=lambda: self.controller.handle_get_csv_puzzle('extreme'))
        
        self.btn_giai.configure(command=self.controller.handle_solve)
        self.btn_sosanh.configure(command=self.controller.handle_compare)
        self.btn_xoa.configure(command=self.controller.handle_clear)
        self.btn_batch_analysis.configure(command=self.controller.handle_batch_compare_setup)

    def get_selected_algorithm(self) -> (str, bool):
        """
        Lấy thuật toán và chế độ (Demo/Giải nhanh) người dùng đã chọn.
        
        :return: (tuple) (algo_key, is_demo_mode)
        """
        selected = self.algo_var.get()
        is_demo = self.switch_demo_mode.get()
        
        # Chuyển đổi tên hiển thị sang key nội bộ
        if "FC + MRV" in selected:
            algo_key = "fc_mrv"
        elif "Forward Checking" in selected:
            algo_key = "fc"
        else:
            algo_key = "bt"
            
        if is_demo:
            # Nếu là demo MRV, tạm thời dùng demo của FC
            if algo_key == "fc_mrv":
                return "visualizer_fc", True
            
            return ("visualizer_fc" if algo_key == "fc" else "visualizer_bt"), True
        else:
            return algo_key, False
    
    def get_demo_speed(self):
        """Lấy giá trị tốc độ từ slider và chuyển thành miligiây (ms)."""
        val = self.slider_demo_speed.get()
        if val < 0.01: return 500 
        # Công thức tính delay (giá trị thấp = delay cao)
        return int(500 * (1.0 - val)**2) 

    def update_puzzle_info(self, text: str):
        """Cập nhật nhãn thông tin đề bài (ví dụ: "Đã nạp: Đề Dễ")."""
        self.lbl_puzzle_info.configure(text=text)

    def load_puzzle_to_grid(self, grid_data):
        """
        Tải một đề bài (ma trận) lên lưới 81 ô.
        
        :param grid_data: Ma trận 9x9 (list[list[int]]).
        """
        self.clear_fast_solve_stats() 
        
        # 1. Xóa sạch lưới về trạng thái trắng
        for r in range(KICH_THUOC_LUOI):
            for c in range(KICH_THUOC_LUOI):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                o_nhap_lieu.configure(state='normal', 
                                     fg_color=MAU_O_BINH_THUONG[0],
                                     text_color=MAU_O_GIAI_TEXT[0], 
                                     border_width=1,
                                     border_color = MAU_VIEN_LUOI[0]) 
                o_nhap_lieu.delete(0, "end")
        
        # 2. Điền các số của đề bài (ô gốc)
        for r in range(KICH_THUOC_LUOI):
            for c in range(KICH_THUOC_LUOI):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                val = grid_data[r][c]
                
                if val != 0:
                    o_nhap_lieu.insert(0, str(val))
                    # Tô màu xám và vô hiệu hóa các ô gốc
                    o_nhap_lieu.configure(state='disabled', 
                                         fg_color=MAU_O_GOC_FG[0],
                                         text_color=MAU_O_GOC_TEXT[0]) 
                else:
                    o_nhap_lieu.configure(state='normal', 
                                         fg_color=MAU_O_BINH_THUONG[0],
                                         text_color=MAU_O_GIAI_TEXT[0]) 

    def update_grid_with_solution(self, solution_data, puzzle_data):
        """
        Hiển thị lời giải cuối cùng lên lưới.
        
        :param solution_data: Ma trận 9x9 lời giải.
        :param puzzle_data: Ma trận 9x9 đề bài gốc (để tô màu).
        """
        for r in range(KICH_THUOC_LUOI):
            for c in range(KICH_THUOC_LUOI):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                val_goc = puzzle_data[r][c]
                val_giai = solution_data[r][c]
                
                o_nhap_lieu.delete(0, "end")
                o_nhap_lieu.insert(0, str(val_giai))
                
                if val_goc != 0:
                    # Ô gốc: màu xám
                    o_nhap_lieu.configure(state='disabled',
                                         fg_color=MAU_O_GOC_FG[0],
                                         text_color=MAU_O_GOC_TEXT[0], 
                                         border_width=1,
                                         border_color = MAU_VIEN_LUOI[0]) 
                else:
                    # Ô được giải: màu trắng
                    o_nhap_lieu.configure(state='normal',
                                         fg_color=MAU_O_BINH_THUONG[0],
                                         text_color=MAU_O_GIAI_TEXT[0], 
                                         border_width=1,
                                         border_color = MAU_VIEN_LUOI[0]) 
                # Vô hiệu hóa toàn bộ lưới sau khi giải xong
                o_nhap_lieu.configure(state='disabled')

    def clear_grid_and_stats(self):
        """Xóa sạch lưới và reset tất cả thống kê."""
        self.clear_fast_solve_stats() 
        
        for r in range(KICH_THUOC_LUOI):
            for c in range(KICH_THUOC_LUOI):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                o_nhap_lieu.configure(state='normal', 
                                     fg_color=MAU_O_BINH_THUONG[0],
                                     text_color=MAU_O_GIAI_TEXT[0], 
                                     border_width=1,
                                     border_color = MAU_VIEN_LUOI[0]) 
                o_nhap_lieu.delete(0, "end")
        
        self.update_puzzle_info("Chưa nạp đề bài nào")
        
        # Chỉ reset bộ đếm demo khi nhấn 'XÓA'
        if self.lbl_demo_stats: 
            self.lbl_demo_stats.configure(text="Số bước lui: 0")

    def get_grid_data(self):
        """Lấy ma trận 9x9 từ các ô Entry do người dùng nhập vào."""
        grid_data = []
        for r in range(KICH_THUOC_LUOI):
            row_data = []
            for c in range(KICH_THUOC_LUOI):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                val = o_nhap_lieu.get()
                if val == "":
                    row_data.append(0)
                elif val.isdigit():
                    row_data.append(int(val))
                else:
                    raise ValueError(f"Giá trị không hợp lệ tại ô ({r+1}, {c+1})")
            grid_data.append(row_data)
        return grid_data
    
    def is_grid_empty(self):
        """Kiểm tra xem lưới có đang trống hoàn toàn không."""
        for r in range(KICH_THUOC_LUOI):
            for c in range(KICH_THUOC_LUOI):
                if self.cac_o_nhap[(r, c)].get() != "":
                    return False
        return True
        
    def show_message(self, title, message, is_error=False):
        """Hiển thị một thông báo (showinfo) hoặc lỗi (showerror)."""
        if is_error:
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
            
    def set_cell_validity(self, r, c, is_valid: bool):
        """Tô viền đỏ cho ô nếu vi phạm ràng buộc (khi người dùng nhập tay)."""
        o_nhap_lieu = self.cac_o_nhap[(r, c)]
        if not is_valid:
            o_nhap_lieu.configure(border_color=MAU_O_LOI, border_width=3)
        else:
            if o_nhap_lieu.cget("state") == "normal":
                o_nhap_lieu.configure(border_color=MAU_VIEN_LUOI[0], border_width=1)
            
    # --- Các hàm quản lý Trạng thái Nút ---

    def set_buttons_state_on_load(self):
        """Trạng thái ban đầu khi mới mở app."""
        self.btn_load_file.configure(state="normal")
        self.btn_csv_easy.configure(state="disabled")
        self.btn_csv_medium.configure(state="disabled")
        self.btn_csv_hard.configure(state="disabled")
        self.btn_csv_extreme.configure(state="disabled")
        self.btn_giai.configure(state="disabled")
        self.btn_sosanh.configure(state="disabled")
        self.btn_batch_analysis.configure(state="disabled")
        self.btn_xoa.configure(state="disabled")

    def set_buttons_state_csv_loaded(self):
        """Trạng thái sau khi nạp file CSV thành công."""
        self.btn_load_file.configure(state="normal")
        self.btn_csv_easy.configure(state="normal")
        self.btn_csv_medium.configure(state="normal")
        self.btn_csv_hard.configure(state="normal")
        self.btn_csv_extreme.configure(state="normal")
        self.btn_giai.configure(state="disabled")
        self.btn_sosanh.configure(state="disabled")
        self.btn_batch_analysis.configure(state="normal")
        self.btn_xoa.configure(state="disabled")

    def set_buttons_state_puzzle_on_grid(self, csv_loaded: bool):
        """Trạng thái khi đã có đề bài trên lưới (sẵn sàng giải)."""
        self.btn_load_file.configure(state="normal")
        if csv_loaded:
            self.btn_csv_easy.configure(state="normal")
            self.btn_csv_medium.configure(state="normal")
            self.btn_csv_hard.configure(state="normal")
            self.btn_csv_extreme.configure(state="normal")
            self.btn_batch_analysis.configure(state="normal")
        else:
            self.btn_csv_easy.configure(state="disabled")
            self.btn_csv_medium.configure(state="disabled")
            self.btn_csv_hard.configure(state="disabled")
            self.btn_csv_extreme.configure(state="disabled")
            self.btn_batch_analysis.configure(state="disabled")
        
        self.btn_giai.configure(state="normal")
        self.btn_sosanh.configure(state="normal")
        self.btn_xoa.configure(state="normal")

    def set_buttons_state_visualizing(self, is_running: bool, csv_loaded: bool):
        """Trạng thái khi đang chạy (Demo, Giải nhanh, hoặc Thực nghiệm)."""
        is_demo_mode = self.switch_demo_mode.get()
        
        if is_running:
            # Vô hiệu hóa hầu hết các nút
            self.btn_load_file.configure(state="disabled")
            self.btn_csv_easy.configure(state="disabled")
            self.btn_csv_medium.configure(state="disabled")
            self.btn_csv_hard.configure(state="disabled")
            self.btn_csv_extreme.configure(state="disabled")
            self.btn_sosanh.configure(state="disabled")
            self.btn_batch_analysis.configure(state="disabled")
            self.btn_xoa.configure(state="disabled")
            self.switch_demo_mode.configure(state="disabled")
            
            # Khóa toàn bộ lưới
            for r in range(9):
                for c in range(9):
                    self.cac_o_nhap[(r, c)].configure(state="disabled")
            
            if is_demo_mode:
                # Nút "Giải" trở thành nút "Dừng Demo"
                self.btn_giai.configure(text="❚❚ DỪNG DEMO", state="normal", fg_color="#E74C3C", hover_color="#EC7063")
            else:
                self.btn_giai.configure(state="disabled")

        else:
            # Kích hoạt lại các nút
            self.btn_load_file.configure(state="normal")
            self.switch_demo_mode.configure(state="normal")
            
            # Mở khóa lưới (tùy thuộc vào trạng thái)
            if self.controller.current_puzzle_data and self.controller.last_demo_status != "solved":
                self.load_puzzle_to_grid(self.controller.current_puzzle_data)
            elif not self.controller.current_puzzle_data:
                for r in range(9):
                    for c in range(9):
                        self.cac_o_nhap[(r, c)].configure(state="normal")
            
            self.set_buttons_state_puzzle_on_grid(csv_loaded)
            self.toggle_demo_widgets() # Đặt lại tên nút "Giải"
            self.btn_giai.configure(fg_color="#28a745", hover_color="#32CD32")


    def cap_nhat_o_visual(self, data: dict, puzzle_data: list):
        """
        Cập nhật GUI trong chế độ Demo (Trực quan hóa).
        
        :param data: Dictionary trạng thái từ generator (ví dụ: 'action', 'cell').
        :param puzzle_data: Ma trận 9x9 của đề bài gốc (để reset màu).
        """
        if not puzzle_data: 
            return
            
        action = data.get("action")
        # 1. Reset lại màu sắc của toàn bộ lưới về trạng thái gốc
        self.reset_all_cells_visual(puzzle_data)
        
        if action == "try":
            # 2a. Tô màu nền XANH cho ô đang "Thử"
            r, c = data["cell"]
            num = data["num"]
            o_nhap_lieu = self.cac_o_nhap[(r, c)]
            
            o_nhap_lieu.configure(state="normal")
            o_nhap_lieu.delete(0, "end")
            o_nhap_lieu.insert(0, str(num))
            o_nhap_lieu.configure(
                state="disabled", 
                fg_color=MAU_NEN_THU, 
                text_color=MAU_CHU_THU, 
                border_width=2
            )
        
        elif action == "backtrack":
            # 2b. Tô màu nền ĐỎ cho ô đang "Quay lui"
            r, c = data["cell"]
            o_nhap_lieu = self.cac_o_nhap[(r, c)]
            
            o_nhap_lieu.configure(state="normal")
            o_nhap_lieu.delete(0, "end")
            o_nhap_lieu.configure(
                state="disabled", 
                fg_color=MAU_NEN_QUAY_LUI, 
                text_color=MAU_CHU_QUAY_LUI, 
                border_width=2
            )
            
            self.lbl_demo_stats.configure(text=f"Số bước lui: {data['stats']['backtracks']:,}")

        elif action == "prune_start":
            # 2c. Tô viền XANH ĐẬM cho các "hàng xóm" đang bị cắt tỉa
            for (nr, nc) in data["neighbors"]:
                if puzzle_data[nr][nc] == 0: 
                    self.cac_o_nhap[(nr, nc)].configure(border_color=MAU_VIEN_HANG_XOM, border_width=4)
                    
        elif action == "prune_fail":
            # 2d. Tô viền ĐỎ cho ô gây ra lỗi cắt tỉa (miền rỗng)
            self.cac_o_nhap[data["cell"]].configure(border_color=MAU_NEN_QUAY_LUI, border_width=5)

        elif action == "restore_start":
            # 2e. Tô viền XÁM cho các "hàng xóm" đang được khôi phục
            for (nr, nc) in data["neighbors"]:
                 if puzzle_data[nr][nc] == 0:
                    self.cac_o_nhap[(nr, nc)].configure(border_color=MAU_VIEN_KHOI_PHUC, border_width=2)
     
        # 3. Cập nhật thống kê khi Demo kết thúc
        if data.get("status") in ("solved", "failed") and 'stats' in data:
             self.lbl_demo_stats.configure(text=f"Số bước lui: {data['stats']['backtracks']:,}")
     
    def reset_all_cells_visual(self, puzzle_data: list):
        """
        Reset lại toàn bộ màu sắc (nền, chữ, viền) của lưới
        về trạng thái ban đầu (ô gốc hoặc ô trắng).
        """
        if not puzzle_data:
            return
            
        for r in range(9):
            for c in range(9):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                
                if puzzle_data[r][c] != 0:
                    # Reset về màu ô gốc (xám)
                    o_nhap_lieu.configure(
                        border_color=MAU_VIEN_LUOI[0], 
                        border_width=1,
                        fg_color=MAU_O_GOC_FG[0],
                        text_color=MAU_O_GOC_TEXT[0]
                    )
                else:
                    # Reset về màu ô trống (trắng)
                    o_nhap_lieu.configure(
                        border_color=MAU_VIEN_LUOI[0], 
                        border_width=1,
                        fg_color=MAU_O_BINH_THUONG[0],
                        text_color=MAU_O_GIAI_TEXT[0]
                    )