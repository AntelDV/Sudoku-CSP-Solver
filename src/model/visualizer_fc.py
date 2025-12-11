from .sudoku_board import SudokuBoard

def solve_forward_checking_visual(board_wrapper: SudokuBoard, stats: dict):
    """
    Generator Visualizer cho Forward Checking.
    """
    try:
        domains = _initialize_domains(board_wrapper)
    except ValueError:
        yield {"status": "failed", "message": "Đề bài gốc không hợp lệ"}
        return False 

    yield from _solve_fc_recursive_visual(board_wrapper, stats, domains)

def _initialize_domains(board_wrapper):
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
    n = board_wrapper.n
    box_size = board_wrapper.box_size
    for col in range(n):
        if col != c and num in domains[r][col]:
            domains[r][col].remove(num)
            if not domains[r][col]: return False 
    for row in range(n):
        if row != r and num in domains[row][c]:
            domains[row][c].remove(num)
            if not domains[row][c]: return False
    box_r = (r // box_size) * box_size
    box_c = (c // box_size) * box_size
    for br in range(box_r, box_r + box_size):
        for bc in range(box_c, box_c + box_size):
            if (br, bc) != (r, c) and num in domains[br][bc]:
                domains[br][bc].remove(num)
                if not domains[br][bc]: return False
    return True

def _solve_fc_recursive_visual(board_wrapper: SudokuBoard, stats: dict, domains: list):
    empty_cell = board_wrapper.find_empty_cell()
    if not empty_cell:
        yield {"status": "solved"}
        return True  

    row, col = empty_cell
    domain_to_try = list(domains[row][col]) 
    
    for num in domain_to_try:
        board_wrapper.set_cell(row, col, num)
        
        # Báo hiệu: Đang thử điền
        yield {"action": "try", "cell": (row, col), "num": num, "status": "running"}

        # Thực hiện Cắt tỉa - Lấy về cả neighbors để sau này restore màu
        is_consistent, pruned_log, neighbors_list = yield from _prune_neighbors_visual(domains, row, col, num, board_wrapper)
        
        if is_consistent:
            result = yield from _solve_fc_recursive_visual(board_wrapper, stats, domains)
            if result: return True 

        # Quay lui
        stats["backtracks"] = stats.get("backtracks", 0) + 1
        
        # Báo hiệu Khôi phục (Truyền neighbors_list để dọn màu xanh)
        yield from _restore_neighbors_visual(domains, pruned_log, neighbors_list)
        
        board_wrapper.set_cell(row, col, 0)
        yield {"action": "backtrack", "cell": (row, col), "stats": stats, "status": "running"}
    
    return False 

def _prune_neighbors_visual(domains, r, c, num, board_wrapper):
    """
    Generator cắt tỉa: Gửi thông báo 'prune_start' để UI tô viền xanh các ô liên quan.
    """
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
    
    neighbors_list = list(neighbors)

    # Báo hiệu bắt đầu cắt tỉa (Tô xanh)
    yield {"action": "prune_start", "neighbors": neighbors_list, "status": "running"}

    for (nr, nc) in neighbors:
        if num in domains[nr][nc]:
            domains[nr][nc].remove(num)
            pruned_log.append((nr, nc, num))
            if not domains[nr][nc]:
                # Nếu cắt tỉa thất bại -> Báo hiệu tô đỏ
                yield {"action": "prune_fail", "cell": (nr, nc), "status": "running"}
                return (False, pruned_log, neighbors_list)
    return (True, pruned_log, neighbors_list)

def _restore_neighbors_visual(domains, pruned_log, neighbors_list):
    """
    Generator khôi phục: Gửi thông báo 'restore_start' để UI xóa màu xanh.
    """
    yield {"action": "restore_start", "neighbors": neighbors_list, "status": "running"}
    
    for (r, c, num) in pruned_log:
        domains[r][c].add(num)