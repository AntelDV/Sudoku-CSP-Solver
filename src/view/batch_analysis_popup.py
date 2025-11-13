import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import TYPE_CHECKING

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import ScalarFormatter 
import numpy as np

if TYPE_CHECKING:
    from src.controller.app_controller import AppController

class BatchAnalysisPopup(ctk.CTkToplevel):

    def __init__(self, parent_view, controller: 'AppController'):
        """
        Khởi tạo cửa sổ popup Thực nghiệm.
        
        :param parent_view: Cửa sổ View cha (MainView).
        :param controller: Đối tượng AppController.
        """
        super().__init__(parent_view)
        self.controller = controller
        
        self.title("Chạy Thực nghiệm Hàng loạt")
        self.geometry("900x700")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Hàng 0: Thanh điều khiển
        self.grid_rowconfigure(1, weight=1) # Hàng 1: Tabs
        self.grid_rowconfigure(2, weight=0) # Hàng 2: Thanh trạng thái

        # 1. Khung Điều khiển (Nhập N, Nút Bắt đầu, Thanh tiến trình)
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=0, column=0, sticky="new", padx=10, pady=10)
        
        ctk.CTkLabel(self.control_frame, text="Số lượng đề/loại:").pack(side="left", padx=(10, 5))
        
        self.entry_n = ctk.CTkEntry(self.control_frame, width=80, justify="center")
        self.entry_n.insert(0, "50") # Giá trị mặc định
        self.entry_n.pack(side="left", padx=5)
        
        self.btn_start = ctk.CTkButton(self.control_frame, text="Bắt đầu Thực nghiệm", font=ctk.CTkFont(weight="bold"), command=self.start_analysis)
        self.btn_start.pack(side="left", padx=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.control_frame)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="left", padx=10, fill="x", expand=True)

        # 2. Khung Tabs (Bảng kết quả và Biểu đồ)
        self.tab_view = ctk.CTkTabview(self, fg_color=("#F0F0F0", "#2B2B2B"))
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))
        
        self.tab_table = self.tab_view.add("📊 Bảng Kết quả (Log)")
        self.tab_chart = self.tab_view.add("📈 Biểu đồ So sánh")
        
        self.create_results_tab(self.tab_table)
        self.create_chart_tab(self.tab_chart)
        
        # 3. Khung Trạng thái (Hiển thị chi tiết tiến trình)
        self.lbl_loading_detail = ctk.CTkLabel(self, text="Sẵn sàng. Nhập số lượng N và nhấn 'Bắt đầu'.", font=ctk.CTkFont(size=12), text_color="gray")
        self.lbl_loading_detail.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 10))
        
        self.chart_canvas = None # Placeholder cho biểu đồ
        
        self.after(100, self._safe_grab_set)

    def _safe_grab_set(self):
        """Gọi grab_set sau khi cửa sổ đã sẵn sàng."""
        try:
            if self.winfo_exists():
                self.grab_set()
        except tk.TclError:
            pass

    def start_analysis(self):
        """Xử lý sự kiện nhấn nút 'Bắt đầu Thực nghiệm'."""
        try:
            n_value = int(self.entry_n.get())
            if n_value <= 0:
                raise ValueError("Số lượng phải là số dương")
        except ValueError as e:
            messagebox.showerror("Lỗi Đầu vào", f"Giá trị không hợp lệ: {e}", parent=self)
            return

        # Vô hiệu hóa các nút điều khiển
        self.btn_start.configure(state="disabled", text="Đang chạy...")
        self.entry_n.configure(state="disabled")
        self.progress_bar.set(0)
        self.lbl_loading_detail.configure(text="Khởi động...")

        # Gọi Controller để bắt đầu chạy (Controller sẽ chạy trong Thread)
        self.controller.handle_run_batch_analysis(n_value, self)

    def update_progress(self, text: str, percentage: float):
        """
        Cập nhật thanh tiến trình và nhãn trạng thái.
        :param text: Văn bản hiển thị trạng thái (ví dụ: "Đang xử lý: Dễ...").
        :param percentage: Giá trị tiến trình (từ 0.0 đến 1.0).
        """
        self.lbl_loading_detail.configure(text=text)
        self.progress_bar.set(percentage)
        self.update() 

    def on_analysis_complete(self, results_data: dict):
        """
        Hiển thị kết quả lên Bảng và Biểu đồ.        
        :param results_data: Dictionary chứa kết quả tổng hợp.
        """
        if not results_data:
             self.lbl_loading_detail.configure(text="Thất bại! Không tìm thấy dữ liệu nào.")
        else:
            # Cập nhật cả hai tab với dữ liệu mới
            self.update_results_tab(results_data)
            self.update_chart_tab(results_data)
            
            total_puzzles = sum(d.get('N', 0) for d in results_data.values())
            self.lbl_loading_detail.configure(text=f"Hoàn thành! Đã phân tích {total_puzzles} đề.")
            self.progress_bar.set(1)

        # Kích hoạt lại các nút điều khiển
        self.btn_start.configure(state="normal", text="Bắt đầu Thực nghiệm")
        self.entry_n.configure(state="normal")

    def create_results_tab(self, tab):
        """Khởi tạo nội dung cho tab 'Bảng Kết quả'."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        self.results_textbox = ctk.CTkTextbox(
            tab, 
            font=("Courier New", 15, "bold"), 
            wrap="none",
            fg_color="#1D1D1D", 
            text_color="#E0E0E0"
        )
        self.results_textbox.grid(row=0, column=0, sticky="nsew")
        self.results_textbox.insert("0.0", "Nhấn 'Bắt đầu Thực nghiệm' để chạy phân tích.")
        self.results_textbox.configure(state="disabled")

    def update_results_tab(self, data):
        """
        Cập nhật tab 'Bảng Kết quả' với dữ liệu được định dạng.
        
        :param data: Dictionary kết quả từ Controller.
        """
        self.results_textbox.configure(state="normal")
        self.results_textbox.delete("0.0", "end")
        
        header = (
            f"{'Loại':<22} | {'Thuật toán':<18} | {'Thời gian (s)':<13} | "
            f"{'Bước lui':<15} | {'Nút duyệt':<15} | {'Cắt tỉa':<12}\n"
        )
        separator = "-" * 100 + "\n"
        
        text_output = "--- BÁO CÁO KẾT QUẢ THỰC NGHIỆM ---\n\n"
        text_output += header
        text_output += separator

        # Định dạng và chèn dữ liệu cho từng độ khó
        for difficulty, stats in data.items():
            diff_label = f"--- {difficulty.upper()} (N={stats['N']}) ---"
            text_output += f"{diff_label:<100}\n"
            
            bt_line = (
                f"{'':<22} | {'Backtracking':<18} | {stats['bt_time']:<13.6f} | "
                f"{stats['bt_backtracks']:<15,.0f} | {stats['bt_nodes']:<15,.0f} | {'N/A':<12}\n"
            )
            fc_line = (
                f"{'':<22} | {'Forward Checking':<18} | {stats['fc_time']:<13.6f} | "
                f"{stats['fc_backtracks']:<15,.0f} | {stats['fc_nodes']:<15,.0f} | {stats['fc_prunes']:<12,.0f}\n"
            )
            
            text_output += bt_line
            text_output += fc_line
            text_output += "\n"

        self.results_textbox.insert("0.0", text_output)
        self.results_textbox.configure(state="disabled")


    def create_chart_tab(self, tab):
        """Khởi tạo nội dung cho tab 'Biểu đồ So sánh'."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        self.chart_frame = ctk.CTkFrame(tab, fg_color="white") 
        self.chart_frame.grid(row=0, column=0, sticky="nsew")
        
    def update_chart_tab(self, data):
        """
        Vẽ biểu đồ Matplotlib với dữ liệu mới.
        
        :param data: Dictionary kết quả từ Controller.
        """
        
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()

        bg_color = "#FFFFFF" 
        text_color = "#000000" 
        grid_color = "#CCCCCC" 
        
        labels = list(data.keys())
        bt_times = [stats['bt_time'] for stats in data.values()]
        fc_times = [stats['fc_time'] for stats in data.values()]
        
        bt_backtracks = [stats['bt_backtracks'] for stats in data.values()]
        fc_backtracks = [stats['fc_backtracks'] for stats in data.values()]

        fig = Figure(figsize=(8, 5.5), dpi=100)
        fig.patch.set_facecolor(bg_color) 
        
        # --- Biểu đồ 1: Thời gian ---
        ax1 = fig.add_subplot(2, 1, 1)
        ax1.set_facecolor(bg_color) 
        x = np.arange(len(labels))
        width = 0.35
        rects1 = ax1.bar(x - width/2, bt_times, width, label='Backtracking', color='#E74C3C')
        rects2 = ax1.bar(x + width/2, fc_times, width, label='Forward Checking', color='#3498DB')
        ax1.set_ylabel('Thời gian TB (s)', color=text_color)
        ax1.set_title('So sánh Thời gian Thực thi (Trung bình)', color=text_color)
        ax1.set_xticks(x, labels)
        ax1.legend()
        ax1.set_yscale('log') 
        
        ax1.yaxis.set_major_formatter(ScalarFormatter()) 
        ax1.yaxis.set_minor_formatter(ScalarFormatter())
        ax1.set_yticks([]) 

        ax1.bar_label(rects1, padding=3, fmt='%.4f', fontsize=9)
        ax1.bar_label(rects2, padding=3, fmt='%.4f', fontsize=9)

        ax1.tick_params(axis='x', colors=text_color)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['bottom'].set_color(grid_color)
        ax1.spines['left'].set_color(grid_color)
        ax1.grid(axis='y', linestyle='--', alpha=0.7, color=grid_color)

        # --- Biểu đồ 2: Số bước lui ---
        ax2 = fig.add_subplot(2, 1, 2)
        ax2.set_facecolor(bg_color)
        rects3 = ax2.bar(x - width/2, bt_backtracks, width, label='Backtracking', color='#E74C3C')
        rects4 = ax2.bar(x + width/2, fc_backtracks, width, label='Forward Checking', color='#3498DB')
        ax2.set_ylabel('Số bước lui TB (log scale)', color=text_color)
        ax2.set_title('So sánh Số bước Quay lui (Trung bình)', color=text_color)
        ax2.set_xticks(x, labels)
        ax2.legend()
        ax2.set_yscale('log') 
        
        ax2.yaxis.set_major_formatter(ScalarFormatter())
        ax2.set_yticks([]) 
        
        ax2.bar_label(rects3, padding=3, fmt='%d', fontsize=9)
        ax2.bar_label(rects4, padding=3, fmt='%d', fontsize=9)
        
        ax2.tick_params(axis='x', colors=text_color)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_color(grid_color)
        ax2.spines['left'].set_color(grid_color)
        ax2.grid(axis='y', linestyle='--', alpha=0.7, color=grid_color)

        fig.tight_layout(pad=3.0)

        # Vẽ biểu đồ 
        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)