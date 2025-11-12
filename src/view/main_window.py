import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from src.controller.app_controller import AppController


KICH_THUOC_LUOI = 9
KICH_THUOC_O = 60 

MAU_O_BINH_THUONG = ("#FFFFFF", "#FFFFFF") 
MAU_O_GOC_FG = ("#E5E5E5", "#E5E5E5")       
MAU_O_GOC_TEXT = ("#000000", "#000000") 
MAU_O_GIAI_TEXT = ("#000000", "#000000") 

MAU_VIEN_3x3 = ("#000000", "#000000") 
MAU_VIEN_LUOI = ("#000000", "#000000") 

MAU_VIEN_HIEN_TAI = "#F1C40F" 
MAU_O_THU = "#3498DB"      
MAU_O_QUAY_LUI = "#E74C3C" 
MAU_VIEN_HANG_XOM = "#17A2B8" 


class MainView(ctk.CTkFrame):
    def __init__(self, root: ctk.CTk, controller: 'AppController'):
        super().__init__(root, fg_color="#0d1b2a") 
        self.root = root
        self.controller = controller
        
        self.cac_o_nhap = {} 
        self.algo_var = ctk.StringVar() 
        
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
        
        self.vcmd = (self.root.register(self.kiem_tra_nhap_lieu), '%P')
        
        self.khoi_tao_giao_dien()

    def kiem_tra_nhap_lieu(self, gia_tri_moi):
        if len(gia_tri_moi) > 1: return False
        if gia_tri_moi == "": return True
        return gia_tri_moi.isdigit() and '1' <= gia_tri_moi <= '9'

    def khoi_tao_giao_dien(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)
        
        khung_luoi = ctk.CTkFrame(self, fg_color="transparent")
        khung_luoi.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.tao_khung_luoi_sudoku(khung_luoi)
        
        khung_dieu_khien = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        khung_dieu_khien.grid(row=0, column=1, sticky="nsew")

        khung_controls_inner = ctk.CTkFrame(khung_dieu_khien, fg_color="transparent", corner_radius=0, width=380)
        khung_controls_inner.pack(fill="y", expand=True, padx=20, pady=20)
        
        self.tao_khung_dieu_khien(khung_controls_inner)

    def tao_khung_luoi_sudoku(self, parent):
        khung_container = ctk.CTkFrame(parent, fg_color="transparent")
        khung_container.pack(expand=True)
        
        self.cac_o_nhap = {}
        for khoi_hang in range(3):
            for khoi_cot in range(3):
                khung_3x3 = ctk.CTkFrame(khung_container, fg_color=MAU_VIEN_3x3[0], corner_radius=0)
                khung_3x3.grid(row=khoi_hang, column=khoi_cot, padx=(3,0), pady=(3,0))
                
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
                        self.cac_o_nhap[(hang_toan_cuc, cot_toan_cuc)] = o_nhap_lieu
                        o_nhap_lieu.bind("<KeyRelease>", self.controller.handle_grid_modified)


    
    def tao_khung_dieu_khien(self, parent):    
        ctk.CTkLabel(
            parent, 
            text="SUDOKU SOLVER", 
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#38bdf8"
        ).pack(pady=(10, 5))
        
        
        self.tao_khung_nap_de(parent)
        ctk.CTkFrame(parent, height=2, fg_color="#334155").pack(fill="x", padx=0, pady=10)

        self.tao_khung_hanh_dong(parent)
        ctk.CTkFrame(parent, height=2, fg_color="#334155").pack(fill="x", padx=0, pady=10)

        self.tao_khung_che_do_demo(parent)
        
        self.set_controller_references()
        self.toggle_demo_widgets()
        
        self.set_buttons_state_on_load()


    def tao_khung_nap_de(self, parent):
        khung_nap = ctk.CTkFrame(parent, fg_color="transparent")
        khung_nap.pack(fill="x", pady=5)
        
        self.btn_load_file = ctk.CTkButton(
            khung_nap,
            text="📁 NẠP DỮ LIỆU",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#0D6EFD", hover_color="#0A58CA", 
            height=32 
        )
        
        self.btn_load_file.pack(fill="x", pady=4)
        self.lbl_puzzle_info = ctk.CTkLabel(
            khung_nap,
            text="Chưa nạp đề bài nào",
            font=ctk.CTkFont(size=13, slant="italic"),
            text_color="#94a3b8",
            wraplength=300 
        )
        self.lbl_puzzle_info.pack(fill="x", pady=5)
        

        khung_kho = ctk.CTkFrame(khung_nap, fg_color="transparent")
        khung_kho.pack(fill="x", pady=5)
        khung_kho.grid_columnconfigure((0, 1), weight=1)
        
        self.btn_csv_easy = ctk.CTkButton(
            khung_kho, text="Lấy Đề Dễ",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#28a745", hover_color="#32CD32",
            text_color="#FFFFFF",
            height=28
        )
        self.btn_csv_easy.grid(row=0, column=0, sticky="ew", padx=(0, 3), pady=2)
        
        self.btn_csv_medium = ctk.CTkButton(
            khung_kho, text="Lấy Đề Trung Bình",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#FFC107", hover_color="#FFD700", 
            text_color="#000000",
            height=28
        )
        self.btn_csv_medium.grid(row=0, column=1, sticky="ew", padx=(3, 0), pady=2)
        
        self.btn_csv_hard = ctk.CTkButton(
            khung_kho, text="Lấy Đề Khó",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#E74C3C", hover_color="#EC7063",
            text_color="#FFFFFF",
            height=28
        )
        self.btn_csv_hard.grid(row=1, column=0, sticky="ew", padx=(0, 3), pady=2)
        
        self.btn_csv_extreme = ctk.CTkButton(
            khung_kho, text="Lấy Đề Siêu Khó",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#8E44AD", hover_color="#A569BD",
            text_color="#FFFFFF",
            height=28
        )
        self.btn_csv_extreme.grid(row=1, column=1, sticky="ew", padx=(3, 0), pady=2)
        
    def tao_khung_hanh_dong(self, parent):
        khung_hanh_dong = ctk.CTkFrame(parent, fg_color="transparent")
        khung_hanh_dong.pack(fill="x", pady=5)
        

        self.algo_var.set('Backtracking (Baseline)') 
        combo_fast_solve = ctk.CTkComboBox(
            khung_hanh_dong,
            variable=self.algo_var, 
            font=ctk.CTkFont(size=13),
            values=['Backtracking (Baseline)', 'Forward Checking (Cải tiến)'],
            state="readonly",
            height=30 
        )
        combo_fast_solve.pack(fill="x", pady=(5, 5))

        khung_nut_hanh_dong = ctk.CTkFrame(khung_hanh_dong, fg_color="transparent")
        khung_nut_hanh_dong.pack(fill="x")
        khung_nut_hanh_dong.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_giai = ctk.CTkButton(
            khung_nut_hanh_dong, text="⚡ GIẢI",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#28a745", hover_color="#32CD32", 
            text_color="#FFFFFF", height=35
        )
        self.btn_giai.grid(row=0, column=0, sticky="ew", padx=(0, 3))
        
        self.btn_sosanh = ctk.CTkButton(
            khung_nut_hanh_dong, text="📊 SO SÁNH",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#8E44AD", hover_color="#A569BD", 
            text_color="#FFFFFF", height=35
        )
        self.btn_sosanh.grid(row=0, column=1, sticky="ew", padx=3)

        self.btn_xoa = ctk.CTkButton(
            khung_nut_hanh_dong, text="✕ XÓA",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#E74C3C", hover_color="#EC7063", 
            text_color="#FFFFFF", height=35
        )
        self.btn_xoa.grid(row=0, column=2, sticky="ew", padx=(3, 0))

    def tao_khung_che_do_demo(self, parent):
        
        khung_demo = ctk.CTkFrame(parent, fg_color="transparent")
        khung_demo.pack(fill="x", pady=10)
        khung_demo.grid_columnconfigure(1, weight=1)
        
        
        self.switch_demo_mode = ctk.CTkSwitch(
            khung_demo, text="Bật Demo Trực Quan Hóa", 
            font=ctk.CTkFont(size=13, weight="bold"),
            onvalue=True, offvalue=False, text_color="#e2e8f0",
            command=self.toggle_demo_widgets
        )
        self.switch_demo_mode.grid(row=1, column=0, columnspan=2, sticky="w", padx=10)
        
        self.slider_demo_speed = ctk.CTkSlider(khung_demo)
        self.slider_demo_speed.set(0.8) 
        self.slider_demo_speed.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        
        self.lbl_demo_stats = ctk.CTkLabel(
            khung_demo, text="Số bước lui: 0",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#F59E0B"
        )
        self.lbl_demo_stats.grid(row=3, column=0, columnspan=2, pady=5)
        
    def toggle_demo_widgets(self):
        is_on = self.switch_demo_mode.get()
        if is_on:
            self.slider_demo_speed.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
            self.lbl_demo_stats.grid(row=3, column=0, columnspan=2, pady=5)
            self.btn_giai.configure(text="▶ BẮT ĐẦU DEMO") 
        else:
            self.slider_demo_speed.grid_remove()
            self.lbl_demo_stats.grid_remove()
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

    def get_selected_algorithm(self) -> (str, bool):
        selected = self.algo_var.get()
        is_demo = self.switch_demo_mode.get()
        is_fc = "Forward Checking" in selected
        
        if is_demo:
            return ("visualizer_fc" if is_fc else "visualizer_bt"), True
        else:
            return ("fc" if is_fc else "bt"), False
    
    def get_demo_speed(self):
        val = self.slider_demo_speed.get()
        if val < 0.01: return 500 
        return int(500 * (1.0 - val)**2) 

    def update_puzzle_info(self, text: str):
        self.lbl_puzzle_info.configure(text=text)

    def load_puzzle_to_grid(self, grid_data):
        for r in range(KICH_THUOC_LUOI):
            for c in range(KICH_THUOC_LUOI):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                o_nhap_lieu.configure(state='normal', 
                                     fg_color=MAU_O_BINH_THUONG[0],
                                     text_color=MAU_O_GIAI_TEXT[0], 
                                     border_width=1,
                                     border_color = MAU_VIEN_LUOI[0]) 
                o_nhap_lieu.delete(0, "end")
        
        if self.lbl_demo_stats: 
            self.lbl_demo_stats.configure(text="Số bước lui: 0")
        
        for r in range(KICH_THUOC_LUOI):
            for c in range(KICH_THUOC_LUOI):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                val = grid_data[r][c]
                
                if val != 0:
                    o_nhap_lieu.insert(0, str(val))
                    o_nhap_lieu.configure(state='disabled', 
                                         fg_color=MAU_O_GOC_FG[0],
                                         text_color=MAU_O_GOC_TEXT[0]) 
                else:
                    o_nhap_lieu.configure(state='normal', 
                                         fg_color=MAU_O_BINH_THUONG[0],
                                         text_color=MAU_O_GIAI_TEXT[0]) 

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
                                         fg_color=MAU_O_GOC_FG[0],
                                         text_color=MAU_O_GOC_TEXT[0], 
                                         border_width=1,
                                         border_color = MAU_VIEN_LUOI[0]) 
                else:
                    o_nhap_lieu.configure(state='normal',
                                         fg_color=MAU_O_BINH_THUONG[0],
                                         text_color=MAU_O_GIAI_TEXT[0], 
                                         border_width=1,
                                         border_color = MAU_VIEN_LUOI[0]) 
                o_nhap_lieu.configure(state='disabled')

    def clear_grid_and_stats(self):
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
        if self.lbl_demo_stats: 
            self.lbl_demo_stats.configure(text="Số bước lui: 0")

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
    
    def is_grid_empty(self):
        for r in range(KICH_THUOC_LUOI):
            for c in range(KICH_THUOC_LUOI):
                if self.cac_o_nhap[(r, c)].get() != "":
                    return False
        return True
        
    def show_message(self, title, message, is_error=False):
        if is_error:
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
            
    def set_buttons_state_on_load(self):
        self.btn_csv_easy.configure(state="disabled")
        self.btn_csv_medium.configure(state="disabled")
        self.btn_csv_hard.configure(state="disabled")
        self.btn_csv_extreme.configure(state="disabled")
        self.btn_giai.configure(state="disabled")
        self.btn_sosanh.configure(state="disabled")
        self.btn_xoa.configure(state="disabled")

    def set_buttons_state_csv_loaded(self):
        self.btn_csv_easy.configure(state="normal")
        self.btn_csv_medium.configure(state="normal")
        self.btn_csv_hard.configure(state="normal")
        self.btn_csv_extreme.configure(state="normal")
        self.btn_giai.configure(state="disabled")
        self.btn_sosanh.configure(state="disabled")
        self.btn_xoa.configure(state="disabled")

    def set_buttons_state_puzzle_on_grid(self, csv_loaded: bool):
        if csv_loaded:
            self.btn_csv_easy.configure(state="normal")
            self.btn_csv_medium.configure(state="normal")
            self.btn_csv_hard.configure(state="normal")
            self.btn_csv_extreme.configure(state="normal")
        else:
            self.btn_csv_easy.configure(state="disabled")
            self.btn_csv_medium.configure(state="disabled")
            self.btn_csv_hard.configure(state="disabled")
            self.btn_csv_extreme.configure(state="disabled")
        
        self.btn_giai.configure(state="normal")
        self.btn_sosanh.configure(state="normal")
        self.btn_xoa.configure(state="normal")

    def set_buttons_state_visualizing(self, is_running: bool, csv_loaded: bool):
        if is_running:
            self.btn_load_file.configure(state="disabled")
            self.btn_csv_easy.configure(state="disabled")
            self.btn_csv_medium.configure(state="disabled")
            self.btn_csv_hard.configure(state="disabled")
            self.btn_csv_extreme.configure(state="disabled")
            self.btn_giai.configure(state="disabled")
            self.btn_sosanh.configure(state="disabled")
            self.btn_xoa.configure(state="disabled")
            self.switch_demo_mode.configure(state="disabled")
        else:
            self.btn_load_file.configure(state="normal")
            self.switch_demo_mode.configure(state="normal")
            self.set_buttons_state_puzzle_on_grid(csv_loaded)
            self.toggle_demo_widgets()


    def cap_nhat_o_visual(self, data: dict, puzzle_data: list):
        if not puzzle_data: 
            return
            
        action = data.get("action")
        self.reset_all_borders(puzzle_data)
        
        if action == "try":
            r, c = data["cell"]
            num = data["num"]
            o_nhap_lieu = self.cac_o_nhap[(r, c)]
            o_nhap_lieu.delete(0, "end")
            o_nhap_lieu.insert(0, str(num))
            o_nhap_lieu.configure(border_color=MAU_O_THU, border_width=4)
        
        elif action == "backtrack":
            r, c = data["cell"]
            o_nhap_lieu = self.cac_o_nhap[(r, c)]
            o_nhap_lieu.delete(0, "end")
            o_nhap_lieu.configure(border_color=MAU_O_QUAY_LUI, border_width=4)
            self.lbl_demo_stats.configure(text=f"Số bước lui: {data['stats']['backtracks']:,}")

        elif action == "prune_start":
            for (nr, nc) in data["neighbors"]:
                if puzzle_data[nr][nc] == 0: 
                    self.cac_o_nhap[(nr, nc)].configure(border_color=MAU_VIEN_HANG_XOM, border_width=3)
                    
        elif action == "prune_fail":
            self.cac_o_nhap[data["cell"]].configure(border_color=MAU_O_QUAY_LUI, border_width=4)

        elif action == "restore_start":
            for (nr, nc) in data["neighbors"]:
                 if puzzle_data[nr][nc] == 0:
                    self.cac_o_nhap[(nr, nc)].configure(border_color="gray", border_width=2)
     
    def reset_all_borders(self, puzzle_data: list):
        if not puzzle_data:
            return
        for r in range(9):
            for c in range(9):
                o_nhap_lieu = self.cac_o_nhap[(r, c)]
                o_nhap_lieu.configure(border_color=MAU_VIEN_LUOI[0], border_width=1)