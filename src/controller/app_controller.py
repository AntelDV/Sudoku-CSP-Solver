# File: src/controller/app_controller.py
# (CẬP NHẬT: Tái cấu trúc luồng nạp dữ liệu)

from tkinter import filedialog
import traceback
import pandas as pd
import random
import os
from typing import TYPE_CHECKING

# Hack để có type hinting cho View mà không bị circular import
if TYPE_CHECKING:
    from src.view.main_window import MainView

class AppController:
    """
    Bộ điều khiển, chịu trách nhiệm liên lạc giữa View và Model.
    """
    def __init__(self, model):
        self.model_classes = model
        self.view: 'MainView' = None
        self.kaggle_df: pd.DataFrame = None # Biến để lưu 1 triệu đề bài

    def set_view(self, view: 'MainView'):
        self.view = view

    # --- HÀM MỚI: NẠP BỘ DỮ LIỆU KAGGLE ---
    def handle_load_kaggle_csv(self):
        """
        Nạp toàn bộ file CSV Kaggle vào bộ nhớ (self.kaggle_df).
        """
        if not self.view:
            return
            
        filepath = filedialog.askopenfilename(
            title="Chọn file CSV (Kaggle)",
            filetypes=[("CSV files", "*.csv")]
        )
        if not filepath:
            return

        try:
            self.view.set_status("Đang nạp file CSV, vui lòng chờ...", "blue")
            self.view.root.update_idletasks()
            
            self.kaggle_df = pd.read_csv(filepath)
            
            # Kiểm tra các cột quan trọng
            if 'puzzle' not in self.kaggle_df.columns and 'quizzes' not in self.kaggle_df.columns:
                raise ValueError("File .csv thiếu cột 'puzzle' hoặc 'quizzes'.")
            if 'clues' not in self.kaggle_df.columns:
                print("Cảnh báo: File CSV thiếu cột 'clues'. Sẽ lọc ngẫu nhiên.")
            
            puzzle_count = len(self.kaggle_df)
            self.view.set_status(f"Đã nạp thành công {puzzle_count:,} đề bài.", "green")
            self.view.enable_csv_load_buttons() # Kích hoạt các nút Dễ/Khó
            
        except Exception as e:
            self.kaggle_df = None
            self.view.show_message("Lỗi Nạp CSV", f"Không thể đọc file:\n{e}", is_error=True)
            self.view.set_status("Nạp file CSV thất bại", "red")
            
    # --- HÀM MỚI: LẤY ĐỀ BÀI TỪ CSV ĐÃ NẠP ---
    def handle_get_csv_puzzle(self, difficulty: str):
        """
        Lấy một đề bài ngẫu nhiên từ DataFrame đã nạp, dựa trên độ khó.
        """
        if self.kaggle_df is None:
            self.view.show_message("Lỗi", "Vui lòng 'Tải File CSV (Kaggle)' trước.", is_error=True)
            return

        try:
            puzzle_col = 'puzzle' if 'puzzle' in self.kaggle_df.columns else 'quizzes'
            
            # 1. Lọc theo độ khó (dựa trên số gợi ý)
            df_filtered = None
            if 'clues' in self.kaggle_df.columns:
                if difficulty == 'easy':
                    # Dễ: > 35 gợi ý
                    df_filtered = self.kaggle_df[self.kaggle_df['clues'] > 35]
                elif difficulty == 'medium':
                    # Trung bình: 30-35 gợi ý
                    df_filtered = self.kaggle_df[(self.kaggle_df['clues'] >= 30) & (self.kaggle_df['clues'] <= 35)]
                elif difficulty == 'hard':
                    # Khó: 25-29 gợi ý
                    df_filtered = self.kaggle_df[(self.kaggle_df['clues'] >= 25) & (self.kaggle_df['clues'] <= 29)]
                elif difficulty == 'extreme':
                    # Siêu khó: < 25 gợi ý (nổi tiếng là 17)
                    df_filtered = self.kaggle_df[self.kaggle_df['clues'] < 25]
            
            # Nếu không lọc được (ví dụ không có cột 'clues'), lấy ngẫu nhiên
            if df_filtered is None or df_filtered.empty:
                print(f"Không lọc được độ khó '{difficulty}', lấy ngẫu nhiên.")
                df_filtered = self.kaggle_df

            # 2. Chọn 1 đề ngẫu nhiên
            random_row = df_filtered.sample(n=1).iloc[0]
            puzzle_string = str(random_row[puzzle_col])
            clues_count = random_row.get('clues', 'N/A') # Lấy số gợi ý
            
            # 3. Nạp lên giao diện
            grid_data = self._string_to_grid(puzzle_string)
            self.view.clear_grid_and_stats()
            self.view.load_puzzle_to_grid(grid_data)
            self.view.update_puzzle_info(f"Độ khó: {difficulty.upper()} (Gợi ý: {clues_count})")
            self.view.set_status("Đã nạp đề bài mới từ CSV.", "black")

        except Exception as e:
            self.view.show_message("Lỗi Lấy Đề", f"Không thể lấy đề từ CSV:\n{e}", is_error=True)

    # --- HÀM NÀY GIỜ CHỈ DÙNG CHO .txt ---
    def handle_load_txt_file(self):
        """
        Mở hộp thoại chọn file .txt (chỉ .txt) và nạp lên lưới.
        """
        if not self.view:
            return

        filepath = filedialog.askopenfilename(
            title="Chọn file Sudoku (.txt)",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not filepath:
            return

        try:
            grid_data = None
            filename = os.path.basename(filepath)
            
            if filepath.endswith(".txt"):
                grid_data = self._load_from_txt(filepath)
            else:
                raise ValueError("Định dạng file không được hỗ trợ. Vui lòng chọn .txt.")

            self.view.clear_grid_and_stats()
            self.view.load_puzzle_to_grid(grid_data)
            self.view.update_puzzle_info(f"Nạp từ file: {filename} (Độ khó: Tự nhập)")
            self.view.set_status(f"Đã nạp từ file: {filename}", "black")

        except Exception as e:
            self.view.show_message("Lỗi Đọc File", f"Không thể đọc file:\n{e}", is_error=True)
            self.view.set_status("Nạp file thất bại", "red")

    # --- CÁC HÀM CÒN LẠI GIỮ NGUYÊN ---

    def _string_to_grid(self, s: str):
        grid = []
        s = str(s).replace('.', '0')
        for i in range(9):
            row_str = s[i*9 : (i+1)*9]
            grid.append([int(char) for char in row_str])
        return grid

    def _load_from_txt(self, filepath):
        grid_data = []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                cleaned_line = line.replace('.', '0').replace('-', '0').replace('_', '0')
                row_digits = [int(char) for char in cleaned_line if char.isdigit()][:9]
                if len(row_digits) < 9: row_digits.extend([0] * (9 - len(row_digits)))
                if row_digits: grid_data.append(row_digits)
                if len(grid_data) == 9: break 
        if len(grid_data) != 9:
            raise ValueError(f"File .txt không chứa đủ 9 hàng dữ liệu.")
        return grid_data

    def handle_solve(self):
        # ... (Giữ nguyên logic hàm solve) ...
        if not self.view: return
        try:
            grid_data = self.view.get_grid_data()
            algo_name = self.view.get_selected_algorithm()
        except ValueError as e:
            self.view.show_message("Lỗi Đầu Vào", f"Lỗi: {e}", is_error=True)
            return
        SudokuBoard_class = self.model_classes['SudokuBoard']
        algorithms_module = self.model_classes['algorithms']
        import copy
        board_to_solve = copy.deepcopy(grid_data)
        board = SudokuBoard_class(board_to_solve)
        stats = {"backtracks": 0}
        if algo_name == "backtracking":
            solve_func = algorithms_module.solve_backtracking
        elif algo_name == "forward_checking":
            solve_func = algorithms_module.solve_forward_checking
        else:
            self.view.show_message("Lỗi", "Thuật toán không xác định.", is_error=True)
            return
        self.view.set_status("Đang giải, vui lòng chờ...", "blue")
        self.view.root.update_idletasks()
        board.start_timer()
        try:
            is_solved = solve_func(board, stats)
        except Exception as e:
            self.view.show_message("Lỗi Thuật Toán", f"Lỗi nghiêm trọng: {traceback.format_exc()}", is_error=True)
            self.view.set_status("Sẵn sàng", "black")
            return
        board.stop_timer()
        if is_solved:
            solution = board.get_board()
            final_stats = board.get_stats()
            final_stats.update(stats)
            original_puzzle = self.view.get_grid_data()
            self.view.update_grid_with_solution(solution, original_puzzle)
            self.view.update_stats(final_stats)
            self.view.set_status("Đã giải xong!", "green")
        else:
            self.view.update_stats({"execution_time_sec": 0, "backtracks": 0})
            self.view.set_status("Không tìm thấy lời giải!", "red")
            self.view.show_message("Thất Bại", "Không tìm thấy lời giải cho đề bài này.", is_error=True)

    def handle_clear(self):
        if self.view:
            self.view.clear_grid_and_stats()
            self.view.set_status("Sẵn sàng", "black")