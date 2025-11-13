from .sudoku_board import SudokuBoard

def solve_forward_checking_visual(board_wrapper: SudokuBoard, stats: dict):
    """
    Tạo hàm Generator (trực quan hóa) cho thuật toán Forward Checking.
    
    Hàm này "yield" các trạng thái: thử, quay lui, bắt đầu cắt tỉa,
    cắt tỉa thất bại, và khôi phục.
    
    :param board_wrapper: Đối tượng SudokuBoard.
    :param stats: Dictionary để đếm (chỉ đếm backtracks).
    :return: (Generator) Trả về các dictionary trạng thái.
    """
    try:
        # 1. Khởi tạo miền giá trị ban đầu
        domains = _initialize_domains(board_wrapper.get_board())
    except ValueError:
        # Đề bài gốc không hợp lệ
        yield {"status": "failed", "message": "Đề bài gốc không hợp lệ"}
        return False 

    # 2. Gọi hàm đệ quy (generator)
    yield from _solve_fc_recursive_visual(board_wrapper, stats, domains)

def _initialize_domains(board):
    """
    Tạo và tiền xử lý (pre-prune) các miền giá trị dựa trên đề bài.
    """
    full_domain = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    domains = [[full_domain.copy() for _ in range(9)] for _ in range(9)]
    
    for r in range(9):
        for c in range(9):
            num = board[r][c]
            if num != 0:
                domains[r][c] = {num}
                if not _prune_domains_on_setup(domains, r, c, num):
                    raise ValueError("Invalid initial puzzle")
    return domains

def _prune_domains_on_setup(domains, r, c, num):
    """Hàm cắt tỉa riêng cho bước khởi tạo."""
    neighbors = set()
    for col in range(9): neighbors.add((r, col))
    for row in range(9): neighbors.add((row, c))
    box_r, box_c = (r // 3) * 3, (c // 3) * 3
    for br in range(box_r, box_r + 3):
        for bc in range(box_c, box_c + 3):
            neighbors.add((br, bc))
    neighbors.remove((r, c))

    for (nr, nc) in neighbors:
        if num in domains[nr][nc]:
            domains[nr][nc].remove(num)
            if not domains[nr][nc]: 
                return False 
    return True


def _solve_fc_recursive_visual(board_wrapper: SudokuBoard, stats: dict, domains: list):
    """
    Hàm đệ quy (generator) chính cho Forward Checking.
    
    :param board_wrapper: Đối tượng SudokuBoard.
    :param stats: Dictionary thống kê (sẽ được cập nhật).
    :param domains: Cấu trúc miền giá trị.
    :return: (Generator)
    """
    # 1. Tìm ô trống
    empty_cell = board_wrapper.find_empty_cell()
    if not empty_cell:
        yield {"status": "solved"}
        return True  

    row, col = empty_cell
    domain_to_try = list(domains[row][col]) 
    
    # 2. Lặp qua miền giá trị
    for num in domain_to_try:
        
        board_wrapper.set_cell(row, col, num)
        
        # --- YIELD 1: Báo cáo "ĐANG THỬ" ---
        yield {
            "action": "try",
            "cell": (row, col),
            "num": num,
            "status": "running"
        }

        # 3. (FORWARD CHECKING) Cắt tỉa hàng xóm
        is_consistent, pruned_log = yield from _prune_neighbors_visual(domains, row, col, num)
        
        if is_consistent:
            # 4. Nếu cắt tỉa OK -> Gọi đệ quy
            result = yield from _solve_fc_recursive_visual(board_wrapper, stats, domains)
            if result:
                return True 

        # 5. (BACKTRACK)
        stats["backtracks"] += 1
        
        # 5.1. Khôi phục miền giá trị
        yield from _restore_neighbors_visual(domains, pruned_log)
        # 5.2. Đặt lại ô
        board_wrapper.set_cell(row, col, 0)
        
        # --- YIELD 2: Báo cáo "QUAY LUI" ---
        yield {
            "action": "backtrack",
            "cell": (row, col),
            "stats": stats, 
            "status": "running"
        }
    
    return False 

def _prune_neighbors_visual(domains, r, c, num):
    """
    Generator cắt tỉa miền giá trị của hàng xóm (cho Demo).
    
    :return: (tuple) (bool: is_consistent, list: pruned_log)
    """
    pruned_log = [] 
    
    # Tìm tất cả hàng xóm
    neighbors = set()
    for col in range(9): neighbors.add((r, col))
    for row in range(9): neighbors.add((row, c))
    box_r, box_c = (r // 3) * 3, (c // 3) * 3
    for br in range(box_r, box_r + 3):
        for bc in range(box_c, box_c + 3):
            neighbors.add((br, bc))
    neighbors.remove((r, c)) 

    # --- YIELD 3: Báo cáo "BẮT ĐẦU CẮT TỈA" (Tô viền xanh) ---
    yield {
        "action": "prune_start",
        "neighbors": list(neighbors),
        "status": "running"
    }

    # Bắt đầu cắt tỉa
    for (nr, nc) in neighbors:
        if num in domains[nr][nc]:
            domains[nr][nc].remove(num)
            pruned_log.append((nr, nc, num))
            
            if not domains[nr][nc]:
                # --- YIELD 4: Báo cáo "CẮT TỈA THẤT BẠI" (Tô viền đỏ) ---
                yield {
                    "action": "prune_fail", 
                    "cell": (nr, nc),
                    "status": "running"
                }
                return (False, pruned_log) # Phát hiện ngõ cụt
                    
    return (True, pruned_log) 

def _restore_neighbors_visual(domains, pruned_log):
    """
    Generator khôi phục miền giá trị (cho Demo).
    
    :param domains: Cấu trúc miền giá trị.
    :param pruned_log: Danh sách (r, c, num) đã bị xóa.
    """
    restored_cells = set((r, c) for (r, c, num) in pruned_log)
    
    # --- YIELD 5: Báo cáo "BẮT ĐẦU KHÔI PHỤC" (Tô viền xám) ---
    yield {
        "action": "restore_start",
        "neighbors": list(restored_cells),
        "status": "running"
    }
    
    # Thực hiện khôi phục
    for (r, c, num) in pruned_log:
        domains[r][c].add(num)
}