from tkinter import filedialog
import traceback
import pandas as pd
import random
import os
import copy
import threading
import queue
import time
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
        self.csv_loaded = False
        
        self.visualizer_queue: queue.Queue = None
        self.is_visualizer_running = False
        self.last_demo_status = None
        
        self.current_puzzle_data = None 
        self.current_known_solution = None 
        
        self.current_visual_board = None
        
        self.colors = {
            "header": "\033[95m",
            "blue": "\033[94m",
            "cyan": "\033[96m",
            "green": "\033[92m",
            "warning": "\033[93m",
            "fail": "\033[91m",
            "endc": "\033[0m",
            "bold": "\033[1m",
            "underline": "\033[4m"
        }

    def _log(self, message, color="endc"):
        if color in self.colors:
            print(f"{self.colors[color]}{message}{self.colors['endc']}")
        else:
            print(message)

    def set_view(self, view: 'MainView'):
        self.view = view
        self.view.set_buttons_state_on_load()
    
    def handle_load_file(self):
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
                self._log("[HỆ THỐNG] Đang nạp file CSV, vui lòng chờ...", "cyan")
                if self.view: self.view.root.update_idletasks()
                
                df = pd.read_csv(filepath)
                
                if 'quizzes' not in df.columns or 'solutions' not in df.columns:
                    raise ValueError("File .csv thiếu cột 'quizzes' hoặc 'solutions'.")
                
                if 'clues' not in df.columns:
                    self._log("[HỆ THỐNG] Đang đếm số gợi ý...", "cyan")
                    df['clues'] = df['quizzes'].astype(str).apply(
                        lambda x: sum(c != '0' for c in x)
                    )
                
                self.kaggle_df = df
                self.csv_loaded = True
                puzzle_count = len(self.kaggle_df)
                
                self._log(f"[HỆ THỐNG] Đã nạp {puzzle_count:,} đề. Hãy 'Lấy Đề'.", "green")
                if self.view:
                    self.view.update_puzzle_info(f"Đã nạp: {filename}")
                    self.view.set_buttons_state_csv_loaded() 
                
            elif filepath.endswith(".txt"):
                self._log("[HỆ THỐNG] Đang nạp file .txt...", "cyan")
                grid_data = self._load_from_txt(filepath)
                
                self.current_puzzle_data = copy.deepcopy(grid_data)
                self.current_known_solution = None 
                
                if self.view:
                    self.view.clear_grid_and_stats()
                    self.view.load_puzzle_to_grid(grid_data)
                    self.view.update_puzzle_info(f"Đã nạp: {filename}")
                    self.view.set_buttons_state_puzzle_on_grid(self.csv_loaded)
                self._log(f"[HỆ THỐNG] Nạp file {filename} thành công.", "green")

            else:
                raise ValueError("Định dạng file không được hỗ... (trimmed)")

        except Exception as e:
            self.kaggle_df = None
            self.csv_loaded = False
            self.current_puzzle_data = None
            self.current_known_solution = None
            if self.view:
                self.view.set_buttons_state_on_load()
                self.view.show_message("Lỗi Nạp File", f"Không thể đọc file:\n{e}", is_error=True)
            self._log(f"[LỖI] Nạp file thất bại: {e}", "fail")
            
    def handle_get_csv_puzzle(self, difficulty: str):
        if self.kaggle_df is None:
            if self.view: self.view.show_message("Lỗi", "Vui lòng 'NẠP DỮ LIỆU' trước.", is_error=True)
            return
            
        try:
            puzzle_col = 'quizzes' 
            solution_col = 'solutions'
            df_filtered = None
            original_difficulty = difficulty
            
            if difficulty == 'extreme':
                df_filtered = self.kaggle_df[self.kaggle_df['clues'] < 25]
                if df_filtered.empty:
                    self._log("[HỆ THỐNG] Không có đề 'Siêu Khó', đang tìm 'Khó'...", "warning")
                    difficulty = 'hard' 
            
            if difficulty == 'hard':
                df_filtered = self.kaggle_df[(self.kaggle_df['clues'] >= 25) & (self.kaggle_df['clues'] <= 29)]
                if df_filtered.empty:
                    self._log("[HỆ THỐNG] Không có đề 'Khó', đang tìm 'Trung Bình'...", "warning")
                    difficulty = 'medium' 
            
            if difficulty == 'medium':
                df_filtered = self.kaggle_df[(self.kaggle_df['clues'] >= 30) & (self.kaggle_df['clues'] <= 35)]
                if df_filtered.empty:
                    self._log("[HỆ THỐNG] Không có đề 'Trung Bình', đang tìm 'Dễ'...", "warning")
                    difficulty = 'easy' 
            
            if difficulty == 'easy':
                df_filtered = self.kaggle_df[self.kaggle_df['clues'] > 35]

            if df_filtered is None or df_filtered.empty:
                if self.view: self.view.show_message("Lỗi Lọc", f"Không tìm thấy bất kỳ đề nào. Lấy ngẫu nhiên.", is_error=True)
                df_filtered = self.kaggle_df 
            
            random_row = df_filtered.sample(n=1).iloc[0]
            puzzle_string = str(random_row[puzzle_col])
            
            solution_string = str(random_row[solution_col])
            self.current_known_solution = self._string_to_grid(solution_string)
            
            grid_data = self._string_to_grid(puzzle_string)
            self.current_puzzle_data = copy.deepcopy(grid_data)

            if self.view: 
                self.view.load_puzzle_to_grid(grid_data)
                self.view.set_buttons_state_puzzle_on_grid(self.csv_loaded)
            
            found_difficulty = difficulty.upper()
            if original_difficulty != difficulty:
                info_text = f"Không có '{original_difficulty.upper()}', đã lấy '{found_difficulty}'"
            else:
                info_text = f"Đã nạp: {found_difficulty}"
                
            if self.view: self.view.update_puzzle_info(info_text)
            self._log(f"[HỆ THỐNG] Đã nạp đề bài mới: {found_difficulty}", "green")
            
        except Exception as e:
            if self.view: self.view.show_message("Lỗi Lấy Đề", f"Không thể lấy đề từ CSV:\n{e}", is_error=True)

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
        grid_data_to_solve = None
        try:
            if self.current_puzzle_data:
                grid_data_to_solve = self.current_puzzle_data
            else:
                grid_data_to_solve = self.view.get_grid_data()
                self.current_puzzle_data = copy.deepcopy(grid_data_to_solve)
                
        except ValueError as e:
            if self.view: self.view.show_message("Lỗi Đầu Vào", f"Lỗi: {e}", is_error=True)
            return
        
        (algo_key, is_demo_mode) = self.view.get_selected_algorithm()
        
        if is_demo_mode:
            self.run_visualizer(grid_data_to_solve, algo_key)
        else:
            self.run_fast_solve(grid_data_to_solve, algo_key)

    def _grid_to_string(self, grid):
        return "".join(str(cell) for row in grid for cell in row)

    def run_fast_solve(self, grid_data, algo_key: str):
        algo_name = "Forward Checking" if algo_key == 'fc' else "Backtracking"
        self._log(f"[GIẢI] Đang giải nhanh bằng {algo_name}...", "cyan")
        
        if self.view: self.view.set_buttons_state_visualizing(True, self.csv_loaded)
        
        board_wrapper, stats, is_solved = self._run_single_algo(
            grid_data, 'algorithms', algo_key
        )
        
        if self.view: self.view.set_buttons_state_visualizing(False, self.csv_loaded)
        
        if is_solved:
            solution = board_wrapper.get_board()
            if self.view: self.view.update_grid_with_solution(solution, grid_data)
            if self.current_known_solution:
                if solution == self.current_known_solution:
                    self._log(f"[GIẢI] Giải xong! Đã xác minh 100%!", "green")
                else:
                    self._log(f"[GIẢI] LỖI XÁC MINH! Lời giải không khớp CSV!", "fail")
            else:
                self._log(f"[GIẢI] Giải xong! (Không có dữ liệu xác minh)", "green")
        else:
            if self.view: self.view.show_message("Thất Bại", "Không tìm thấy lời giải.", is_error=True)
            self._log(f"[GIẢI] Giải thất bại ({algo_name})", "fail")
            
    def handle_compare(self):
        if self.is_visualizer_running:
            if self.view: self.view.show_message("Lỗi", "Đang chạy Demo, không thể so sánh.", is_error=True)
            return
        if self.analysis_popup_window and self.analysis_popup_window.winfo_exists():
            self.analysis_popup_window.focus() 
            return
            
        grid_data_to_solve = None
        try:
            if self.current_puzzle_data:
                grid_data_to_solve = self.current_puzzle_data
            else:
                grid_data_to_solve = self.view.get_grid_data()
                self.current_puzzle_data = copy.deepcopy(grid_data_to_solve)
                
        except ValueError as e:
            if self.view: self.view.show_message("Lỗi Đầu Vào", f"Lỗi: {e}", is_error=True)
            return
            
        self._log("[PHÂN TÍCH] Đang phân tích hiệu năng...", "cyan")
        if self.view: self.view.root.update_idletasks()
        
        try:
            bt_board, bt_stats, bt_solved = self._run_single_algo(
                grid_data_to_solve, 'profiler_bt', 'bt'
            )
            fc_board, fc_stats, fc_solved = self._run_single_algo(
                grid_data_to_solve, 'profiler_fc', 'fc'
            )
            
            if bt_solved:
                bt_solution = bt_board.get_board()
                if self.current_known_solution:
                    if bt_solution == self.current_known_solution:
                        self._log("[PHÂN TÍCH] Phân tích xong. Đã xác minh 100%!", "green")
                    else:
                        self._log("[PHÂN TÍCH] LỖI XÁC MINH! Lời giải không khớp CSV!", "fail")
                else:
                     self._log("[PHÂN TÍCH] Phân tích xong. (Không có dữ liệu xác minh)", "green")
                
                self.analysis_popup_window = self.analysis_popup_class(
                    self.view, bt_stats, fc_stats
                )
            else:
                if self.view: self.view.show_message("Thất Bại", "Không tìm thấy lời giải.", is_error=True)
                self._log("[PHÂN TÍCH] Phân tích thất bại", "fail")
        except Exception as e:
            if self.view: self.view.show_message("Lỗi Thực Thi", f"Lỗi nghiêm trọng: {traceback.format_exc()}", is_error=True)
            self._log(f"[LỖI] {e}", "fail")

    def _run_single_algo(self, grid_data, module_key: str, algo_key: str):
        SudokuBoard_class = self.model_classes['SudokuBoard']
        
        if 'profiler' in module_key:
            module = self.model_classes[module_key]
        elif 'visualizer' in module_key:
            module = self.model_classes[module_key]
        else:
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
        if self.analysis_popup_window and self.analysis_popup_window.winfo_exists():
            self.analysis_popup_window.destroy() 

        if self.view:
            if self.current_puzzle_data:
                self.view.load_puzzle_to_grid(self.current_puzzle_data)
                self.view.set_buttons_state_puzzle_on_grid(self.csv_loaded)
                self._log("[HỆ THỐNG] Đã khôi phục đề bài gốc.", "green")
            else:
                self.view.clear_grid_and_stats()
                if self.csv_loaded:
                    self.view.set_buttons_state_csv_loaded()
                else:
                    self.view.set_buttons_state_on_load()
                self._log("[HỆ THỐNG] Đã xóa trắng lưới.", "green")

    def handle_grid_modified(self, event=None):
        self.current_puzzle_data = None
        self.current_known_solution = None
        
        is_empty = self.view.is_grid_empty()
        
        if is_empty:
            if self.csv_loaded:
                self.view.set_buttons_state_csv_loaded()
            else:
                self.view.set_buttons_state_on_load()
        else:
             self.view.set_buttons_state_puzzle_on_grid(self.csv_loaded)
        
        self._log("[HỆ THỐNG] Đã phát hiện sửa đổi.", "warning")

    def run_visualizer(self, grid_data, algo_name: str):
        if self.is_visualizer_running:
            return

        if self.view: 
            self.view.load_puzzle_to_grid(grid_data) 
            self.view.set_buttons_state_visualizing(True, self.csv_loaded)
        
        algo_key = 'fc' if 'fc' in algo_name else 'bt' 
        
        board_wrapper, _stats, generator = self._run_single_algo(
            grid_data, algo_name, algo_key
        )
        self.visualizer_queue = queue.Queue()
        self.is_visualizer_running = True
        self.last_demo_status = None 
        
        threading.Thread(
            target=self._run_visualizer_worker, 
            args=(generator, self.visualizer_queue, _stats), 
            daemon=True
        ).start()
        
        if self.view:
            self.view.root.after(50, self._check_visualizer_queue)
        
        algo_full_name = "Forward Checking" if algo_key == 'fc' else "Backtracking"
        self._log(f"[DEMO] Bắt đầu Demo {algo_full_name}...", "cyan")

    def _run_visualizer_worker(self, generator, visualizer_queue, stats):
        try:
            for data in generator:
                visualizer_queue.put(data)
                time.sleep(0.001)
            
            visualizer_queue.put({"status": "finished", "stats": stats})
        except Exception as e:
            visualizer_queue.put({"status": "failed", "message": str(e)})

    def _check_visualizer_queue(self):
        if not self.is_visualizer_running:
            return

        try:
            data = self.visualizer_queue.get_nowait()
            
            if "status" in data:
                status = data["status"]
                if status == "solved":
                    self.last_demo_status = "solved"
                elif status == "failed":
                    self.last_demo_status = "failed"
                    self._log(f"[DEMO] Thất bại: {data.get('message')}", "fail")
                elif status == "finished":
                    self._visualizer_finished()
                    return
            else:
                if self.view and self.current_puzzle_data:
                    self.view.cap_nhat_o_visual(data, self.current_puzzle_data)
            
        except queue.Empty:
            pass
        
        if self.view:
            delay = self.view.get_demo_speed()
            self.view.root.after(delay, self._check_visualizer_queue)

    def _visualizer_finished(self):
        self.is_visualizer_running = False
        
        if self.last_demo_status == "solved":
            if self.current_known_solution:
                if self.current_visual_board and self.current_visual_board.get_board() == self.current_known_solution:
                    self._log("[DEMO] Demo xong! Đã xác minh 100%!", "green")
                else:
                    self._log("[DEMO] Demo xong! LỖI XÁC MINH!", "fail")
            else:
                self._log("[DEMO] Đã tìm thấy lời giải!", "green")
        elif self.last_demo_status == "failed":
            pass
        else:
            self._log("[DEMO] Không tìm thấy lời giải!", "fail")
            
        if self.view:
            self.view.set_buttons_state_visualizing(False, self.csv_loaded)