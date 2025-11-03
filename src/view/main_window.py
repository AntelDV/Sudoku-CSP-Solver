# File: src/view/main_window.py
# (CẬP NHẬT: Tái cấu trúc giao diện cho luồng nạp CSV)

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.controller.app_controller import AppController

# --- CẤU HÌNH GIAO DIỆN (cho CTk) ---
KICH_THUOC_LUOI = 9
MAU_O_BINH_THUONG = ("#FFFFFF", "#343638") 
MAU_O_GOC_FG = ("#E5E5E5", "#2B2B2B")       
MAU_O_GOC_TEXT = ("#101010", "#DCE4EE")     
MAU_O_GIAI_TEXT = ("#3B82F6", "#60A5FA")    

class MainView(ctk.CTkFrame):
    """
    Lớp giao diện chính (View) - Bố cục 2 cột.
    """
    def __init__(self, root: ctk.CTk, controller: 'AppController'):
        super().__init__(root, fg_color="transparent")
        self.root = root
        self.controller = controller
        
        self.cac_o_nhap = {} 
        self.algo_var = ctk.StringVar()
        self.lbl_thoi_gian = None
        self.lbl_buoc_lui = None
        self.lbl_trang_thai = None
        self.lbl_puzzle_info = None # Label thông tin đề bài
        
        # --- Biến lưu các nút CSV ---
        self.btn_csv_easy = None
        self.btn_csv_medium = None
        self.btn_csv_hard = None
        self.btn_csv_extreme = None

        vcmd = (self.root.register(self.kiem_tra_nhap_lieu), '%P')
        self.vcmd = vcmd
        
        self.khoi_tao_giao_dien()

    def kiem_tra_nhap_lieu(self, gia_tri_moi):
        if len(gia_tri_moi) > 1: return False
        if gia_tri_moi == "": return True
        return gia_tri_moi.isdigit() and '1' <= gia_tri_moi <= '9'

    def khoi_tao_giao_dien(self):
        self.grid_columnconfigure(0, weight=6) 
        self.grid_columnconfigure(1, weight=4) 
        self.grid_rowconfigure(0, weight=1)
        
        # --- CỘT 0: LƯỚI SUDOKU ---
        khung_luoi = ctk.CTkFrame(self, fg_color="transparent")
        khung_luoi.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        khung_luoi.grid_rowconfigure(0, weight=1)
        khung_luoi.grid_columnconfigure(0, weight=1)
        
        self.tao_luoi_sudoku(khung_luoi)
        
        # --- CỘT 1: BẢNG ĐIỀU KHIỂN ---
        khung_dieu_khien = ctk.CTkFrame(self, fg_color=("#F8F9FA", "#212529"), corner_radius=0)
        khung_dieu_khien.grid(row=0, column=1, sticky="nsew")

        khung_controls_inner = ctk.CTkFrame(khung_dieu_khien, fg_color="transparent", corner_radius=0)
        khung_controls_inner.pack(fill="both", expand=True, padx=30, pady=20)

        # 1. Tiêu đề
        ctk.CTkLabel(
            khung_controls_inner, 
            text="SUDOKU SOLVER", 
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=("blue", "#38bdf8")
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            khung_controls_inner, 
            text="So sánh Backtracking và Forward Checking", 
            font=ctk.CTkFont(size=14),
            text_color="gray"
        ).pack(pady=(0, 20))

        # 2. KHU VỰC NẠP ĐỀ BÀI
        self.tao_khung_nap_de_bai(khung_controls_inner)

        # 3. Khung điều khiển
        self.tao_khung_dieu_khien(khung_controls_inner)
        
        # 4. Khung kết quả
        self.tao_khung_thong_so(khung_controls_inner)
        
        # 5. Thanh trạng thái
        self.lbl_trang_thai = ctk.CTkLabel(
            khung_controls_inner, 
            text="Sẵn sàng", 
            font=ctk.CTkFont(size=12), 
            text_color="gray"
        )
        self.lbl_trang_thai.pack(side="bottom", fill="x", pady=10)

    def tao_khung_nap_de_bai(self, parent):
        """Tái cấu trúc khu vực nạp dữ liệu."""
        
        ctk.CTkLabel(
            parent,
            text="BƯỚC 1: NẠP DỮ LIỆU",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray20", "gray80")
        ).pack(fill="x", pady=(10, 5))
        
        khung_nut_load = ctk.CTkFrame(parent, fg_color="transparent")
        khung_nut_load.pack(fill="x")
        
        # Nút nạp CSV
        btn_load_csv = ctk.CTkButton(
            khung_nut_load,
            text="📁 Tải File CSV (Kaggle)",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#0D6EFD", hover_color="#0A58CA",
            height=40,
            command=self.controller.handle_load_kaggle_csv 
        )
        btn_load_csv.pack(fill="x", pady=5)
        
        # Nút nạp TXT (ít dùng hơn)
        btn_load_txt = ctk.CTkButton(
            khung_nut_load,
            text="Tải File .txt (Tùy chỉnh)",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#565B5E", hover_color="#6C757D",
            height=30,
            command=self.controller.handle_load_txt_file
        )
        btn_load_txt.pack(fill="x", pady=(0, 10))
        
        ctk.CTkFrame(parent, height=2, fg_color="gray").pack(fill="x", padx=0, pady=10)
        
        # --- KHU VỰC MỚI: LẤY ĐỀ TỪ CSV ---
        ctk.CTkLabel(
            parent,
            text="BƯỚC 2: LẤY ĐỀ BÀI TỪ CSV",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray20", "gray80")
        ).pack(fill="x", pady=(0, 5))
        
        # Label thông tin đề bài
        self.lbl_puzzle_info = ctk.CTkLabel(
            parent,
            text="Chưa nạp đề bài nào",
            font=ctk.CTkFont(size=13, slant="italic"),
            text_color="gray"
        )
        self.lbl_puzzle_info.pack(fill="x", pady=5)
        
        # Khung cho các nút độ khó
        khung_kho = ctk.CTkFrame(parent, fg_color="transparent")
        khung_kho.pack(fill="x")
        khung_kho.grid_columnconfigure((0, 1), weight=1)
        
        self.btn_csv_easy = ctk.CTkButton(
            khung_kho, text="Lấy Đề Dễ", state="disabled",
            fg_color="#198754", hover_color="#157347",
            command=lambda: self.controller.handle_get_csv_puzzle('easy')
        )
        self.btn_csv_easy.grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=2)
        
        self.btn_csv_medium = ctk.CTkButton(
            khung_kho, text="Lấy Đề Trung Bình", state="disabled",
            fg_color="#FFC107", hover_color="#D39E00", text_color="#333",
            command=lambda: self.controller.handle_get_csv_puzzle('medium')
        )
        self.btn_csv_medium.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=2)
        
        self.btn_csv_hard = ctk.CTkButton(
            khung_kho, text="Lấy Đề Khó", state="disabled",
            fg_color="#DC3545", hover_color="#BB2D3B",
            command=lambda: self.controller.handle_get_csv_puzzle('hard')
        )
        self.btn_csv_hard.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=2)
        
        self.btn_csv_extreme = ctk.CTkButton(
            khung_kho, text="Lấy Đề Siêu Khó", state="disabled",
            fg_color="#6F42C1", hover_color="#59369A",
            command=lambda: self.controller.handle_get_csv_puzzle('extreme')
        )
        self.btn_csv_extreme.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=2)

        ctk.CTkFrame(parent, height=2, fg_color="gray").pack(fill="x", padx=0, pady=20)


    def tao_luoi_sudoku(self, parent):
        khung_container = ctk.CTkFrame(parent, fg_color="#334155", corner_radius=8)
        khung_container.grid(row=0, column=0, sticky="ew") 
        
        self.cac_o_nhap = {}
        for hang in range(KICH_THUOC_LUOI):
            for cot in range(KICH_THUOC_LUOI):
                o_nhap_lieu = ctk.CTkEntry(
                    khung_container, 
                    width=60, 
                    height=60,
                    font=ctk.CTkFont(size=24, weight="bold"), 
                    justify="center",
                    corner_radius=4,
                    border_width=1,
                    fg_color=MAU_O_BINH_THUONG,
                    text_color=MAU_O_GIAI_TEXT,
                    border_color = ("gray80", "gray40"),
                    validate="key", 
                    validatecommand=self.vcmd,
                )
                
                padx_ngoai = (5, 0) if cot % 3 == 0 else (1, 0)
                pady_ngoai = (5, 0) if hang % 3 == 0 else (1, 0)
                if cot == 8: padx_ngoai = (padx_ngoai[0], 5)
                if hang == 8: pady_ngoai = (pady_ngoai[0], 5)
                
                o_nhap_lieu.grid(
                    row=hang, column=cot, 
                    padx=padx_ngoai, 
                    pady=pady_ngoai, 
                    sticky="nsew"
                )
                self.cac_o_nhap[(hang, cot)] = o_nhap_lieu

    def tao_khung_dieu_khien(self, parent):
        ctk.CTkLabel(
            parent, 
            text="BƯỚC 3: CẤU HÌNH GIẢI", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray20", "gray80")
        ).pack(fill="x")
        
        combo_algo = ctk.CTkComboBox(
            parent,
            variable=self.algo_var,
            font=ctk.CTkFont(size=13),
            values=['Backtracking (Baseline)', 'Forward Checking (Cải tiến)'],
            state="readonly",
            height=35
        )
        combo_algo.set('Backtracking (Baseline)') 
        combo_algo.pack(fill="x", pady=(5, 15))
        
        btn_solve = ctk.CTkButton(
            parent,
            text="⚡ BẮT ĐẦU GIẢI ⚡",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#198754", hover_color="#157347",
            height=50,
            command=self.controller.handle_solve 
        )
        btn_solve.pack(fill="x", pady=(5, 10))
        
        btn_clear = ctk.CTkButton(
            parent,
            text="XÓA TRẮNG LƯỚI",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#DC3545", hover_color="#BB2D3B",
            height=35,
            command=self.controller.handle_clear 
        )
        btn_clear.pack(fill="x", pady=0)
        
        ctk.CTkFrame(parent, height=2, fg_color="gray").pack(fill="x", padx=0, pady=20)


    def tao_khung_thong_so(self, parent):
        # (Phần thông số này nằm ở đây, đúng như bạn thấy)
        ctk.CTkLabel(
            parent, 
            text="KẾT QUẢ THỰC NGHIỆM:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray20", "gray80")
        ).pack()
        
        khung_ket_qua = ctk.CTkFrame(parent, fg_color="transparent")
        khung_ket_qua.pack(fill="x", pady=10)
        
        khung_ket_qua.columnconfigure(0, weight=1)
        khung_ket_qua.columnconfigure(1, weight=1)
        
        khung_tg = ctk.CTkFrame(khung_ket_qua, fg_color=("#F8F9FA", "#343638"), corner_radius=8)
        khung_tg.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        ctk.CTkLabel(
            khung_tg, text="Thời gian thực thi", 
            font=ctk.CTkFont(size=13), text_color="gray"
        ).pack(pady=(10, 0))
        self.lbl_thoi_gian = ctk.CTkLabel(
            khung_tg, text="0.0000 giây", 
            font=ctk.CTkFont(size=18, weight="bold"), text_color="#F59E0B"
        )
        self.lbl_thoi_gian.pack(pady=(0, 10), padx=10)
        
        khung_bl = ctk.CTkFrame(khung_ket_qua, fg_color=("#F8F9FA", "#343638"), corner_radius=8)
        khung_bl.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        ctk.CTkLabel(
            khung_bl, text="Số bước quay lui", 
            font=ctk.CTkFont(size=13), text_color="gray"
        ).pack(pady=(10, 0))
        self.lbl_buoc_lui = ctk.CTkLabel(
            khung_bl, text="0", 
            font=ctk.CTkFont(size=18, weight="bold"), text_color="#F59E0B"
        )
        self.lbl_buoc_lui.pack(pady=(0, 10), padx=10)

    # --- CÁC HÀM ĐƯỢC GỌI BỞI CONTROLLER ---
    
    def enable_csv_load_buttons(self):
        """Kích hoạt các nút lấy đề sau khi nạp CSV thành công."""
        self.btn_csv_easy.configure(state="normal")
        self.btn_csv_medium.configure(state="normal")
        self.btn_csv_hard.configure(state="normal")
        self.btn_csv_extreme.configure(state="normal")
        
    def update_puzzle_info(self, text: str):
        """Cập nhật label thông tin đề bài."""
        self.lbl_puzzle_info.configure(text=text)

    def get_selected_algorithm(self):
        selected = self.algo_var.get()
        if "Forward Checking" in selected:
            return "forward_checking"
        return "backtracking"

    def load_puzzle_to_grid(self, grid_data):
        self.clear_grid_and_stats()
        for r in range(KICH_THUOC_LUOI):
            for c in range(KICH_THUOC_LUOI):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                val = grid_data[r][c]
                
                if val != 0:
                    o_nhap_lieu.insert(0, str(val))
                    o_nhap_lieu.configure(state='disabled', 
                                         fg_color=MAU_O_GOC_FG,
                                         text_color=MAU_O_GOC_TEXT)
                else:
                    o_nhap_lieu.configure(state='normal', 
                                         fg_color=MAU_O_BINH_THUONG,
                                         text_color=MAU_O_GIAI_TEXT)

    def update_grid_with_solution(self, solution_data, puzzle_data):
        for r in range(KICH_THUOC_LUOI):
            for c in range(KICH_THUOC_LUOI):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                val_goc = puzzle_data[r][c]
                val_giai = solution_data[r][c]
                
                o_nhap_lieu.delete(0, "end")
                o_nhap_lieu.insert(0, str(val_giai))
                
                if val_goc != 0:
                    o_nhap_lieu.configure(state='disabled',
                                         fg_color=MAU_O_GOC_FG,
                                         text_color=MAU_O_GOC_TEXT)
                else:
                    o_nhap_lieu.configure(state='normal',
                                         fg_color=MAU_O_BINH_THUONG,
                                         text_color=MAU_O_GIAI_TEXT)
                o_nhap_lieu.configure(state='disabled')

    def clear_grid_and_stats(self):
        for r in range(KICH_THUOC_LUOI):
            for c in range(KICH_THUOC_LUOI):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                o_nhap_lieu.configure(state='normal', 
                                     fg_color=MAU_O_BINH_THUONG,
                                     text_color=MAU_O_GIAI_TEXT)
                o_nhap_lieu.delete(0, "end")
        
        self.lbl_thoi_gian.configure(text="0.0000 giây")
        self.lbl_buoc_lui.configure(text="0")
        self.update_puzzle_info("Chưa nạp đề bài nào") # Reset thông tin

    def set_status(self, text, style):
        color = "gray"
        if style == "green": color = "#198754"
        elif style == "red": color = "#DC3545"
        elif style == "blue": color = "#0D6EFD"
        self.lbl_trang_thai.configure(text=text, text_color=color)

    def get_grid_data(self):
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
        
    def update_stats(self, stats_dict):
        thoi_gian = stats_dict.get("execution_time_sec", 0)
        buoc_lui = stats_dict.get("backtracks", 0)
        self.lbl_thoi_gian.configure(text=f"{thoi_gian:.6f} giây")
        self.lbl_buoc_lui.configure(text=f"{buoc_lui:,}") 

    def show_message(self, title, message, is_error=False):
        if is_error:
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)