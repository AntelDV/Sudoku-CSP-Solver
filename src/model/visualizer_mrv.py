from .sudoku_board import SudokuBoard

def solve_forward_checking_mrv_visual(board_wrapper: SudokuBoard, stats: dict):
    try:
        domains = _initialize_domains(board_wrapper)
    except ValueError:
        yield {"status": "failed", "message": "Đề bài gốc không hợp lệ"}
        return False 

    yield from _solve_fc_recursive_mrv_visual(board_wrapper, stats, domains)

def _initialize_domains(board_wrapper):
    # Quy trình khởi tạo giống FC visual
    n = board_wrapper.n
    board = board_wrapper.get_board()
    full_domain = set(range(1, n + 1))
    domains = [[full_domain.copy() for _ in range(n)] for _ in range(n)]
    
    for r in range(n):
        for c in range(n):
            num = board[r][c]
            if num != 0:
                domains[r][c] = {num}
                if not _prune_domains_on_setup(domains, r, c, num, board_wrapper):
                    raise ValueError("Invalid initial puzzle")
    return domains

def _prune_domains_on_setup(domains, r, c, num, board_wrapper):
    # Quy trình cắt tỉa ban đầu giống FC visual
    n = board_wrapper.n
    box_size = board_wrapper.box_size
    neighbors = set()
    for col in range(n): neighbors.add((r, col))
    for row in range(n): neighbors.add((row, c))
    box_r = (r // box_size) * box_size
    box_c = (c // box_size) * box_size
    for br in range(box_r, box_r + box_size):
        for bc in range(box_c, box_c + box_size):
            neighbors.add((br, bc))
    neighbors.discard((r, c))

    for (nr, nc) in neighbors:
        if num in domains[nr][nc]:
            domains[nr][nc].remove(num)
            if not domains[nr][nc]: 
                return False 
    return True

def _find_cell_with_mrv(board_wrapper: SudokuBoard, domains: list):
    """
    Tìm ô trống có domain nhỏ nhất (MRV) để ưu tiên xử lý.
    """
    min_len = board_wrapper.n + 1 
    best_cell = None
    board = board_wrapper.get_board()
    n = board_wrapper.n
    
    for r in range(n):
        for c in range(n):
            if board[r][c] == 0: 
                current_len = len(domains[r][c])
                if current_len == 0: return None 
                
                if current_len < min_len:
                    min_len = current_len
                    best_cell = (r, c)
                    if min_len == 1: return best_cell
    return best_cell

def _solve_fc_recursive_mrv_visual(board_wrapper: SudokuBoard, stats: dict, domains: list):
    # Bước 1: Chọn ô bằng MRV
    empty_cell = _find_cell_with_mrv(board_wrapper, domains)

    if not empty_cell:
        if board_wrapper.find_empty_cell() is None:
            yield {"status": "solved"}
            return True
        else:
            return False 

    row, col = empty_cell
    domain_to_try = list(domains[row][col]) 
    
    for num in domain_to_try:
        board_wrapper.set_cell(row, col, num)
        
        # Báo hiệu thử giá trị
        yield {
            "action": "try",
            "cell": (row, col),
            "num": num,
            "status": "running"
        }

        # Báo hiệu cắt tỉa
        is_consistent, pruned_log = yield from _prune_neighbors_visual(domains, row, col, num, board_wrapper)
        
        if is_consistent:
            result = yield from _solve_fc_recursive_mrv_visual(board_wrapper, stats, domains)
            if result:
                return True 

        # Quay lui
        stats["backtracks"] = stats.get("backtracks", 0) + 1
        yield from _restore_neighbors_visual(domains, pruned_log)
        board_wrapper.set_cell(row, col, 0)
        
        yield {
            "action": "backtrack",
            "cell": (row, col),
            "stats": stats, 
            "status": "running"
        }
    
    return False 

def _prune_neighbors_visual(domains, r, c, num, board_wrapper):
    # (Giống logic cắt tỉa FC Visualizer)
    pruned_log = [] 
    n = board_wrapper.n
    box_size = board_wrapper.box_size
    neighbors = set()
    for col in range(n): neighbors.add((r, col))
    for row in range(n): neighbors.add((row, c))
    box_r = (r // box_size) * box_size
    box_c = (c // box_size) * box_size
    for br in range(box_r, box_r + box_size):
        for bc in range(box_c, box_c + box_size):
            neighbors.add((br, bc))
    neighbors.discard((r, c)) 

    yield {"action": "prune_start", "neighbors": list(neighbors), "status": "running"}

    for (nr, nc) in neighbors:
        if num in domains[nr][nc]:
            domains[nr][nc].remove(num)
            pruned_log.append((nr, nc, num))
            if not domains[nr][nc]:
                yield {"action": "prune_fail", "cell": (nr, nc), "status": "running"}
                return (False, pruned_log) 
    return (True, pruned_log) 

def _restore_neighbors_visual(domains, pruned_log):
    # (Giống logic khôi phục FC Visualizer)
    restored_cells = set((r, c) for (r, c, num) in pruned_log)
    yield {"action": "restore_start", "neighbors": list(restored_cells), "status": "running"}
    for (r, c, num) in pruned_log:
        domains[r][c].add(num)