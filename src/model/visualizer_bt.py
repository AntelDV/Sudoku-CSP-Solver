from .sudoku_board import SudokuBoard

def solve_backtracking_visual(board_wrapper: SudokuBoard, stats: dict):
    """
    Tạo hàm Generator (trực quan hóa) cho thuật toán Backtracking.
    
    Thay vì trả về (bool), hàm này "yield" (trả về) một
    dictionary trạng thái sau mỗi hành động (thử, quay lui)
    để View có thể cập nhật giao diện.
    
    :param board_wrapper: Đối tượng SudokuBoard.
    :param stats: Dictionary để đếm (chỉ đếm backtracks).
    :return: (Generator) Trả về các dictionary trạng thái.
    """
    
    # 1. Tìm ô trống tiếp theo
    empty_cell = board_wrapper.find_empty_cell()

    if not empty_cell:
        # Không còn ô trống -> Báo thành công
        yield {"status": "solved"}
        return True  

    row, col = empty_cell

    # 2. Thử các giá trị từ 1 đến 9
    for num in range(1, 10):
        
        # 3. Kiểm tra ràng buộc
        if board_wrapper.is_valid(num, row, col):
            
            # 3.1. Gán giá trị
            board_wrapper.set_cell(row, col, num)
            
            # --- YIELD 1: Báo cáo "ĐANG THỬ" ---
            yield {
                "action": "try",
                "cell": (row, col),
                "num": num,
                "status": "running"
            }

            # 3.2. "Gọi đệ quy" (bằng yield from)
            result = yield from solve_backtracking_visual(board_wrapper, stats)
            
            if result:
                return True # Nhánh con thành công -> lan truyền True lên

            # 3.3. Nếu đệ quy (result) trả về False -> NGÕ CỤT
            stats["backtracks"] += 1
            board_wrapper.set_cell(row, col, 0) # Đặt lại giá trị ô

            # --- YIELD 2: Báo cáo "QUAY LUI" ---
            yield {
                "action": "backtrack",
                "cell": (row, col),
                "stats": stats, # Gửi stats mới nhất lên GUI
                "status": "running"
            }

    # 4. Nếu thử hết 9 số mà không số nào hợp lệ
    return False # Kích hoạt quay lui ở cấp cao hơn
}