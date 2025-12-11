from tkinter import filedialog, messagebox
import traceback
import pandas as pd
import random
import os
import copy
from typing import TYPE_CHECKING, Type
import threading
import time
import math

from src.model.sudoku_generator import SudokuGenerator
from src.utils.sudoku_converter import SudokuConverter
from src.model.hint_generator import HintGenerator 
from src.model import solver_dlx 

if TYPE_CHECKING:
    from src.view.main_window import MainView
    from src.view.analysis_popup import AnalysisPopup

class AppController:

    def __init__(self, model, analysis_popup_class: Type['AnalysisPopup'], batch_analysis_popup_class: Type['object'], base_dir: str):
        self.model_classes = model  
        self.view: 'MainView' = None
        self.base_dir = base_dir
        self.data_dir = os.path.join(self.base_dir, "data")
        
        self.analysis_popup_class = analysis_popup_class
        self.analysis_popup_window = None 
        
        self.kaggle_df: pd.DataFrame = None 
        self.csv_loaded = False
        
        self.visualizer_generator = None 
        self.is_visualizer_running = False
        self.last_demo_status = None 
        
        self.current_puzzle_data = None      
        self.current_known_solution = None   
        self.current_visual_board = None    

        self.is_play_mode = False 
        self.focused_cell = None 
        self.current_size = 9 

        self.colors = {
            "header": "\033[95m", "blue": "\033[94m", "cyan": "\033[96m",
            "green": "\033[92m", "warning": "\033[93m", "fail": "\033[91m",
            "endc": "\033[0m", "bold": "\033[1m", "underline": "\033[4m"
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
        if self.is_visualizer_running:
            self.view.show_message("Lỗi", "Đang chạy Demo, không thể nạp file.", is_error=True)
            return

        initial_dir = self.base_dir
        if os.path.isdir(self.data_dir):
            initial_dir = self.data_dir

        filepath = filedialog.askopenfilename(
            title="Chọn file CSV hoặc TXT",
            initialdir=initial_dir,
            filetypes=[("Data Files", "*.csv *.txt"), ("All files", "*.*")]
        )
        if not filepath: return

        try:
            filename = os.path.basename(filepath)
            if filepath.endswith(".csv"):
                self._log("[HỆ THỐNG] Đang nạp file CSV...", "cyan")
                if self.view: self.view.root.update_idletasks()
                
                df = pd.read_csv(filepath)
                if 'quizzes' not in df.columns or 'solutions' not in df.columns:
                    raise ValueError("File thiếu cột 'quizzes' hoặc 'solutions'.")
                
                if 'clues' not in df.columns:
                    self._log("[HỆ THỐNG] Đang đếm số gợi ý...", "cyan")
                    df['clues'] = df['quizzes'].astype(str).apply(lambda x: sum(c != '0' for c in x))
                
                self.kaggle_df = df
                self.csv_loaded = True
                
                self._log(f"[HỆ THỐNG] Đã nạp {len(self.kaggle_df):,} đề.", "green")
                if self.view:
                    self.view.update_puzzle_info(f"Đã nạp: {filename}")
                    self.view.set_buttons_state_csv_loaded() 
                    self.view.clear_fast_solve_stats() 
            
            elif filepath.endswith(".txt"):
                self._log("[HỆ THỐNG] Đang nạp file .txt...", "cyan")
                grid_data = self._load_from_txt(filepath)
                size = len(grid_data)
                self.current_size = size
                if self.view: self.view.rebuild_grid(size) 
                
                self.current_puzzle_data = copy.deepcopy(grid_data)
                self.current_known_solution = None 
                
                if self.view:
                    self.view.clear_grid_and_stats()
                    self.view.load_puzzle_to_grid(grid_data, is_play_mode=self.is_play_mode)
                    self.view.update_puzzle_info(f"Đã nạp: {filename} ({size}x{size})")
                    self.view.set_buttons_state_puzzle_on_grid(self.csv_loaded)
                self._log(f"[HỆ THỐNG] Nạp file {filename} thành công.", "green")

        except Exception as e:
            self.kaggle_df = None
            self.csv_loaded = False
            self.current_puzzle_data = None
            if self.view:
                self.view.set_buttons_state_on_load()
                self.view.show_message("Lỗi Nạp File", f"Không thể đọc file:\n{e}", is_error=True)
            self._log(f"[LỖI] Nạp file thất bại: {e}", "fail")
            
    def handle_size_change(self, size_str: str):
        try:
            new_size = int(size_str.split('x')[0])
            self.current_size = new_size
            self.current_puzzle_data = None
            self.current_known_solution = None
            
            if self.view:
                self.view.rebuild_grid(new_size)
                self.view.clear_grid_and_stats()
                self.view.update_puzzle_info(f"Đã chọn kích thước: {new_size}x{new_size}")
                self.view.set_buttons_state_puzzle_on_grid(self.csv_loaded)
            self._log(f"[HỆ THỐNG] Đổi kích thước sang {new_size}x{new_size}", "blue")
        except Exception as e:
            print(f"Lỗi đổi size: {e}")

    def handle_get_csv_puzzle(self, difficulty: str):
        if self.current_size == 9 and self.kaggle_df is not None:
            try:
                df_filtered = None
                if difficulty == 'extreme':
                    df_filtered = self.kaggle_df[self.kaggle_df['clues'] < 25]
                    if df_filtered.empty: difficulty = 'hard'
                if difficulty == 'hard':
                    df_filtered = self.kaggle_df[(self.kaggle_df['clues'] >= 25) & (self.kaggle_df['clues'] <= 29)]
                    if df_filtered.empty: difficulty = 'medium'
                if difficulty == 'medium':
                    df_filtered = self.kaggle_df[(self.kaggle_df['clues'] >= 30) & (self.kaggle_df['clues'] <= 35)]
                    if df_filtered.empty: difficulty = 'easy'
                if difficulty == 'easy':
                    df_filtered = self.kaggle_df[self.kaggle_df['clues'] > 35]

                if df_filtered is None or df_filtered.empty:
                    df_filtered = self.kaggle_df 
                
                random_row = df_filtered.sample(n=1).iloc[0]
                self.current_known_solution = self._string_to_grid(str(random_row['solutions']), 9)
                grid_data = self._string_to_grid(str(random_row['quizzes']), 9)
                self.current_puzzle_data = copy.deepcopy(grid_data)

                if self.view: 
                    self.view.load_puzzle_to_grid(grid_data, is_play_mode=self.is_play_mode)
                    self.view.set_buttons_state_puzzle_on_grid(self.csv_loaded)
                    self.view.update_puzzle_info(f"Đã nạp: {difficulty.upper()} (CSV)")
                
                self._log(f"[HỆ THỐNG] Đã nạp đề CSV: {difficulty.upper()}", "green")
                return
            except Exception as e:
                self.view.show_message("Lỗi Lấy Đề", f"Lỗi CSV: {e}", is_error=True)
                return
        else:
            self._log(f"[GENERATOR] Đang sinh đề {self.current_size}x{self.current_size} độ khó {difficulty}...", "cyan")
            if self.view: self.view.root.update_idletasks()
            try:
                gen = SudokuGenerator(size=self.current_size)
                puzzle, solution = gen.generate_puzzle(difficulty)
                
                self.current_puzzle_data = puzzle
                self.current_known_solution = solution
                
                if self.view:
                    self.view.load_puzzle_to_grid(puzzle, is_play_mode=self.is_play_mode)
                    self.view.set_buttons_state_puzzle_on_grid(True) 
                    self.view.update_puzzle_info(f"Đã sinh: {difficulty.upper()} (Gen)")
                
                self._log(f"[GENERATOR] Sinh đề thành công.", "green")
            except Exception as e:
                self.view.show_message("Lỗi Sinh Đề", f"Không thể sinh đề: {e}", is_error=True)

    def handle_mode_change(self, mode_str: str):
        self.is_play_mode = (mode_str == "👤 Người Chơi")
        self.focused_cell = None
        if self.current_puzzle_data and self.view:
            self.view.load_puzzle_to_grid(self.current_puzzle_data, is_play_mode=self.is_play_mode)
            self.view.update_puzzle_info(self.view.lbl_puzzle_info.cget("text") + " (Reset)")

    def handle_cell_focus(self, r, c):
        if self.is_play_mode:
            self.focused_cell = (r, c)

    def handle_numpad_click(self, num):
        if not self.is_play_mode or not self.focused_cell: return
        r, c = self.focused_cell
        if (r, c) not in self.view.cac_o_nhap: return
        entry = self.view.cac_o_nhap[(r, c)]
        
        if entry.cget("state") == "normal":
            entry.delete(0, "end")
            if num != 0: 
                entry.insert(0, SudokuConverter.int_to_char(num))
            self.handle_grid_modified(None, r, c)

    def handle_grid_modified(self, event, r, c):
        if self.is_play_mode:
            try:
                entry_widget = self.view.cac_o_nhap[(r, c)]
                val_str = entry_widget.get()
                if val_str == "": 
                    self.view.set_cell_validity(r, c, True)
                    return
                num = SudokuConverter.char_to_int(val_str)
                if num == 0:
                    entry_widget.delete(0, "end")
                    return

                grid_data = self.view.get_grid_data()
                SudokuBoard_class = self.model_classes['SudokuBoard']
                board = SudokuBoard_class(grid_data)
                
                board.set_cell(r, c, 0)
                is_ok = board.is_valid(num, r, c)
                
                if not is_ok:
                    self.view.set_cell_validity(r, c, False)
                    display_char = SudokuConverter.int_to_char(num)
                    self.view.show_message("Sai Luật!", f"Giá trị {display_char} không hợp lệ tại ô ({r+1}, {c+1})!", is_error=True)
                else:
                    self.view.set_cell_validity(r, c, True)
            except Exception:
                pass
            return

        self.current_puzzle_data = None
        self.current_known_solution = None
        if self.view: self.view.clear_fast_solve_stats()
        is_empty = self.view.is_grid_empty()
        if is_empty:
            if self.csv_loaded: self.view.set_buttons_state_csv_loaded()
            else: self.view.set_buttons_state_on_load()
        else:
             self.view.set_buttons_state_puzzle_on_grid(self.csv_loaded)

    def handle_check_solution(self):
        if not self.current_known_solution:
            self.view.show_message("Thông báo", "Đề bài này không có sẵn đáp án để kiểm tra.", is_error=True)
            return
        try:
            user_grid = self.view.get_grid_data()
            solution = self.current_known_solution
            n = self.current_size
            is_full = True
            has_error = False
            
            for r in range(n):
                for c in range(n):
                    val_user = user_grid[r][c]
                    val_sol = solution[r][c]
                    if val_user == 0:
                        is_full = False
                    elif val_user != val_sol:
                        self.view.mark_error_cell(r, c, True)
                        has_error = True
                    else:
                        self.view.mark_error_cell(r, c, False)

            if not has_error and is_full:
                self.view.show_message("Chúc mừng", "Bạn đã giải chính xác hoàn toàn! 🎉")
            elif has_error:
                self.view.show_message("Kết quả", "Có ô bị sai (nền đỏ). Hãy kiểm tra lại.", is_error=True)
            elif not is_full:
                self.view.show_message("Chưa xong", "Các số đã điền đều đúng. Hãy tiếp tục!")
        except Exception as e:
            self.view.show_message("Lỗi", str(e), is_error=True)

    def handle_hint(self):
        try:
            current_grid = self.view.get_grid_data()
            
            if self.current_known_solution:
                has_error = False
                for r in range(self.current_size):
                    for c in range(self.current_size):
                        val_user = current_grid[r][c]
                        if val_user != 0 and val_user != self.current_known_solution[r][c]:
                            self.view.mark_error_cell(r, c, True)
                            val_char = SudokuConverter.int_to_char(val_user)
                            self.view.show_message("Gợi ý", f"Bạn đang điền sai ô ({r+1}, {c+1}) giá trị {val_char}. Hãy sửa trước!", is_error=True)
                            return
            
            hint = HintGenerator.get_hint(current_grid, self.current_known_solution)
            
            if hint:
                r, c, val, msg_type = hint
                val_char = SudokuConverter.int_to_char(val)
                self.view.highlight_hint_cell(r, c)
                
                if msg_type == 'naked_single':
                    msg = f"Gợi ý ô ({r+1}, {c+1}):\n\nNên điền: {val_char}\n\nLý do: Đây là giá trị khả thi duy nhất (các số khác bị chặn)."
                    self.view.show_message("Gợi ý Logic", msg)
                else:
                    msg = f"Gợi ý ô ({r+1}, {c+1}):\n\nThử điền: {val_char}\n\nLý do: Đây là nước đi khó, cần suy luận sâu."
                    self.view.show_message("Gợi ý Fallback", msg)
            else:
                self.view.show_message("Thông báo", "Không tìm thấy gợi ý nào khả thi (hoặc đã đầy bàn cờ).")
                
        except Exception as e:
            self.view.show_message("Lỗi Gợi ý", str(e), is_error=True)

    def _string_to_grid(self, s: str, n: int):
        grid = []
        s = str(s).replace('.', '0')
        for i in range(n):
            row_str = s[i*n : (i+1)*n]
            row_digits = []
            for char in row_str:
                row_digits.append(SudokuConverter.char_to_int(char))
            grid.append(row_digits)
        return grid

    def _load_from_txt(self, filepath):
        grid_data = []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                cleaned_line = line.replace('.', '0').replace('-', '0').replace('_', '0')
                row_digits = []
                for char in cleaned_line:
                    if char.isalnum(): 
                        val = SudokuConverter.char_to_int(char)
                        row_digits.append(val)
                if row_digits: grid_data.append(row_digits)
        return grid_data

    def handle_solve(self):
        if self.is_play_mode:
            self.view.show_message("Chú ý", "Bạn đang ở chế độ Người chơi. Hãy dùng nút 'Kiểm tra'.", is_error=True)
            return

        grid_data_to_solve = None
        try:
            if self.current_puzzle_data:
                grid_data_to_solve = self.current_puzzle_data
            else:
                grid_data_to_solve = self.view.get_grid_data()
                self.current_puzzle_data = copy.deepcopy(grid_data_to_solve)
            if self.view: self.view.clear_fast_solve_stats()
        except ValueError as e:
            if self.view: self.view.show_message("Lỗi Đầu Vào", f"Lỗi: {e}", is_error=True)
            return
        
        (algo_key, is_demo_mode) = self.view.get_selected_algorithm()
        
        if is_demo_mode:
            if self.is_visualizer_running:
                self.is_visualizer_running = False
                self._log("[DEMO] Đã dừng Demo.", "warning")
            else:
                self.run_visualizer(grid_data_to_solve, algo_key)
        else:
            self.run_fast_solve(grid_data_to_solve, algo_key)

    def run_fast_solve(self, grid_data, algo_key: str):
        algo_map = {
            'bt': ('profiler_bt', 'Backtracking'),
            'fc': ('profiler_fc', 'Forward Checking'),
            'fc_mrv': ('profiler_mrv', 'FC + MRV'),
            'dlx': ('solver_dlx', 'Dancing Links (DLX)') 
        }
        
        module_key, algo_name = algo_map.get(algo_key, (None, None))
        if not module_key:
            self.view.show_message("Lỗi", f"Thuật toán '{algo_key}' không xác định.", is_error=True)
            return

        self._log(f"[GIẢI] Đang giải nhanh bằng {algo_name}...", "cyan")
        if self.view: self.view.set_buttons_state_visualizing(True, self.csv_loaded)
        
        board_wrapper, stats, is_solved = self._run_single_algo(
            grid_data, module_key, algo_key 
        )
        
        if self.view: self.view.set_buttons_state_visualizing(False, self.csv_loaded)
        
        if is_solved:
            solution = board_wrapper.get_board()
            if self.view: 
                self.view.update_grid_with_solution(solution, grid_data)
                self.view.show_fast_solve_stats(stats) 
            
            if self.current_known_solution:
                if solution == self.current_known_solution:
                    self._log("[GIẢI] Giải xong! Đã xác minh 100%!", "green")
                else:
                    self._log("[GIẢI] Lời giải hợp lệ (nhưng khác đáp án mẫu).", "warning")
        else:
            if self.view: 
                self.view.show_message("Thất Bại", "Không tìm thấy lời giải.", is_error=True)
                self.view.clear_fast_solve_stats()
            self._log(f"[GIẢI] Giải thất bại ({algo_name})", "fail")

    def handle_compare(self):
        if self.is_visualizer_running: return
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
            if self.view: self.view.clear_fast_solve_stats()
        except ValueError as e:
            if self.view: self.view.show_message("Lỗi Đầu Vào", f"Lỗi: {e}", is_error=True)
            return
            
        self._log("[PHÂN TÍCH] Đang chạy so sánh 4 thuật toán...", "cyan")
        if self.view: self.view.root.update_idletasks()
        
        try:
            _, bt_stats, _ = self._run_single_algo(grid_data_to_solve, 'profiler_bt', 'bt')
            _, fc_stats, _ = self._run_single_algo(grid_data_to_solve, 'profiler_fc', 'fc')
            _, mrv_stats, _ = self._run_single_algo(grid_data_to_solve, 'profiler_mrv', 'fc_mrv')
            _, dlx_stats, _ = self._run_single_algo(grid_data_to_solve, 'solver_dlx', 'dlx')
            
            self.analysis_popup_window = self.analysis_popup_class(
                self.view, self, bt_stats, fc_stats, mrv_stats, dlx_stats
            )
        except Exception as e:
            self._log(f"[LỖI] {e}", "fail")
            if self.view: self.view.show_message("Lỗi So Sánh", f"{e}", is_error=True)

    def handle_batch_compare_setup(self): pass 
    def handle_run_batch_analysis(self, n_value: int, popup_instance: 'object'): pass

    def _run_single_algo(self, grid_data, module_key: str, algo_key: str):
        SudokuBoard_class = self.model_classes['SudokuBoard']
        
        if algo_key == 'dlx':
            board_wrapper = SudokuBoard_class(copy.deepcopy(grid_data))
            stats = {"backtracks": 0}
            
            dlx_instance = self.model_classes['solver_dlx'].SudokuDLX(board_wrapper)
            
            if 'visualizer' in module_key:
                generator = dlx_instance.solve_visual(board_wrapper, stats)
                return (board_wrapper, stats, generator)
            else:
                board_wrapper.start_timer()
                is_solved = dlx_instance.solve(stats)
                board_wrapper.stop_timer()
                
                final_stats = board_wrapper.get_stats()
                final_stats.update(stats)
                return (board_wrapper, final_stats, is_solved)

        module = self.model_classes.get(module_key, self.model_classes['algorithms'])
        solve_func = None
        
        if algo_key == 'bt':
            if 'profiler' in module_key: solve_func = module.solve_backtracking_profile
            elif 'visualizer' in module_key: solve_func = module.solve_backtracking_visual
            else: solve_func = module.solve_backtracking
        elif algo_key == 'fc':
            if 'profiler' in module_key: solve_func = module.solve_forward_checking_profile
            elif 'visualizer' in module_key: solve_func = module.solve_forward_checking_visual
            else: solve_func = module.solve_forward_checking
        elif algo_key == 'fc_mrv':
            if 'profiler' in module_key: solve_func = module.solve_forward_checking_mrv_profile
            elif 'visualizer' in module_key: solve_func = self.model_classes['visualizer_mrv'].solve_forward_checking_mrv_visual
            else: solve_func = self.model_classes['profiler_mrv'].solve_forward_checking_mrv_profile
        
        board_wrapper = SudokuBoard_class(copy.deepcopy(grid_data))
        stats = {"backtracks": 0} 
        board_wrapper.start_timer()
        
        is_solved_or_generator = solve_func(board_wrapper, stats)
        
        if 'visualizer' in module_key:
            return (board_wrapper, stats, is_solved_or_generator)
        
        board_wrapper.stop_timer()
        final_stats = board_wrapper.get_stats()
        final_stats.update(stats)
        return (board_wrapper, final_stats, is_solved_or_generator)

    def handle_clear(self):
        if self.is_visualizer_running: self.is_visualizer_running = False 
        if self.analysis_popup_window: self.analysis_popup_window.destroy() 
        
        if self.view:
            if self.current_puzzle_data:
                self.view.load_puzzle_to_grid(self.current_puzzle_data, is_play_mode=self.is_play_mode)
                self.view.set_buttons_state_puzzle_on_grid(self.csv_loaded)
            else:
                self.view.clear_grid_and_stats() 
                if self.csv_loaded: self.view.set_buttons_state_csv_loaded()
                else: self.view.set_buttons_state_on_load()
            self._log("[HỆ THỐNG] Đã xóa/khôi phục lưới.", "green")

    def run_visualizer(self, grid_data, algo_key: str): 
        if self.view: 
            self.view.load_puzzle_to_grid(grid_data, is_play_mode=False) 
            self.view.set_buttons_state_visualizing(True, self.csv_loaded)
        
        target_key = "bt"
        mod_name = "visualizer_bt"
        algo_full_name = "Backtracking"

        if algo_key == 'visualizer_dlx':
            target_key = 'dlx'
            mod_name = 'visualizer_dlx'
            algo_full_name = "Dancing Links (DLX)"
        elif algo_key == 'visualizer_mrv':
            target_key = 'fc_mrv'
            mod_name = 'visualizer_mrv'
            algo_full_name = "FC + MRV"
        elif algo_key == 'visualizer_fc':
            target_key = 'fc'
            mod_name = 'visualizer_fc'
            algo_full_name = "Forward Checking"
            
        board_wrapper, _, generator = self._run_single_algo(
            grid_data, mod_name, target_key
        )
        
        self.visualizer_generator = generator
        self.current_visual_board = board_wrapper
        self.is_visualizer_running = True
        self.last_demo_status = None 
        self._log(f"[DEMO] Bắt đầu Demo {algo_full_name}...", "cyan")
        
        self.step_visualizer()

    def step_visualizer(self):
        if not self.is_visualizer_running:
            self.visualizer_generator = None
            self.current_visual_board = None
            if self.view: self.view.set_buttons_state_visualizing(False, self.csv_loaded)
            return
        try:
            data = next(self.visualizer_generator)
            
            if self.view and self.current_puzzle_data:
                self.view.cap_nhat_o_visual(data, self.current_puzzle_data)
            
            status = data.get("status")
            if status in ("solved", "failed"):
                self.is_visualizer_running = False
                self.last_demo_status = status
                msg = "Tìm thấy lời giải!" if status == "solved" else f"Thất bại: {data.get('message')}"
                color = "green" if status == "solved" else "fail"
                self._log(f"[DEMO] {msg}", color)
                self.visualizer_generator = None
                self.current_visual_board = None
                if self.view: self.view.set_buttons_state_visualizing(False, self.csv_loaded)
                return
            
            if self.view:
                delay_ms = self.view.get_demo_speed()
                self.view.root.after(delay_ms, self.step_visualizer)
            else:
                self.is_visualizer_running = False
        except StopIteration:
            self.is_visualizer_running = False
            self.last_demo_status = "stop_iteration"
            self._log("[DEMO] Không tìm thấy lời giải!", "fail")
            if self.view: self.view.set_buttons_state_visualizing(False, self.csv_loaded)
        except Exception as e:
            self.is_visualizer_running = False
            self.last_demo_status = "exception"
            if self.view: self.view.show_message("Lỗi Demo", f"Lỗi: {traceback.format_exc()}", is_error=True)
            self._log(f"[DEMO] Lỗi: {e}", "fail")
            if self.view: self.view.set_buttons_state_visualizing(False, self.csv_loaded)