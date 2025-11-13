from .sudoku_board import SudokuBoard

def solve_backtracking_profile(board_wrapper: SudokuBoard, stats: dict):
    """
    Hàm "public" để khởi chạy Backtracking phiên bản Profiler.
    Đếm số liệu chi tiết hơn,cụ thể là 'nodes_visited' (số nút đã duyệt).
    
    :param board_wrapper: Đối tượng SudokuBoard.
    :param stats: Dictionary thống kê (sẽ được cập nhật).
    :return: (bool) True nếu tìm thấy lời giải.
    """
    if "nodes_visited" not in stats:
        stats["nodes_visited"] = 0
    return _solve_bt_recursive(board_wrapper, stats)


def _solve_bt_recursive(board_wrapper: SudokuBoard, stats: dict):
    """
    Hàm đệ quy Backtracking (Profiler) đếm số nút đã duyệt.
    
    :param board_wrapper: Đối tượng SudokuBoard.
    :param stats: Dictionary thống kê (sẽ được cập nhật).
    :return: (bool) True nếu tìm thấy lời giải.
    """
    # Mỗi lần gọi hàm đệ quy được tính là 1 nút đã duyệt
    stats["nodes_visited"] += 1
    
    # 1. Tìm ô trống
    empty_cell = board_wrapper.find_empty_cell()
    if not empty_cell:
        return True # Đã giải xong

    row, col = empty_cell

    # 2. Lặp qua miền giá trị (1-9)
    for num in range(1, 10):
        # 3. Kiểm tra ràng buộc
        if board_wrapper.is_valid(num, row, col):
            # 3.1. Gán giá trị
            board_wrapper.set_cell(row, col, num)

            # 3.2. Gọi đệ quy
            if _solve_bt_recursive(board_wrapper, stats):
                return True 

            # 3.3. Quay lui
            stats["backtracks"] += 1
            board_wrapper.set_cell(row, col, 0)
            
    # 4. Thử hết 9 số thất bại
    return False
