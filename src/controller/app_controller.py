from tkinter import filedialog, messagebox
import traceback
import pandas as pd
import random
import os
import copy
from typing import TYPE_CHECKING, Type
import threading
import time

if TYPE_CHECKING:
    from src.view.main_window import MainView
    from src.view.analysis_popup import AnalysisPopup
    from src.view.batch_analysis_popup import BatchAnalysisPopup

class AppController:

    def __init__(self, model, analysis_popup_class: Type['AnalysisPopup'], batch_analysis_popup_class: Type['BatchAnalysisPopup'], base_dir: str):
        """
        Khởi tạo Controller.
        
        :param model: Dictionary chứa các lớp và mô-đun của Model.
        :param analysis_popup_class: Lớp View cho cửa sổ "So sánh".
        :param batch_analysis_popup_class: Lớp View cho cửa sổ "Thực nghiệm Hàng loạt".
        :param base_dir: Đường dẫn gốc của ứng dụng (do main.py cung cấp).
        """
        self.model_classes = model  
        self.view: 'MainView' = None
        
        # Lưu đường dẫn gốc và đường dẫn thư mục 'data'
        self.base_dir = base_dir
        self.data_dir = os.path.join(self.base_dir, "data")
        
        # Quản lý các lớp View của cửa sổ Popup
        self.analysis_popup_class = analysis_popup_class
        self.analysis_popup_window = None 
        self.batch_analysis_popup_class = batch_analysis_popup_class
        self.batch_popup_window = None 
        
        # DataFrame để lưu dữ liệu từ file CSV 
        self.kaggle_df: pd.DataFrame = None 
        self.csv_loaded = False
        
        # Quản lý trạng thái của Chế độ Trực quan hóa (Demo)
        self.visualizer_generator = None 
        self.is_visualizer_running = False
        self.last_demo_status = None 
        
        # Lưu trữ đề bài và lời giải hiện tại
        self.current_puzzle_data = None 
        self.current_known_solution = None 
        self.current_visual_board = None
        
        # Cấu hình màu cho việc log ra console
        self.colors = {
            "header": "\033[95m", "blue": "\033[94m", "cyan": "\033[96m",
            "green": "\033[92m", "warning": "\033[93m", "fail": "\033[91m",
            "endc": "\033[0m", "bold": "\033[1m", "underline": "\033[4m"
        }

    def _log(self, message, color="endc"):
        """Hàm nội bộ để in log có màu ra console."""
        if color in self.colors:
            print(f"{self.colors[color]}{message}{self.colors['endc']}")
        else:
            print(message)

    def set_view(self, view: 'MainView'):
        self.view = view
        self.view.set_buttons_state_on_load()
    
    def handle_load_file(self):
        """Xử lý sự kiện nhấn nút 'Nạp dữ liệu'."""
        if self.is_visualizer_running:
            self.view.show_message("Lỗi", "Đang chạy Demo, không thể nạp file.", is_error=True)
            return

        # Ưu tiên mở thư mục 'data' nếu nó tồn tại
        initial_dir = self.base_dir
        if os.path.isdir(self.data_dir):
            initial_dir = self.data_dir

        # 1. Mở hộp thoại để chọn file .csv hoặc .txt
        filepath = filedialog.askopenfilename(
            title="Chọn file CSV hoặc TXT",
            initialdir=initial_dir,  # Mở hộp thoại tại thư mục 'data'
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
            
            # 2. Xử lý nếu là file CSV (Kho dữ liệu đề bài)
            if filepath.endswith(".csv"):
                self._log("[HỆ THỐNG] Đang nạp file CSV, vui lòng chờ...", "cyan")
                if self.view: self.view.root.update_idletasks()
                
                df = pd.read_csv(filepath)
                
                if 'quizzes' not in df.columns or 'solutions' not in df.columns:
                    raise ValueError("File .csv thiếu cột 'quizzes' hoặc 'solutions'.")
                
                # Tự động tính toán độ khó (số gợi ý) nếu chưa có
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
                    self.view.clear_fast_solve_stats() 
            
            # 3. Xử lý nếu là file TXT (Một đề bài duy nhất)
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
                raise ValueError("Định dạng file không được hỗ trợ (chỉ .csv hoặc .txt).")

        except Exception as e:
            # Xử lý nếu nạp file thất bại
            self.kaggle_df = None
            self.csv_loaded = False
            self.current_puzzle_data = None
            self.current_known_solution = None
            if self.view:
                self.view.set_buttons_state_on_load()
                self.view.show_message("Lỗi Nạp File", f"Không thể đọc file:\n{e}", is_error=True)
            self._log(f"[LỖI] Nạp file thất bại: {e}", "fail")
            
    def handle_get_csv_puzzle(self, difficulty: str):
        """Xử lý sự kiện nhấn các nút 'Lấy Đề' (Dễ, Khó, ...)."""
        if self.kaggle_df is None:
            if self.view: self.view.show_message("Lỗi", "Vui lòng 'NẠP DỮ LIỆU' (file .csv) trước.", is_error=True)
            return
            
        try:
            puzzle_col = 'quizzes' 
            solution_col = 'solutions'
            df_filtered = None
            original_difficulty = difficulty
            
            # Logic lọc đề bài theo độ khó (dựa trên số gợi ý)
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
                self._log("[HỆ THỐNG] Không tìm thấy đề, lấy ngẫu nhiên.", "warning")
                if self.view: self.view.show_message("Lỗi Lọc", f"Không tìm thấy bất kỳ đề nào. Lấy ngẫu nhiên.", is_error=True)
                df_filtered = self.kaggle_df 
            
            # Lấy ngẫu nhiên 1 đề từ kho đã lọc
            random_row = df_filtered.sample(n=1).iloc[0]
            puzzle_string = str(random_row[puzzle_col])
            
            # Lưu lại lời giải (để xác minh)
            solution_string = str(random_row[solution_col])
            self.current_known_solution = self._string_to_grid(solution_string)
            
            grid_data = self._string_to_grid(puzzle_string)
            self.current_puzzle_data = copy.deepcopy(grid_data)

            # Tải đề bài lên giao diện
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
        """Chuyển một chuỗi 81 ký tự thành ma trận 9x9."""
        grid = []
        s = str(s).replace('.', '0')
        for i in range(9):
            row_str = s[i*9 : (i+1)*9]
            grid.append([int(char) for char in row_str])
        return grid

    def _load_from_txt(self, filepath):
        """Đọc ma trận 9x9 từ file .txt."""
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
        """Xử lý sự kiện nhấn nút 'Giải' hoặc 'Bắt đầu Demo'."""
        grid_data_to_solve = None
        try:
            # Ưu tiên lấy đề bài đã nạp, nếu không có thì lấy từ lưới
            if self.current_puzzle_data:
                grid_data_to_solve = self.current_puzzle_data
            else:
                grid_data_to_solve = self.view.get_grid_data()
                self.current_puzzle_data = copy.deepcopy(grid_data_to_solve)
            
            if self.view: 
                self.view.clear_fast_solve_stats()
                
        except ValueError as e:
            if self.view: self.view.show_message("Lỗi Đầu Vào", f"Lỗi: {e}", is_error=True)
            return
        
        # Kiểm tra xem người dùng muốn 'Giải nhanh' hay 'Demo'
        (algo_key, is_demo_mode) = self.view.get_selected_algorithm()
        
        if is_demo_mode:
            if self.is_visualizer_running:
                # Nếu demo đang chạy, nút này có nghĩa là "Dừng"
                self.is_visualizer_running = False
                self._log("[DEMO] Đã dừng Demo.", "warning")
            else:
                # Nếu demo chưa chạy, bắt đầu chạy
                self.run_visualizer(grid_data_to_solve, algo_key)
        else:
            # Chạy chế độ giải nhanh (không demo)
            self.run_fast_solve(grid_data_to_solve, algo_key)

    def _grid_to_string(self, grid):
        """Chuyển ma trận 9x9 thành chuỗi 81 ký tự."""
        return "".join(str(cell) for row in grid for cell in row)

    def run_fast_solve(self, grid_data, algo_key: str):
        """Chạy thuật toán ở chế độ 'Giải nhanh' ."""
        
        # Ánh xạ key từ View sang key của Model 
        if algo_key == 'bt':
            module_key = 'profiler_bt'
            algo_name = "Backtracking"
        elif algo_key == 'fc':
            module_key = 'profiler_fc'
            algo_name = "Forward Checking"
        elif algo_key == 'fc_mrv':
            module_key = 'profiler_mrv'
            algo_name = "FC + MRV"
        else:
            self.view.show_message("Lỗi", f"Thuật toán '{algo_key}' không xác định.", is_error=True)
            return

        self._log(f"[GIẢI] Đang giải nhanh bằng {algo_name}...", "cyan")
        
        if self.view: self.view.set_buttons_state_visualizing(True, self.csv_loaded)
        
        # Chạy thuật toán 
        board_wrapper, stats, is_solved = self._run_single_algo(
            grid_data, module_key, algo_key 
        )
        
        if self.view: self.view.set_buttons_state_visualizing(False, self.csv_loaded)
        
        if is_solved:
            solution = board_wrapper.get_board()
            if self.view: 
                self.view.update_grid_with_solution(solution, grid_data)
                self.view.show_fast_solve_stats(stats) 
                
            # Xác minh với lời giải đã biết (nếu có)
            if self.current_known_solution:
                if solution == self.current_known_solution:
                    self._log(f"[GIẢI] Giải xong! Đã xác minh 100%!", "green")
                else:
                    self._log(f"[GIẢI] LỖI XÁC MINH! Lời giải không khớp CSV!", "fail")
            else:
                self._log(f"[GIẢI] Giải xong! (Không có dữ liệu xác minh)", "green")
        else:
            if self.view: 
                self.view.show_message("Thất Bại", "Không tìm thấy lời giải.", is_error=True)
                self.view.clear_fast_solve_stats()
            self._log(f"[GIẢI] Giải thất bại ({algo_name})", "fail")
            
    
    def handle_compare(self):
        """Xử lý sự kiện nhấn nút 'So sánh'."""
        if self.is_visualizer_running:
            if self.view: self.view.show_message("Lỗi", "Đang chạy Demo, không thể so sánh.", is_error=True)
            return
        # Nếu cửa sổ đã mở, đưa nó lên trước
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
            
            if self.view: 
                self.view.clear_fast_solve_stats()
                
        except ValueError as e:
            if self.view: self.view.show_message("Lỗi Đầu Vào", f"Lỗi: {e}", is_error=True)
            return
            
        self._log("[PHÂN TÍCH] Đang phân tích hiệu năng (BT vs FC)...", "cyan")
        if self.view: self.view.root.update_idletasks()
        
        try:
            # 1. Chạy Baseline (Backtracking)
            bt_board, bt_stats, bt_solved = self._run_single_algo(
                grid_data_to_solve, 'profiler_bt', 'bt'
            )
            
            # 2. Chạy Cải tiến (Forward Checking)
            fc_board, fc_stats, fc_solved = self._run_single_algo(
                grid_data_to_solve, 'profiler_fc', 'fc'
            )
            
            if bt_solved and fc_solved:
                self._log("[PHÂN TÍCH] Hoàn tất (BT vs FC). Mở popup.", "green")
                
                # 3. Mở Popup và truyền (controller, stats_bt, stats_fc, grid_data)
                # Popup sẽ tự chạy MRV khi cần
                self.analysis_popup_window = self.analysis_popup_class(
                    self.view, self, bt_stats, fc_stats, grid_data_to_solve
                )
            else:
                if self.view: self.view.show_message("Thất Bại", "Một trong hai thuật toán cơ bản không tìm thấy lời giải.", is_error=True)
                self._log("[PHÂN TÍCH] Phân tích thất bại (không tìm thấy lời giải)", "fail")
        except Exception as e:
            if self.view: self.view.show_message("Lỗi Thực Thi", f"Lỗi nghiêm trọng: {traceback.format_exc()}", is_error=True)
            self._log(f"[LỖI] {e}", "fail")

    def handle_batch_compare_setup(self):
        """Xử lý nhấn nút 'Cài đặt' (⚙️)"""
        if self.is_visualizer_running:
            self.view.show_message("Lỗi", "Đang chạy Demo, không thể chạy thực nghiệm.", is_error=True)
            return
        if self.batch_popup_window and self.batch_popup_window.winfo_exists():
            self.batch_popup_window.focus() 
            return
        
        if not self.csv_loaded or self.kaggle_df is None:
            self.view.show_message("Lỗi", "Vui lòng 'NẠP DỮ LIỆU' (file .csv) trước khi chạy thực nghiệm.", is_error=True)
            return
            
        if self.view: 
            self.view.clear_fast_solve_stats()

        self.batch_popup_window = self.batch_analysis_popup_class(
            self.view, self
        )

    def handle_run_batch_analysis(self, n_value: int, popup_instance: 'BatchAnalysisPopup'):
        """
        Tạo một Thread (luồng) mới để chạy thực nghiệm hàng loạt
        """
        self._log(f"[THỰC NGHIỆM] Bắt đầu chạy thực nghiệm hàng loạt (N={n_value})...", "header")
        
        # Vô hiệu hóa các nút khi đang chạy
        self.view.set_buttons_state_visualizing(True, self.csv_loaded)
        self.view.btn_giai.configure(text="⚡ GIẢI", state="disabled")

        thread = threading.Thread(
            target=self._run_batch_analysis_thread, 
            args=(n_value, popup_instance),
            daemon=True # Tự động tắt thread khi thoát ứng dụng
        )
        thread.start()

    def _run_batch_analysis_thread(self, N: int, popup: 'BatchAnalysisPopup'):
        """
        Hàm logic chính chạy trong Thread, xử lý việc chạy
        hàng loạt N đề bài.
        """
        try:
            # Định nghĩa các khoảng độ khó
            difficulty_ranges = {
                'Dễ': (36, 99),
                'Trung bình': (30, 35),
                'Khó': (25, 29),
                'Siêu khó': (0, 24)
            }
            
            final_results = {}
            total_tasks = len(difficulty_ranges) * N
            tasks_done = 0

            for diff_name, (clues_min, clues_max) in difficulty_ranges.items():
                self._log(f"[THỰC NGHIỆM] Bắt đầu xử lý loại: {diff_name.upper()}", "cyan")
                
                # 1. Lọc và lấy mẫu
                df_filtered = self.kaggle_df[
                    (self.kaggle_df['clues'] >= clues_min) & 
                    (self.kaggle_df['clues'] <= clues_max)
                ]
                
                if len(df_filtered) < N:
                    self._log(f"[THỰC NGHIỆM] Cảnh báo: Không đủ {N} đề '{diff_name}', chỉ tìm thấy {len(df_filtered)}.", "warning")
                    actual_N = len(df_filtered)
                    if actual_N == 0:
                        self._log(f"[THỰC NGHIỆM] Bỏ qua loại '{diff_name}' vì không có đề.", "warning")
                        total_tasks -= N 
                        continue
                    df_sample = df_filtered
                else:
                    actual_N = N
                    df_sample = df_filtered.sample(n=N, random_state=1) # Dùng random_state để kết quả lặp lại được

                # 2. Chuẩn bị biến tổng hợp
                bt_stats_sum = {'time': 0, 'backtracks': 0, 'nodes': 0}
                fc_stats_sum = {'time': 0, 'backtracks': 0, 'nodes': 0, 'prunes': 0}

                # 3. Lặp qua các đề đã lấy mẫu
                for index, row in df_sample.iterrows():
                    # Cập nhật GUI 
                    tasks_done += 1
                    progress_text = f"Đang xử lý: {diff_name} ({tasks_done}/{total_tasks})"
                    progress_perc = tasks_done / total_tasks
                    self.view.root.after(0, popup.update_progress, progress_text, progress_perc)
                    
                    grid_data = self._string_to_grid(str(row['quizzes']))
                    
                    # Chạy Backtracking
                    _bt_board, bt_stats, _bt_solved = self._run_single_algo(
                        grid_data, 'profiler_bt', 'bt'
                    )
                    bt_stats_sum['time'] += bt_stats.get('execution_time_sec', 0)
                    bt_stats_sum['backtracks'] += bt_stats.get('backtracks', 0)
                    bt_stats_sum['nodes'] += bt_stats.get('nodes_visited', 0)

                    # Chạy Forward Checking
                    _fc_board, fc_stats, _fc_solved = self._run_single_algo(
                        grid_data, 'profiler_fc', 'fc'
                    )
                    fc_stats_sum['time'] += fc_stats.get('execution_time_sec', 0)
                    fc_stats_sum['backtracks'] += fc_stats.get('backtracks', 0)
                    fc_stats_sum['nodes'] += fc_stats.get('nodes_visited', 0)
                    fc_stats_sum['prunes'] += fc_stats.get('prunes_made', 0)
                    
                    time.sleep(0.001)
                
                if actual_N == 0: continue

                # 4. Tính trung bình và lưu kết quả
                final_results[diff_name] = {
                    'N': actual_N,
                    'bt_time': bt_stats_sum['time'] / actual_N,
                    'bt_backtracks': bt_stats_sum['backtracks'] / actual_N,
                    'bt_nodes': bt_stats_sum['nodes'] / actual_N,
                    
                    'fc_time': fc_stats_sum['time'] / actual_N,
                    'fc_backtracks': fc_stats_sum['backtracks'] / actual_N,
                    'fc_nodes': fc_stats_sum['nodes'] / actual_N,
                    'fc_prunes': fc_stats_sum['prunes'] / actual_N,
                }
                self._log(f"[THỰC NGHIỆM] Hoàn tất loại: {diff_name.upper()}", "green")

            # 5. Gửi kết quả về GUI (dùng `root.after`)
            self._log(f"[THỰC NGHIỆM] Hoàn tất tất cả. Đang hiển thị kết quả.", "header")
            self.view.root.after(0, popup.on_analysis_complete, final_results)

        except Exception as e:
            # Xử lý lỗi nghiêm trọng trong Thread
            self._log(f"[THỰC NGHIỆM] LỖI NGHIÊM TRỌNG: {traceback.format_exc()}", "fail")
            self.view.root.after(0, popup.destroy) 
            self.view.root.after(0, self.view.show_message, "Lỗi Thực nghiệm", f"Đã xảy ra lỗi: {e}", True)
        
        finally:
            # Luôn luôn bật lại các nút, dù thành công hay thất bại
            self.view.root.after(0, self.view.set_buttons_state_visualizing, False, self.csv_loaded)

    def _run_single_algo(self, grid_data, module_key: str, algo_key: str):
        """        
        Hàm này sẽ chọn đúng module (profiler, visualizer) và
        đúng hàm (bt, fc, fc_mrv) để thực thi.
        
        :param grid_data: Ma trận 9x9 của đề bài.
        :param module_key: 'profiler_bt', 'visualizer_fc', v.v.
        :param algo_key: 'bt', 'fc', 'fc_mrv'.
        :return: (SudokuBoard, stats, (is_solved | generator))
        """
        SudokuBoard_class = self.model_classes['SudokuBoard']
        
        # 1. Xác định module (profiler, visualizer, ...)
        if 'profiler' in module_key:
            module = self.model_classes[module_key]
        elif 'visualizer' in module_key:
            module = self.model_classes[module_key]
        else:
            module = self.model_classes['algorithms']

        # 2. Xác định hàm (bt, fc, fc_mrv)
        solve_func = None
        if algo_key == 'bt':
            if 'profiler' in module_key:
                solve_func = module.solve_backtracking_profile
            elif 'visualizer' in module_key:
                solve_func = module.solve_backtracking_visual
            else: 
                solve_func = module.solve_backtracking
        
        elif algo_key == 'fc':
            if 'profiler' in module_key:
                solve_func = module.solve_forward_checking_profile
            elif 'visualizer' in module_key:
                solve_func = module.solve_forward_checking_visual
            else: 
                solve_func = module.solve_forward_checking
                
        elif algo_key == 'fc_mrv':
            if 'profiler' in module_key:
                solve_func = module.solve_forward_checking_mrv_profile
            elif 'visualizer' in module_key:
                solve_func = self.model_classes['visualizer_fc'].solve_forward_checking_visual
            else: 
                solve_func = self.model_classes['profiler_mrv'].solve_forward_checking_mrv_profile
        
        
        board_wrapper = SudokuBoard_class(copy.deepcopy(grid_data))
        stats = {"backtracks": 0} 
        board_wrapper.start_timer()
        
        # Hàm solve_func có thể trả về (bool) hoặc (generator)
        is_solved_or_generator = solve_func(board_wrapper, stats)
        
        if 'visualizer' in module_key:
            # Nếu là visualizer, trả về generator ngay lập tức
            return (board_wrapper, stats, is_solved_or_generator)

        # Nếu là profiler, dừng đồng hồ và tổng hợp số liệu
        board_wrapper.stop_timer()
        final_stats = board_wrapper.get_stats()
        final_stats.update(stats)
        
        return (board_wrapper, final_stats, is_solved_or_generator)

    def handle_clear(self):
        """Xử lý sự kiện nhấn nút 'Xóa'."""
        # Dừng mọi tiến trình đang chạy
        if self.is_visualizer_running:
            self.is_visualizer_running = False 
        if self.analysis_popup_window and self.analysis_popup_window.winfo_exists():
            self.analysis_popup_window.destroy() 
        if self.batch_popup_window and self.batch_popup_window.winfo_exists():
            self.batch_popup_window.destroy() 

        is_grid_manually_filled = (not self.current_puzzle_data) and (self.view and not self.view.is_grid_empty())

        if self.view:
            if self.current_puzzle_data:
                # Nếu có đề bài, nút "Xóa" chỉ khôi phục lại đề bài gốc
                self.view.load_puzzle_to_grid(self.current_puzzle_data)
                self.view.set_buttons_state_puzzle_on_grid(self.csv_loaded)
                self._log("[HỆ THỐNG] Đã khôi phục đề bài gốc.", "green")
            else:
                # Nếu không có đề bài, nút "Xóa" sẽ dọn sạch lưới
                self.view.clear_grid_and_stats() 
                if self.csv_loaded:
                    self.view.set_buttons_state_csv_loaded()
                else:
                    self.view.set_buttons_state_on_load()
                
                if is_grid_manually_filled:
                     self._log("[HỆ THỐNG] Đã xóa lưới (nhập tay).", "green")
                else:
                     self._log("[HỆ THỐNG] Đã xóa trắng lưới.", "green")

    def handle_grid_modified(self, event, r, c):
        """Xử lý sự kiện người dùng tự nhập số vào lưới."""
        # Khi người dùng sửa lưới, đề bài hiện tại bị vô hiệu hóa
        self.current_puzzle_data = None
        self.current_known_solution = None
        
        if self.view: 
            self.view.clear_fast_solve_stats()
            
        is_empty = self.view.is_grid_empty()
        
        if is_empty:
            if self.csv_loaded:
                self.view.set_buttons_state_csv_loaded()
            else:
                self.view.set_buttons_state_on_load()
        else:
             self.view.set_buttons_state_puzzle_on_grid(self.csv_loaded)
        
        self._log("[HỆ THỐNG] Đã phát hiện sửa đổi.", "warning")
        
        # Logic kiểm tra ràng buộc theo thời gian thực
        try:
            grid_data = self.view.get_grid_data()
            num_str = self.view.cac_o_nhap[(r, c)].get()
            
            if num_str == "":
                self.view.set_cell_validity(r, c, True) # Ô trống là hợp lệ
                return

            num = int(num_str)
            
            SudokuBoard_class = self.model_classes['SudokuBoard']
            board = SudokuBoard_class(grid_data)
            
            # Tạm thời giấu số hiện tại để kiểm tra
            board.set_cell(r, c, 0)
            is_ok = board.is_valid(num, r, c)
            
            # Tô viền đỏ nếu vi phạm
            self.view.set_cell_validity(r, c, is_ok)
            
            if not is_ok:
                self.view.show_message("Lỗi Nhập liệu", f"Số {num} đã vi phạm ràng buộc tại ô ({r+1}, {c+1}). Số này sẽ bị xóa.", is_error=True)
                self.view.cac_o_nhap[(r, c)].delete(0, "end")
                self.view.set_cell_validity(r, c, True) 
                
        except Exception as e:
            self._log(f"[LỖI] Kiểm tra hợp lệ thất bại: {e}", "fail")
            if self.view:
                self.view.show_message("Lỗi", f"Lỗi khi kiểm tra ô: {e}", is_error=True)

    def run_visualizer(self, grid_data, algo_name: str):
        """Chuẩn bị và khởi chạy Chế độ Trực quan hóa (Demo)."""
        if self.view: 
            self.view.load_puzzle_to_grid(grid_data) 
            self.view.set_buttons_state_visualizing(True, self.csv_loaded)
        
        algo_key = 'fc' if 'fc' in algo_name else 'bt' 
        
        # Chạy thuật toán 
        board_wrapper, _stats, generator = self._run_single_algo(
            grid_data, algo_name, algo_key
        )
        self.visualizer_generator = generator
        self.current_visual_board = board_wrapper
        
        self.is_visualizer_running = True
        self.last_demo_status = None 
        
        algo_full_name = "Forward Checking" if algo_key == 'fc' else "Backtracking"
        self._log(f"[DEMO] Bắt đầu Demo {algo_full_name}...", "cyan")
        self.step_visualizer()

    def step_visualizer(self):
        """
        Thực hiện một bước duy nhất trong generator của visualizer.
        Hàm này sẽ tự gọi lại chính nó (dùng `root.after`) để tạo
        thành một vòng lặp demo.
        """
        if not self.is_visualizer_running:
            # Người dùng đã nhấn "Dừng Demo"
            self.visualizer_generator = None
            self.current_visual_board = None
            if self.view:
                self.view.set_buttons_state_visualizing(False, self.csv_loaded)
            return
            
        try:
            # Lấy trạng thái tiếp theo từ generator
            data = next(self.visualizer_generator)
            
            if self.view and self.current_puzzle_data:
                self.view.cap_nhat_o_visual(data, self.current_puzzle_data)
            
            status = data.get("status")
            if status == "solved":
                # Demo thành công
                self.is_visualizer_running = False
                self.last_demo_status = "solved" # Lưu trạng thái
                if self.current_known_solution:
                    if self.current_visual_board and self.current_visual_board.get_board() == self.current_known_solution:
                         self._log("[DEMO] Demo xong! Đã xác minh 100%!", "green")
                    else:
                         self._log("[DEMO] Demo xong! LỖI XÁC MINH!", "fail")
                else:
                    self._log("[DEMO] Demo hoàn tất: Đã tìm thấy lời giải!", "green")

                self.visualizer_generator = None
                self.current_visual_board = None
                if self.view:
                    self.view.set_buttons_state_visualizing(False, self.csv_loaded)
                return
                
            elif status == "failed":
                # Đề bài không hợp lệ
                self.is_visualizer_running = False
                self.last_demo_status = "failed" # Lưu trạng thái
                self._log(f"[DEMO] Thất bại: {data.get('message')}", "fail")
                self.visualizer_generator = None
                self.current_visual_board = None
                if self.view:
                    self.view.set_buttons_state_visualizing(False, self.csv_loaded)
                return
            
            # Nếu demo vẫn đang chạy, hẹn giờ cho bước tiếp theo
            if self.view:
                delay_ms = self.view.get_demo_speed()
                self.view.root.after(delay_ms, self.step_visualizer)
            else:
                self.is_visualizer_running = False
            
        except StopIteration:
            # Generator đã kết thúc nhưng không tìm thấy lời giải
            self.is_visualizer_running = False
            self.last_demo_status = "stop_iteration" # Lưu trạng thái
            self._log("[DEMO] Không tìm thấy lời giải!", "fail")
            
            if self.view and self.current_puzzle_data:
                # Cập nhật lần cuối cho thống kê
                final_data = {'status': 'failed', 'stats': stats}
                self.view.cap_nhat_o_visual(final_data, self.current_puzzle_data)
                
            self.visualizer_generator = None
            self.current_visual_board = None
            if self.view:
                self.view.set_buttons_state_visualizing(False, self.csv_loaded)
                
        except Exception as e:
            # Lỗi nghiêm trọng
            self.is_visualizer_running = False
            self.last_demo_status = "exception" # Lưu trạng thái
            if self.view:
                self.view.show_message("Lỗi Demo", f"Lỗi nghiêm trọng: {traceback.format_exc()}", is_error=True)
            self._log(f"[DEMO] Lỗi: {e}", "fail")
            self.visualizer_generator = None
            self.current_visual_board = None
            if self.view:
                self.view.set_buttons_state_visualizing(False, self.csv_loaded)