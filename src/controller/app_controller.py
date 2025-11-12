from tkinter import filedialog
import traceback
import pandas as pd
import random
import os
import copy
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from src.view.main_window import MainView
    from src.view.analysis_popup import AnalysisPopup

class AppController:
    def __init__(self, model, analysis_popup_class: Type['AnalysisPopup']):
        self.model_classes = model  
        self.view: 'MainView' = None
        self.analysis_popup_class = analysis_popup_class 
        self.analysis_popup_window = None 
        
        self.kaggle_df: pd.DataFrame = None 
        
        self.visualizer_generator = None 
        self.is_visualizer_running = False
        self.current_puzzle_data = None 
        self.current_known_solution = None 

    def set_view(self, view: 'MainView'):
        self.view = view
    
    def handle_load_file(self):
        """
        Mở hộp thoại, cho phép chọn .csv hoặc .txt
        Tự động xử lý tùy theo loại file.
        """
        if not self.view: return
        filepath = filedialog.askopenfilename(
            title="Chọn file CSV hoặc TXT",
            filetypes=[
                ("Data Files", "*.csv *.txt"),
                ("CSV files", "*.csv"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if not filepath: return

        try:
            filename = os.path.basename(filepath)
            
            if filepath.endswith(".csv"):
                self.view.set_status("Đang nạp file CSV, vui lòng chờ...", "blue")
                self.view.root.update_idletasks()
                
                df = pd.read_csv(filepath)
                
                if 'quizzes' not in df.columns or 'solutions' not in df.columns:
                    raise ValueError("File .csv thiếu cột 'quizzes' hoặc 'solutions'.")
                
                if 'clues' not in df.columns:
                    self.view.set_status("Đang đếm số gợi ý...", "blue")
                    df['clues'] = df['quizzes'].astype(str).apply(
                        lambda x: sum(c != '0' for c in x)
                    )
                
                self.kaggle_df = df
                puzzle_count = len(self.kaggle_df)
                
                self.view.set_status(f"Đã nạp {puzzle_count:,} đề. Hãy 'Lấy Đề'.", "green")
                self.view.update_puzzle_info(f"Đã nạp: {filename}")
                self.view.enable_csv_buttons() 
                
            elif filepath.endswith(".txt"):
                self.view.set_status("Đang nạp file .txt...", "blue")
                grid_data = self._load_from_txt(filepath)
                
                self.current_known_solution = None 
                
                self.view.clear_grid_and_stats()
                self.view.load_puzzle_to_grid(grid_data)
                self.view.update_puzzle_info(f"Đã nạp: {filename}")
                self.view.set_status(f"Nạp file {filename} thành công.", "green")

            else:
                raise ValueError("Định dạng file không được hỗ trợ.")

        except Exception as e:
            self.kaggle_df = None
            self.view.disable_csv_buttons()
            self.view.show_message("Lỗi Nạp File", f"Không thể đọc file:\n{e}", is_error=True)
            self.view.set_status("Nạp file thất bại", "red")
            
    def handle_get_csv_puzzle(self, difficulty: str):
        """Lấy một đề bài ngẫu nhiên, với logic fallback."""
        if self.kaggle_df is None:
            self.view.show_message("Lỗi", "Vui lòng 'NẠP DỮ LIỆU' trước.", is_error=True)
            return
            
        try:
            puzzle_col = 'quizzes' 
            solution_col = 'solutions'
            df_filtered = None
            original_difficulty = difficulty
            
            if difficulty == 'extreme':
                df_filtered = self.kaggle_df[self.kaggle_df['clues'] < 25]
                if df_filtered.empty:
                    self.view.set_status("Không có đề 'Siêu Khó', đang tìm 'Khó'...", "orange")
                    difficulty = 'hard' 
            
            if difficulty == 'hard':
                df_filtered = self.kaggle_df[(self.kaggle_df['clues'] >= 25) & (self.kaggle_df['clues'] <= 29)]
                if df_filtered.empty:
                    self.view.set_status("Không có đề 'Khó', đang tìm 'Trung Bình'...", "orange")
                    difficulty = 'medium' 
            
            if difficulty == 'medium':
                df_filtered = self.kaggle_df[(self.kaggle_df['clues'] >= 30) & (self.kaggle_df['clues'] <= 35)]
                if df_filtered.empty:
                    self.view.set_status("Không có đề 'Trung Bình', đang tìm 'Dễ'...", "orange")
                    difficulty = 'easy' 
            
            if difficulty == 'easy':
                df_filtered = self.kaggle_df[self.kaggle_df['clues'] > 35]

            if df_filtered is None or df_filtered.empty:
                self.view.show_message("Lỗi Lọc", f"Không tìm thấy bất kỳ đề nào. Lấy ngẫu nhiên.", is_error=True)
                df_filtered = self.kaggle_df 
            
            random_row = df_filtered.sample(n=1).iloc[0]
            puzzle_string = str(random_row[puzzle_col])
            clues_count = random_row.get('clues', 'N/A') 
            
            solution_string = str(random_row[solution_col])
            self.current_known_solution = self._string_to_grid(solution_string)
            
            grid_data = self._string_to_grid(puzzle_string)
            self.view.clear_grid_and_stats()
            self.view.load_puzzle_to_grid(grid_data)
            
            found_difficulty = difficulty.upper()
            if original_difficulty != difficulty:
                info_text = f"Không có '{original_difficulty.upper()}', đã lấy '{found_difficulty}' (Gợi ý: {clues_count})"
            else:
                info_text = f"Đã nạp: {found_difficulty} (Gợi ý: {clues_count})"
                
            self.view.update_puzzle_info(info_text)
            self.view.set_status("Đã nạp đề bài mới từ CSV.", "black")
            
        except Exception as e:
            self.view.show_message("Lỗi Lấy Đề", f"Không thể lấy đề từ CSV:\n{e}", is_error=True)

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
        if self.is_visualizer_running:
            self.is_visualizer_running = False
            self.view.set_status("Đã dừng demo", "red")
            return
        try:
            self.current_puzzle_data = self.view.get_grid_data()
        except ValueError as e:
            self.view.show_message("Lỗi Đầu Vào", f"Lỗi: {e}", is_error=True)
            return
        
        (algo_key, is_demo_mode) = self.view.get_selected_algorithm()
        
        if is_demo_mode:
            self.run_visualizer(self.current_puzzle_data, algo_key)
        else:
            self.run_fast_solve(self.current_puzzle_data, algo_key)

    def run_fast_solve(self, grid_data, algo_key: str):
        self.view.set_status(f"Đang giải nhanh ({algo_key})...", "blue")
        self.view.root.update_idletasks()
        board_wrapper, stats, is_solved = self._run_single_algo(
            grid_data, 'algorithms', algo_key
        )
        if is_solved:
            solution = board_wrapper.get_board()
            self.view.update_grid_with_solution(solution, grid_data)
            if self.current_known_solution:
                if solution == self.current_known_solution:
                    self.view.set_status(f"Giải xong! Đã xác minh 100%!", "green")
                else:
                    self.view.set_status(f"LỖI XÁC MINH! Lời giải không khớp CSV!", "orange")
            else:
                self.view.set_status(f"Giải xong! (Không có dữ liệu xác minh)", "green")
        else:
            self.view.show_message("Thất Bại", "Không tìm thấy lời giải.", is_error=True)
            self.view.set_status(f"Giải thất bại ({algo_key})", "red")
            
    def handle_compare(self):
        if self.is_visualizer_running:
            self.view.show_message("Lỗi", "Đang chạy Demo, không thể so sánh.", is_error=True)
            return
        if self.analysis_popup_window and self.analysis_popup_window.winfo_exists():
            self.analysis_popup_window.focus() 
            return
        try:
            grid_data = self.view.get_grid_data()
            self.current_puzzle_data = grid_data 
        except ValueError as e:
            self.view.show_message("Lỗi Đầu Vào", f"Lỗi: {e}", is_error=True)
            return
        self.view.set_status("Đang phân tích (profiling)...", "blue")
        self.view.root.update_idletasks()
        try:
            bt_board, bt_stats, bt_solved = self._run_single_algo(
                grid_data, 'profiler_bt', 'bt'
            )
            fc_board, fc_stats, fc_solved = self._run_single_algo(
                grid_data, 'profiler_fc', 'fc'
            )
            if bt_solved:
                bt_solution = bt_board.get_board()
                if self.current_known_solution:
                    if bt_solution == self.current_known_solution:
                        self.view.set_status("Phân tích xong. Đã xác minh 100%!", "green")
                    else:
                        self.view.set_status("LỖI XÁC MINH! Lời giải không khớp CSV!", "orange")
                else:
                     self.view.set_status("Phân tích xong. (Không có dữ liệu xác minh)", "green")
                self.analysis_popup_window = self.analysis_popup_class(
                    self.view, bt_stats, fc_stats
                )
            else:
                self.view.show_message("Thất Bại", "Không tìm thấy lời giải.", is_error=True)
                self.view.set_status("Phân tích thất bại", "red")
        except Exception as e:
            self.view.show_message("Lỗi Thực Thi", f"Lỗi nghiêm trọng: {traceback.format_exc()}", is_error=True)
            self.view.set_status("Lỗi", "red")

    def _run_single_algo(self, grid_data, module_key: str, algo_key: str):
        SudokuBoard_class = self.model_classes['SudokuBoard']
        
        if 'profiler' in module_key:
            module = self.model_classes[module_key]
        elif 'visualizer' in module_key:
            module = self.model_classes[module_key]
        else: # 'algorithms'
            module = self.model_classes['algorithms']

        solve_func = None
        if 'algorithms' in module_key:
            solve_func = module.solve_backtracking if algo_key == 'bt' else module.solve_forward_checking
        elif 'profiler' in module_key:
            solve_func = module.solve_backtracking_profile if algo_key == 'bt' else module.solve_forward_checking_profile
        elif 'visualizer' in module_key:
             solve_func = module.solve_backtracking_visual if algo_key == 'bt' else module.solve_forward_checking_visual
        
        board_wrapper = SudokuBoard_class(copy.deepcopy(grid_data))
        stats = {"backtracks": 0} 
        board_wrapper.start_timer()
        is_solved_or_generator = solve_func(board_wrapper, stats)
        board_wrapper.stop_timer()
        final_stats = board_wrapper.get_stats()
        final_stats.update(stats)
        return (board_wrapper, final_stats, is_solved_or_generator)

    def handle_clear(self):
        if self.is_visualizer_running:
            self.is_visualizer_running = False 
        if self.analysis_popup_window and self.analysis_popup_window.winfo_exists():
            self.analysis_popup_window.destroy() 
        if self.view:
            self.view.clear_grid_and_stats()
        self.current_known_solution = None 
        self.current_puzzle_data = None

    def run_visualizer(self, grid_data, algo_name: str):
        self.view.clear_grid_and_stats() 
        self.view.load_puzzle_to_grid(grid_data) 
        
        algo_key = 'fc' if 'fc' in algo_name else 'bt' 
        
        _board, _stats, generator = self._run_single_algo(
            grid_data, algo_name, algo_key
        )
        self.visualizer_generator = generator
        self.is_visualizer_running = True
        self.view.set_status(f"Bắt đầu Demo: {algo_name}...", "blue")
        self.step_visualizer()

    def step_visualizer(self):
        if not self.is_visualizer_running:
            self.visualizer_generator = None
            return
        try:
            data = next(self.visualizer_generator)
            self.view.cap_nhat_o_visual(data, self.current_puzzle_data)
            status = data.get("status")
            if status == "solved":
                self.is_visualizer_running = False
                if self.current_known_solution:
                    # Lấy bảng cuối cùng từ frame của generator
                    final_board_wrapper = None
                    try:
                        final_board_wrapper = self.visualizer_generator.gi_frame.f_locals.get('board_wrapper')
                    except Exception:
                        pass 
                        
                    if final_board_wrapper and final_board_wrapper.get_board() == self.current_known_solution:
                         self.view.set_status("Demo xong! Đã xác minh 100%!", "green")
                    else:
                         self.view.set_status("Demo xong! LỖI XÁC MINH!", "orange")
                else:
                    self.view.set_status("Demo hoàn tất: Đã tìm thấy lời giải!", "green")
                self.visualizer_generator = None
                return
            elif status == "failed":
                self.is_visualizer_running = False
                self.view.set_status(f"Thất bại: {data.get('message')}", "red")
                self.visualizer_generator = None
                return
            delay_ms = self.view.get_demo_speed()
            self.view.root.after(delay_ms, self.step_visualizer)
        except StopIteration:
            self.is_visualizer_running = False
            self.view.set_status("Hoàn tất: Không tìm thấy lời giải!", "red")
            self.visualizer_generator = None
        except Exception as e:
            self.is_visualizer_running = False
            self.view.show_message("Lỗi", f"Lỗi nghiêm trọng: {traceback.format_exc()}", is_error=True)
            self.view.set_status("Lỗi", "red")
            self.visualizer_generator = None