from .sudoku_board import SudokuBoard

def solve_backtracking_visual(board_wrapper: SudokuBoard, stats: dict):
    """
    Generator Visualizer cho Backtracking.
    Sử dụng yield để trả trạng thái từng bước cho giao diện vẽ.
    """
    empty_cell = board_wrapper.find_empty_cell()

    if not empty_cell:
        yield {"status": "solved"}
        return True  

    row, col = empty_cell

    for num in range(1, board_wrapper.n + 1):
        if board_wrapper.is_valid(num, row, col):
            board_wrapper.set_cell(row, col, num)
            
            # Báo hiệu: Đang thử điền số (Tô xanh)
            yield {
                "action": "try",
                "cell": (row, col),
                "num": num,
                "status": "running"
            }

            result = yield from solve_backtracking_visual(board_wrapper, stats)
            if result:
                return True 

            # Thất bại -> Quay lui -> Reset ô về 0
            stats["backtracks"] = stats.get("backtracks", 0) + 1
            board_wrapper.set_cell(row, col, 0) 

            # Báo hiệu: Đang quay lui (Tô đỏ)
            yield {
                "action": "backtrack",
                "cell": (row, col),
                "stats": stats, 
                "status": "running"
            }

    return False