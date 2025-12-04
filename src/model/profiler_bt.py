from .sudoku_board import SudokuBoard

def solve_backtracking_profile(board_wrapper: SudokuBoard, stats: dict):
    """
    Thuật toán Backtracking có đo hiệu năng (đếm số nút).
    """
    if "nodes_visited" not in stats:
        stats["nodes_visited"] = 0
    return _solve_bt_recursive(board_wrapper, stats)

def _solve_bt_recursive(board_wrapper: SudokuBoard, stats: dict):
    """
    Quy trình Backtracking:
    1. Tìm ô trống. Nếu hết ô trống -> Giải xong.
    2. Thử lần lượt các số từ 1 đến N.
    3. Nếu điền được -> Gọi đệ quy tiếp.
    4. Nếu nhánh đệ quy thất bại -> Quay lui (Xóa số) và thử số khác.
    """
    stats["nodes_visited"] += 1
    
    empty_cell = board_wrapper.find_empty_cell()
    if not empty_cell:
        return True 

    row, col = empty_cell

    for num in range(1, board_wrapper.n + 1):
        if board_wrapper.is_valid(num, row, col):
            # Thử điền số
            board_wrapper.set_cell(row, col, num)

            # Đệ quy
            if _solve_bt_recursive(board_wrapper, stats):
                return True 

            # Quay lui (Backtrack)
            stats["backtracks"] = stats.get("backtracks", 0) + 1
            board_wrapper.set_cell(row, col, 0)
            
    return False