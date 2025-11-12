from .sudoku_board import SudokuBoard

def solve_backtracking_profile(board_wrapper: SudokuBoard, stats: dict):
    if "nodes_visited" not in stats:
        stats["nodes_visited"] = 0
    return _solve_bt_recursive(board_wrapper, stats)


def _solve_bt_recursive(board_wrapper: SudokuBoard, stats: dict):
    stats["nodes_visited"] += 1
    
    empty_cell = board_wrapper.find_empty_cell()
    if not empty_cell:
        return True 

    row, col = empty_cell

    for num in range(1, 10):
        if board_wrapper.is_valid(num, row, col):
            board_wrapper.set_cell(row, col, num)

            if _solve_bt_recursive(board_wrapper, stats):
                return True 

            stats["backtracks"] += 1
            board_wrapper.set_cell(row, col, 0)
    return False