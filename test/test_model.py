import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# ---------------------------------------------------------------

from src.model.sudoku_board import SudokuBoard
from src.model.algorithms import solve_backtracking, solve_forward_checking

# --- Đề bài dùng chung cho cả 2 bài test ---
puzzle_matrix = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

def run_test_backtracking():
    """Chạy kịch bản kiểm thử cho thuật toán Backtracking."""
    
    print("\n>>> KIỂM THỬ THUẬT TOÁN: Backtracking (Baseline) <<<")
    
    # 1. Khởi tạo Lớp Model
    print("\n--- Đề bài gốc ---")
    board = SudokuBoard(puzzle_matrix)
    print(board)
    
    # 2. Chuẩn bị bộ đếm thống kê
    stats = {"backtracks": 0}

    # 3. Bắt đầu giải
    print("\n--- Đang giải... ---")
    board.start_timer()
    
    try:
        is_solved = solve_backtracking(board, stats)
    except Exception as e:
        print(f"\n!!! LỖI NGHIÊM TRỌNG TRONG THUẬT TOÁN: {e}")
        return
        
    board.stop_timer()
    
    # 4. In kết quả
    if is_solved:
        print("\n--- ĐÃ TÌM THẤY LỜI GẢI ---")
        print(board)
        
        # 5. In thông số
        final_stats = board.get_stats()
        final_stats.update(stats)
        
        print("\n--- THỐNG KÊ HIỆU NĂNG ---")
        print(f"  Thời gian thực thi: {final_stats['execution_time_sec']:.6f} giây")
        print(f"  Số bước quay lui:   {final_stats['backtracks']}")
    else:
        print("\n--- KHÔNG TÌM THẤY LỜI GẢI ---")

def run_test_forward_checking():
    """Chạy kịch bản kiểm thử cho thuật toán Forward Checking."""
    
    print("\n>>> KIỂM THỬ THUẬT TOÁN: Forward Checking (Cải tiến) <<<")
    
    # 1. Khởi tạo Lớp Model
    print("\n--- Đề bài gốc ---")
    board = SudokuBoard(puzzle_matrix)
    print(board)
    
    # 2. Chuẩn bị bộ đếm thống kê
    stats = {"backtracks": 0}

    # 3. Bắt đầu giải
    print("\n--- Đang giải... ---")
    board.start_timer()
    
    try:
        is_solved = solve_forward_checking(board, stats)
    except Exception as e:
        print(f"\n!!! LỖI NGHIÊM TRỌNG TRONG THUẬT TOÁN: {e}")
        return
        
    board.stop_timer()
    
    # 4. In kết quả
    if is_solved:
        print("\n--- ĐÃ TÌM THẤY LỜI GIẢI ---")
        print(board)
        
        # 5. In thông số
        final_stats = board.get_stats()
        final_stats.update(stats)
        
        print("\n--- THỐNG KÊ HIỆU NĂNG ---")
        print(f"  Thời gian thực thi: {final_stats['execution_time_sec']:.6f} giây")
        print(f"  Số bước quay lui:   {final_stats['backtracks']}")
    else:
        print("\n--- KHÔNG TÌM THẤY LỜI GẢI ---")
        
if __name__ == "__main__":
    print("=====================================================")
    print("  BẮT ĐẦU KIỂM THỬ SO SÁNH CÁC THUẬT TOÁN MODEL")
    print("=====================================================")
    
    run_test_backtracking()
    
    print("\n-----------------------------------------------------")
    
    run_test_forward_checking()
    
    print("\n=====================================================")
    print("  KẾT THÚC KIỂM THỬ")
    print("=====================================================")