
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import math
from typing import TYPE_CHECKING
from src.utils.sudoku_converter import SudokuConverter

if TYPE_CHECKING:
    from src.controller.app_controller import AppController

# --- CẤU HÌNH MÀU SẮC ---
MAU_O_BINH_THUONG = ("#FFFFFF", "#FFFFFF") 
MAU_O_GOC_FG = ("#D0D0D0", "#D0D0D0")      
MAU_O_GOC_TEXT = ("#000000", "#000000") 
MAU_O_GIAI_TEXT = ("#000000", "#000000") 
MAU_VIEN_LUOI = ("#000000", "#000000") 
MAU_O_LOI = "#E74C3C" 

MAU_GOI_Y = "#FFC107"
MAU_CHU_GOI_Y = "#000000"

# Màu Demo
MAU_NEN_THU = "#28a745"       
MAU_CHU_THU = "#FFFFFF"       
MAU_NEN_QUAY_LUI = "#E74C3C" 
MAU_CHU_QUAY_LUI = "#FFFFFF"  
MAU_VIEN_HANG_XOM = "#0052cc" 
MAU_VIEN_KHOI_PHUC = "#6a7075" 

class MainView(ctk.CTkFrame):
 
    def __init__(self, root: ctk.CTk, controller: 'AppController'):
        super().__init__(root, fg_color="#0d1b2a") 
        self.root = root
        self.controller = controller
        
        # Dữ liệu lưới
        self.cac_o_nhap = {} 
        self.current_n = 9 
        
        # Biến trạng thái
        self.algo_var = ctk.StringVar() 
        self.mode_var = ctk.StringVar(value="🤖 Máy Giải") 
        
        # Widgets
        self.lbl_puzzle_info = None
        self.switch_demo_mode = None
        self.slider_demo_speed = None
        self.lbl_demo_stats = None 
        self.combo_mode = None 
        self.combo_size = None
        self.combo_fast_solve = None 
        self.frame_numpad = None 
        self.sep_1 = None
        self.sep_2 = None

        # Buttons
        self.btn_load_file = None
        self.btn_csv_easy = None
        self.btn_csv_medium = None
        self.btn_csv_hard = None
        self.btn_csv_extreme = None
        
        self.btn_giai = None
        self.btn_sosanh = None
        self.btn_xoa = None
        
        #  Nút Gợi ý
        self.btn_hint = None
        self.btn_check = None 
        
        self.khung_ket_qua_nhanh = None
        self.lbl_fast_solve_time = None
        self.lbl_fast_solve_backtracks = None
        
        self.vcmd = (self.root.register(self.kiem_tra_nhap_lieu), '%P')
        
        self.khoi_tao_giao_dien()

    def kiem_tra_nhap_lieu(self, gia_tri_moi):
        return SudokuConverter.is_valid_input(gia_tri_moi)

    def khoi_tao_giao_dien(self):
        self.grid_columnconfigure(0, weight=1, minsize=800) 
        self.grid_columnconfigure(1, minsize=350)
        self.grid_rowconfigure(0, weight=1)
        
        # Khung Lưới
        self.khung_luoi_container = ctk.CTkFrame(self, fg_color="transparent")
        self.khung_luoi_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.rebuild_grid(9)
        
        # Khung Điều khiển
        khung_dieu_khien = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        khung_dieu_khien.grid(row=0, column=1, sticky="nsew")

        khung_controls_inner = ctk.CTkFrame(khung_dieu_khien, fg_color="transparent", corner_radius=0)
        khung_controls_inner.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.tao_khung_dieu_khien(khung_controls_inner)

    def rebuild_grid(self, n):
        self.current_n = n
        for widget in self.khung_luoi_container.winfo_children():
            widget.destroy()
            
        max_width = 800 
        max_height = 800
        cell_size = min(max_width // n, max_height // n)
        if cell_size < 22: cell_size = 22 
        
        if n >= 25:   font_size = int(cell_size * 0.45) 
        elif n >= 16: font_size = int(cell_size * 0.5)
        else:         font_size = int(cell_size * 0.6)
            
        box_size = int(math.isqrt(n))
        self.cac_o_nhap = {}
        
        khung_center = ctk.CTkFrame(self.khung_luoi_container, fg_color="transparent")
        khung_center.pack(expand=True)
        
        block_pad = 1 if n > 16 else 2
        cell_pad = 0 if n >= 16 else 1 
        
        for box_r in range(box_size):
            for box_c in range(box_size):
                frame_box = ctk.CTkFrame(khung_center, fg_color="black", corner_radius=0, border_width=0)
                frame_box.grid(row=box_r, column=box_c, padx=block_pad, pady=block_pad)
                
                for cell_r in range(box_size):
                    for cell_c in range(box_size):
                        global_r = box_r * box_size + cell_r
                        global_c = box_c * box_size + cell_c
                        
                        entry = ctk.CTkEntry(
                            frame_box, width=cell_size, height=cell_size,
                            font=ctk.CTkFont(size=font_size, weight="bold"),
                            justify="center", corner_radius=0, border_width=0 if n>=25 else 1,
                            fg_color="white", text_color="black",
                            validate="key", validatecommand=self.vcmd
                        )
                        entry.grid(row=cell_r, column=cell_c, padx=cell_pad, pady=cell_pad)
                        self.cac_o_nhap[(global_r, global_c)] = entry
                        
                        entry.bind("<KeyRelease>", lambda e, r=global_r, c=global_c: self.controller.handle_grid_modified(e, r, c))
                        entry.bind("<FocusIn>", lambda e, r=global_r, c=global_c: self.controller.handle_cell_focus(r, c))

        self.rebuild_numpad(n)

    def tao_khung_dieu_khien(self, parent):
        # Tiêu đề
        khung_tieu_de = ctk.CTkFrame(parent, fg_color="transparent")
        khung_tieu_de.pack(fill="x", pady=(5, 5))
        ctk.CTkLabel(
            khung_tieu_de, text="SUDOKU SOLVER", 
            font=ctk.CTkFont(size=36, weight="bold"), text_color="#38bdf8"
        ).pack(expand=True)
        
        #  Chọn Size
        khung_size = ctk.CTkFrame(parent, fg_color="transparent")
        khung_size.pack(fill="x", pady=2)
        ctk.CTkLabel(khung_size, text="Kích thước:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        self.combo_size = ctk.CTkComboBox(
            khung_size, values=["4x4 (Mini)", "9x9 (Chuẩn)", "16x16 (Lớn)", "25x25 (Khủng)"],
            state="readonly", width=150, command=self.on_size_change
        )
        self.combo_size.set("9x9 (Chuẩn)")
        self.combo_size.pack(side="right", padx=5, fill="x", expand=True)

        #  Nạp đề
        self.tao_khung_nap_de(parent)
        self.sep_1 = ctk.CTkFrame(parent, height=2, fg_color="#334155")
        self.sep_1.pack(fill="x", padx=0, pady=5)

        # Chọn chế độ
        self.tao_khung_che_do(parent) 
        
        #  Hành động
        self.tao_khung_hanh_dong(parent)
        self.sep_2 = ctk.CTkFrame(parent, height=2, fg_color="#334155")
        self.sep_2.pack(fill="x", padx=0, pady=5)

        #  Demo Tools & Numpad
        self.tao_khung_che_do_demo(parent)
        self.frame_numpad = ctk.CTkFrame(parent, fg_color="transparent")
        self.rebuild_numpad(self.current_n)
        
        self.set_controller_references()
        self.toggle_demo_widgets()
        self.set_buttons_state_on_load()

    def rebuild_numpad(self, n):
        if self.frame_numpad is None: return 
        for widget in self.frame_numpad.winfo_children(): widget.destroy()

        label = ctk.CTkLabel(self.frame_numpad, text=f"Bàn phím nhập ({n} giá trị):", font=ctk.CTkFont(size=13, weight="bold"))
        label.pack(pady=(0, 5))
        grid_frame = ctk.CTkFrame(self.frame_numpad, fg_color="transparent")
        grid_frame.pack()
        
        cols = int(math.isqrt(n))
        for val in range(1, n + 1):
            row = (val - 1) // cols
            col = (val - 1) % cols
            display_text = SudokuConverter.int_to_char(val)
            btn = ctk.CTkButton(
                grid_frame, text=display_text, width=45, height=35,
                font=ctk.CTkFont(size=14, weight="bold"),
                command=lambda v=val: self.controller.handle_numpad_click(v)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            
        btn_clear = ctk.CTkButton(
            self.frame_numpad, text="⌫ Xóa Ô", width=120, height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#6c757d", hover_color="#5a6268",
            command=lambda: self.controller.handle_numpad_click(0) 
        )
        btn_clear.pack(pady=(10, 0))

    def on_size_change(self, choice):
        self.controller.handle_size_change(choice)

    def tao_khung_nap_de(self, parent):
        khung_nap = ctk.CTkFrame(parent, fg_color="transparent")
        khung_nap.pack(fill="x", pady=2)
        self.btn_load_file = ctk.CTkButton(khung_nap, text="📁 NẠP DỮ LIỆU", font=ctk.CTkFont(weight="bold"), fg_color="#0D6EFD", hover_color="#0A58CA", height=32)
        self.btn_load_file.pack(pady=2)
        self.lbl_puzzle_info = ctk.CTkLabel(khung_nap, text="Chưa nạp đề bài nào", font=ctk.CTkFont(size=13, slant="italic"), text_color="#94a3b8", wraplength=300)
        self.lbl_puzzle_info.pack(fill="x", pady=2)
        
        khung_kho = ctk.CTkFrame(khung_nap, fg_color="transparent")
        khung_kho.pack(pady=2)
        khung_kho.grid_columnconfigure((0, 1), weight=1)
        self.btn_csv_easy = ctk.CTkButton(khung_kho, text="Lấy Đề Dễ", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#28a745", hover_color="#32CD32", width=130)
        self.btn_csv_easy.grid(row=0, column=0, padx=2, pady=2)
        self.btn_csv_medium = ctk.CTkButton(khung_kho, text="Lấy Đề TB", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#FFC107", hover_color="#FFD700", text_color="black", width=130)
        self.btn_csv_medium.grid(row=0, column=1, padx=2, pady=2)
        self.btn_csv_hard = ctk.CTkButton(khung_kho, text="Lấy Đề Khó", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#E74C3C", hover_color="#EC7063", width=130)
        self.btn_csv_hard.grid(row=1, column=0, padx=2, pady=2)
        self.btn_csv_extreme = ctk.CTkButton(khung_kho, text="Siêu Khó", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#8E44AD", hover_color="#A569BD", width=130)
        self.btn_csv_extreme.grid(row=1, column=1, padx=2, pady=2)

    def tao_khung_che_do(self, parent):
        khung_mode = ctk.CTkFrame(parent, fg_color="transparent")
        khung_mode.pack(fill="x", pady=5)
        ctk.CTkLabel(khung_mode, text="Chế độ:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=5)
        self.combo_mode = ctk.CTkComboBox(
            khung_mode, variable=self.mode_var, values=["🤖 Máy Giải", "👤 Người Chơi"],
            state="readonly", width=150, command=self.on_mode_change
        )
        self.combo_mode.pack(side="right", padx=5, fill="x", expand=True)

    def on_mode_change(self, choice):
        self.controller.handle_mode_change(choice)
        is_play = (choice == "👤 Người Chơi")
        
        if is_play:
            self.switch_demo_mode.pack_forget() 
            self.slider_demo_speed.pack_forget()
            self.lbl_demo_stats.pack_forget()
            self.khung_ket_qua_nhanh.pack_forget()
            self.btn_giai.grid_remove() 
            self.btn_sosanh.grid_remove()
            self.combo_fast_solve.pack_forget()
            
            self.btn_check.pack(pady=(5, 2))
            self.btn_hint.pack(pady=(2, 5))
            
            self.btn_xoa.configure(text="✕ LÀM LẠI")
            self.btn_check.configure(state="normal")
            self.btn_hint.configure(state="normal")
            
            if self.frame_numpad: self.frame_numpad.pack(fill="x", pady=5)
        else:
            self.switch_demo_mode.pack(pady=5, padx=10, anchor="w")
            if self.switch_demo_mode.get():
                self.slider_demo_speed.pack(pady=(5, 5))
                self.lbl_demo_stats.pack(pady=5)
            
            self.btn_giai.grid()
            self.btn_sosanh.grid()
            self.combo_fast_solve.pack(pady=(5, 5))
            
            # Ẩn nút người chơi
            self.btn_check.pack_forget()
            self.btn_hint.pack_forget()
            
            self.btn_xoa.configure(text="✕ XÓA")
            if self.frame_numpad: self.frame_numpad.pack_forget()
            
            self.set_buttons_state_puzzle_on_grid(self.controller.csv_loaded)

    def tao_khung_hanh_dong(self, parent):
        khung_hanh_dong = ctk.CTkFrame(parent, fg_color="transparent")
        khung_hanh_dong.pack(fill="x", pady=2)
        
        self.algo_var.set('Backtracking (Baseline)') 
        self.combo_fast_solve = ctk.CTkComboBox(
            khung_hanh_dong, variable=self.algo_var, font=ctk.CTkFont(size=13),
            values=['Backtracking (Baseline)', 'Forward Checking (Cải tiến)', 'FC + MRV (Nâng cao)'], 
            state="readonly", height=30, width=220
        )
        self.combo_fast_solve.pack(pady=(5, 5))

        khung_nut_hanh_dong = ctk.CTkFrame(khung_hanh_dong, fg_color="transparent")
        khung_nut_hanh_dong.pack()

        self.btn_giai = ctk.CTkButton(khung_nut_hanh_dong, text="⚡ GIẢI", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#28a745", hover_color="#32CD32", width=105)
        self.btn_giai.grid(row=0, column=0, padx=(0, 3))
        self.btn_sosanh = ctk.CTkButton(khung_nut_hanh_dong, text="📊 SO SÁNH", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#8E44AD", hover_color="#A569BD", width=105)
        self.btn_sosanh.grid(row=0, column=1, padx=3)
        self.btn_xoa = ctk.CTkButton(khung_nut_hanh_dong, text="✕ XÓA", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#E74C3C", hover_color="#EC7063", width=105)
        self.btn_xoa.grid(row=0, column=2, padx=(3, 0))
        
        self.btn_check = ctk.CTkButton(khung_hanh_dong, text="✅ KIỂM TRA", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#17a2b8", hover_color="#138496", width=200, height=35)
        self.btn_check.pack_forget()

        self.btn_hint = ctk.CTkButton(
            khung_hanh_dong, text="💡 GỢI Ý THÔNG MINH", 
            font=ctk.CTkFont(size=14, weight="bold"), 
            fg_color="#F59E0B", hover_color="#D97706", text_color="#000000",
            width=200, height=35
        )
        self.btn_hint.pack_forget()

        self.khung_ket_qua_nhanh = ctk.CTkFrame(khung_hanh_dong, fg_color="transparent")
        self.lbl_fast_solve_time = ctk.CTkLabel(self.khung_ket_qua_nhanh, text="Thời gian: 0.00s", font=ctk.CTkFont(size=13, weight="bold"), text_color="#3498DB")
        self.lbl_fast_solve_time.pack(pady=(5, 2))
        self.lbl_fast_solve_backtracks = ctk.CTkLabel(self.khung_ket_qua_nhanh, text="Số bước lui: 0", font=ctk.CTkFont(size=13, weight="bold"), text_color="#F59E0B")
        self.lbl_fast_solve_backtracks.pack(pady=(2, 5))

    def tao_khung_che_do_demo(self, parent):
        khung_demo = ctk.CTkFrame(parent, fg_color="transparent")
        khung_demo.pack(fill="x", pady=5)
        self.switch_demo_mode = ctk.CTkSwitch(khung_demo, text="Bật Demo Trực Quan Hóa", font=ctk.CTkFont(size=13, weight="bold"), onvalue=True, offvalue=False, text_color="#e2e8f0", command=self.toggle_demo_widgets)
        self.switch_demo_mode.pack(pady=5, padx=10, anchor="w")
        self.slider_demo_speed = ctk.CTkSlider(khung_demo)
        self.slider_demo_speed.set(0.2) 
        self.slider_demo_speed.pack(pady=(5, 5))
        self.lbl_demo_stats = ctk.CTkLabel(khung_demo, text="Số bước lui: 0", font=ctk.CTkFont(size=13, weight="bold"), text_color="#F59E0B")
        self.lbl_demo_stats.pack(pady=5)
        
    def show_fast_solve_stats(self, stats: dict):
        time_val = stats.get('execution_time_sec', 0)
        backtracks_val = stats.get('backtracks', 0)
        self.lbl_fast_solve_time.configure(text=f"Thời gian thực thi: {time_val:.6f} s")
        self.lbl_fast_solve_backtracks.configure(text=f"Số bước quay lui: {backtracks_val:,}")
        self.khung_ket_qua_nhanh.pack(fill="x", pady=(5,0))

    def clear_fast_solve_stats(self):
        self.khung_ket_qua_nhanh.pack_forget()

    def toggle_demo_widgets(self):
        is_on = self.switch_demo_mode.get()
        is_play = (self.mode_var.get() == "👤 Người Chơi")
        
        if is_on and not is_play:
            self.slider_demo_speed.pack(pady=(5, 5))
            self.lbl_demo_stats.pack(pady=5)
            self.btn_giai.configure(text="▶ BẮT ĐẦU DEMO") 
        else:
            self.slider_demo_speed.pack_forget()
            self.lbl_demo_stats.pack_forget()
            self.btn_giai.configure(text="⚡ GIẢI") 
    
    def set_controller_references(self):
        self.btn_load_file.configure(command=self.controller.handle_load_file)
        self.btn_csv_easy.configure(command=lambda: self.controller.handle_get_csv_puzzle('easy'))
        self.btn_csv_medium.configure(command=lambda: self.controller.handle_get_csv_puzzle('medium'))
        self.btn_csv_hard.configure(command=lambda: self.controller.handle_get_csv_puzzle('hard'))
        self.btn_csv_extreme.configure(command=lambda: self.controller.handle_get_csv_puzzle('extreme'))
        self.btn_giai.configure(command=self.controller.handle_solve)
        self.btn_sosanh.configure(command=self.controller.handle_compare)
        self.btn_xoa.configure(command=self.controller.handle_clear)
        self.btn_check.configure(command=self.controller.handle_check_solution)
        self.btn_hint.configure(command=self.controller.handle_hint)

    def get_selected_algorithm(self) -> (str, bool):
        selected = self.algo_var.get()
        is_demo = self.switch_demo_mode.get()
        if "FC + MRV" in selected: algo_key = "fc_mrv"
        elif "Forward Checking" in selected: algo_key = "fc"
        else: algo_key = "bt"
        if is_demo:
            if algo_key == "fc_mrv": return "visualizer_mrv", True 
            elif algo_key == "fc": return "visualizer_fc", True
            else: return "visualizer_bt", True
        return algo_key, False
    
    def get_demo_speed(self):
        val = self.slider_demo_speed.get()
        if val < 0.01: return 500 
        return int(500 * (1.0 - val)**2) 

    def update_puzzle_info(self, text: str):
        self.lbl_puzzle_info.configure(text=text)

    def load_puzzle_to_grid(self, grid_data, is_play_mode=False):
        n = len(grid_data)
        if n != self.current_n: self.rebuild_grid(n)
        self.clear_fast_solve_stats() 
        for r in range(n):
            for c in range(n):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                o_nhap_lieu.configure(state='normal', fg_color=MAU_O_BINH_THUONG[0], text_color=MAU_O_GIAI_TEXT[0], border_width=1, border_color = MAU_VIEN_LUOI[0]) 
                o_nhap_lieu.delete(0, "end")
        for r in range(n):
            for c in range(n):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                val = grid_data[r][c]
                if val != 0:
                    val_display = SudokuConverter.int_to_char(val)
                    o_nhap_lieu.insert(0, str(val_display))
                    o_nhap_lieu.configure(state='disabled', fg_color=MAU_O_GOC_FG[0], text_color=MAU_O_GOC_TEXT[0]) 
                else:
                    o_nhap_lieu.configure(state='normal', fg_color=MAU_O_BINH_THUONG[0], text_color=MAU_O_GIAI_TEXT[0]) 

    def update_grid_with_solution(self, solution_data, puzzle_data):
        n = len(solution_data)
        for r in range(n):
            for c in range(n):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                val_goc = puzzle_data[r][c]
                val_giai = solution_data[r][c]
                o_nhap_lieu.delete(0, "end")
                o_nhap_lieu.insert(0, SudokuConverter.int_to_char(val_giai))
                if val_goc != 0:
                    o_nhap_lieu.configure(state='disabled', fg_color=MAU_O_GOC_FG[0], text_color=MAU_O_GOC_TEXT[0], border_width=1, border_color = MAU_VIEN_LUOI[0]) 
                else:
                    o_nhap_lieu.configure(state='normal', fg_color=MAU_O_BINH_THUONG[0], text_color=MAU_O_GIAI_TEXT[0], border_width=1, border_color = MAU_VIEN_LUOI[0]) 
                o_nhap_lieu.configure(state='disabled')

    def clear_grid_and_stats(self):
        self.clear_fast_solve_stats() 
        for r in range(self.current_n):
            for c in range(self.current_n):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                o_nhap_lieu.configure(state='normal', fg_color=MAU_O_BINH_THUONG[0], text_color=MAU_O_GIAI_TEXT[0], border_width=1, border_color = MAU_VIEN_LUOI[0]) 
                o_nhap_lieu.delete(0, "end")
        self.update_puzzle_info("Chưa nạp đề bài nào")
        if self.lbl_demo_stats: self.lbl_demo_stats.configure(text="Số bước lui: 0")

    def get_grid_data(self):
        grid_data = []
        for r in range(self.current_n):
            row_data = []
            for c in range(self.current_n):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                val_str = o_nhap_lieu.get()
                if val_str == "": 
                    row_data.append(0)
                else:
                    num = SudokuConverter.char_to_int(val_str)
                    if num > 0:
                        row_data.append(num)
                    else:
                        raise ValueError(f"Giá trị không hợp lệ tại ô ({r+1}, {c+1})")
            grid_data.append(row_data)
        return grid_data
    
    def is_grid_empty(self):
        for r in range(self.current_n):
            for c in range(self.current_n):
                if self.cac_o_nhap[(r, c)].get() != "": return False
        return True
        
    def show_message(self, title, message, is_error=False):
        if is_error: messagebox.showerror(title, message)
        else: messagebox.showinfo(title, message)
    
    def mark_error_cell(self, r, c, is_error: bool):
        o_nhap_lieu = self.cac_o_nhap[(r, c)]
        if o_nhap_lieu.cget("state") == "normal":
            if is_error:
                o_nhap_lieu.configure(fg_color="#f8d7da", text_color="#721c24") 
            else:
                o_nhap_lieu.configure(fg_color=MAU_O_BINH_THUONG[0], text_color=MAU_O_GIAI_TEXT[0])

    def highlight_hint_cell(self, r, c):
        o_nhap_lieu = self.cac_o_nhap[(r, c)]
        o_nhap_lieu.configure(fg_color=MAU_GOI_Y, text_color=MAU_CHU_GOI_Y)
        o_nhap_lieu.focus_set()

    def set_cell_validity(self, r, c, is_valid: bool):
        o_nhap_lieu = self.cac_o_nhap[(r, c)]
        if not is_valid:
            o_nhap_lieu.configure(border_color=MAU_O_LOI, border_width=3)
        else:
            if o_nhap_lieu.cget("state") == "normal":
                o_nhap_lieu.configure(border_color=MAU_VIEN_LUOI[0], border_width=1)
            
    def set_buttons_state_on_load(self):
        self.btn_load_file.configure(state="normal")
        self.btn_csv_easy.configure(state="disabled")
        self.btn_csv_medium.configure(state="disabled")
        self.btn_csv_hard.configure(state="disabled")
        self.btn_csv_extreme.configure(state="disabled")
        self.btn_giai.configure(state="disabled")
        self.btn_sosanh.configure(state="disabled")
        self.btn_xoa.configure(state="disabled")
        if self.btn_check: self.btn_check.configure(state="disabled")
        if self.btn_hint: self.btn_hint.configure(state="disabled")

    def set_buttons_state_csv_loaded(self):
        self.btn_load_file.configure(state="normal")
        self.btn_csv_easy.configure(state="normal")
        self.btn_csv_medium.configure(state="normal")
        self.btn_csv_hard.configure(state="normal")
        self.btn_csv_extreme.configure(state="normal")
        self.btn_giai.configure(state="disabled")
        self.btn_sosanh.configure(state="disabled")
        self.btn_xoa.configure(state="disabled")
        if self.btn_check: self.btn_check.configure(state="disabled")
        if self.btn_hint: self.btn_hint.configure(state="disabled")

    def set_buttons_state_puzzle_on_grid(self, csv_loaded: bool):
        self.btn_load_file.configure(state="normal")
        state_csv = "normal" if csv_loaded else "disabled"
        self.btn_csv_easy.configure(state="normal")
        self.btn_csv_medium.configure(state="normal")
        self.btn_csv_hard.configure(state="normal")
        self.btn_csv_extreme.configure(state="normal")
        is_play = (self.mode_var.get() == "👤 Người Chơi")
        if is_play:
            self.btn_giai.grid_remove()
            self.btn_sosanh.grid_remove()
            if self.btn_check: 
                self.btn_check.pack(pady=(5, 2))
                self.btn_check.configure(state="normal")
            if self.btn_hint:
                self.btn_hint.pack(pady=(2, 5))
                self.btn_hint.configure(state="normal")
        else:
            self.btn_giai.grid()
            self.btn_giai.configure(state="normal")
            self.btn_sosanh.grid()
            self.btn_sosanh.configure(state="normal")
            if self.btn_check: self.btn_check.pack_forget()
            if self.btn_hint: self.btn_hint.pack_forget()
        self.btn_xoa.configure(state="normal")

    def set_buttons_state_visualizing(self, is_running: bool, csv_loaded: bool):
        is_demo_mode = self.switch_demo_mode.get()
        if is_running:
            self.btn_load_file.configure(state="disabled")
            self.btn_csv_easy.configure(state="disabled")
            self.btn_csv_medium.configure(state="disabled")
            self.btn_csv_hard.configure(state="disabled")
            self.btn_csv_extreme.configure(state="disabled")
            self.btn_sosanh.configure(state="disabled")
            self.btn_xoa.configure(state="disabled")
            self.switch_demo_mode.configure(state="disabled")
            self.combo_mode.configure(state="disabled")
            self.combo_size.configure(state="disabled")
            if self.btn_check: self.btn_check.configure(state="disabled")
            if self.btn_hint: self.btn_hint.configure(state="disabled")
            for r in range(self.current_n):
                for c in range(self.current_n):
                    self.cac_o_nhap[(r, c)].configure(state="disabled")
            if is_demo_mode:
                self.btn_giai.configure(text="❚❚ DỪNG DEMO", state="normal", fg_color="#E74C3C", hover_color="#EC7063")
            else:
                self.btn_giai.configure(state="disabled")
        else:
            self.btn_load_file.configure(state="normal")
            self.switch_demo_mode.configure(state="normal")
            self.combo_mode.configure(state="normal")
            self.combo_size.configure(state="normal")
            if self.controller.current_puzzle_data and self.controller.last_demo_status != "solved":
                self.load_puzzle_to_grid(self.controller.current_puzzle_data, is_play_mode=(self.mode_var.get() == "👤 Người Chơi"))
            elif not self.controller.current_puzzle_data:
                for r in range(self.current_n):
                    for c in range(self.current_n):
                        self.cac_o_nhap[(r, c)].configure(state="normal")
            self.set_buttons_state_puzzle_on_grid(csv_loaded)
            self.toggle_demo_widgets() 
            self.btn_giai.configure(fg_color="#28a745", hover_color="#32CD32")

    def cap_nhat_o_visual(self, data: dict, puzzle_data: list):
        if not puzzle_data: return
        action = data.get("action")
        self.reset_all_cells_visual(puzzle_data)
        if action == "try":
            r, c = data["cell"]
            num = data["num"]
            o = self.cac_o_nhap[(r, c)]
            o.configure(state="normal")
            o.delete(0, "end")
            o.insert(0, SudokuConverter.int_to_char(num))
            o.configure(state="disabled", fg_color=MAU_NEN_THU, text_color=MAU_CHU_THU, border_width=2)
        elif action == "backtrack":
            r, c = data["cell"]
            o = self.cac_o_nhap[(r, c)]
            o.configure(state="normal")
            o.delete(0, "end")
            o.configure(state="disabled", fg_color=MAU_NEN_QUAY_LUI, text_color=MAU_CHU_QUAY_LUI, border_width=2)
            self.lbl_demo_stats.configure(text=f"Số bước lui: {data['stats']['backtracks']:,}")
        elif action == "prune_start":
            for (nr, nc) in data["neighbors"]:
                if (nr, nc) in self.cac_o_nhap:
                    if puzzle_data[nr][nc] == 0: 
                        self.cac_o_nhap[(nr, nc)].configure(border_color=MAU_VIEN_HANG_XOM, border_width=4)
        elif action == "prune_fail":
            self.cac_o_nhap[data["cell"]].configure(border_color=MAU_NEN_QUAY_LUI, border_width=5)
        elif action == "restore_start":
            for (nr, nc) in data["neighbors"]:
                 if (nr, nc) in self.cac_o_nhap:
                     if puzzle_data[nr][nc] == 0:
                        self.cac_o_nhap[(nr, nc)].configure(border_color=MAU_VIEN_KHOI_PHUC, border_width=2)
        if data.get("status") in ("solved", "failed") and 'stats' in data:
             self.lbl_demo_stats.configure(text=f"Số bước lui: {data['stats']['backtracks']:,}")
     
    def reset_all_cells_visual(self, puzzle_data: list):
        if not puzzle_data: return
        n = len(puzzle_data)
        for r in range(n):
            for c in range(n):
                o = self.cac_o_nhap[(r, c)]
                if puzzle_data[r][c] != 0:
                    o.configure(border_color=MAU_VIEN_LUOI[0], border_width=1, fg_color=MAU_O_GOC_FG[0], text_color=MAU_O_GOC_TEXT[0])
                else:
                    o.configure(border_color=MAU_VIEN_LUOI[0], border_width=1, fg_color=MAU_O_BINH_THUONG[0], text_color=MAU_O_GIAI_TEXT[0])