from .sudoku_board import SudokuBoard

def _find_cell_with_mrv(board_wrapper: SudokuBoard, domains: list):
    """
    Chiến lược MRV (Minimum Remaining Values):
    - Quét toàn bộ bàn cờ.
    - Chọn ô trống có ít lựa chọn nhất (domain nhỏ nhất).
    - Giúp phát hiện ngõ cụt sớm hơn.
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

def solve_forward_checking_mrv_profile(board_wrapper: SudokuBoard, stats: dict):
    """
    Thuật toán FC kết hợp MRV có đo hiệu năng.
    """
    if "nodes_visited" not in stats: stats["nodes_visited"] = 0
    if "prunes_made" not in stats: stats["prunes_made"] = 0
        
    try:
        domains = _initialize_domains(board_wrapper, stats)
    except ValueError:
        return False 

    return _solve_fc_recursive_mrv(board_wrapper, stats, domains)

def _initialize_domains(board_wrapper, stats):
    # Quy trình khởi tạo giống FC: Tạo domain -> Cắt tỉa ban đầu
    n = board_wrapper.n
    board = board_wrapper.get_board()
    full_domain = set(range(1, n + 1))
    domains = [[full_domain.copy() for _ in range(n)] for _ in range(n)]
    
    for r in range(n):
        for c in range(n):
            num = board[r][c]
            if num != 0:
                domains[r][c] = {num}
                if not _prune_domains_on_setup(domains, r, c, num, stats, board_wrapper):
                    raise ValueError("Invalid initial puzzle")
    return domains

def _prune_domains_on_setup(domains, r, c, num, stats, board_wrapper):
    # Cắt tỉa số đã có sẵn khỏi Hàng, Cột, Khối
    n = board_wrapper.n
    box_size = board_wrapper.box_size
    
    for col in range(n):
        if col != c and num in domains[r][col]:
            domains[r][col].remove(num)
            stats["prunes_made"] += 1 
            if not domains[r][col]: return False 
    for row in range(n):
        if row != r and num in domains[row][c]:
            domains[row][c].remove(num)
            stats["prunes_made"] += 1 
            if not domains[row][c]: return False
    box_r = (r // box_size) * box_size
    box_c = (c // box_size) * box_size
    for br in range(box_r, box_r + box_size):
        for bc in range(box_c, box_c + box_size):
            if (br, bc) != (r, c) and num in domains[br][bc]:
                domains[br][bc].remove(num)
                stats["prunes_made"] += 1 
                if not domains[br][bc]: return False
    return True

def _solve_fc_recursive_mrv(board_wrapper: SudokuBoard, stats: dict, domains: list):
    """
    Quy trình FC + MRV:
    1. Chọn ô tốt nhất bằng hàm MRV (thay vì chọn lần lượt).
    2. Thử các giá trị trong domain.
    3. Cắt tỉa -> Đệ quy -> Khôi phục.
    """
    stats["nodes_visited"] += 1
    
    empty_cell = _find_cell_with_mrv(board_wrapper, domains)
    if not empty_cell:
        if board_wrapper.find_empty_cell() is None: return True 
        else: return False 
        
    row, col = empty_cell
    domain_to_try = list(domains[row][col]) 
    
    for num in domain_to_try:
        board_wrapper.set_cell(row, col, num)
        
        is_consistent, pruned_log = _prune_neighbors_domains(domains, row, col, num, stats, board_wrapper)
        
        if is_consistent:
            if _solve_fc_recursive_mrv(board_wrapper, stats, domains):
                return True 

        stats["backtracks"] = stats.get("backtracks", 0) + 1
        _restore_neighbors_domains(domains, pruned_log)
        board_wrapper.set_cell(row, col, 0)
    
    return False

def _prune_neighbors_domains(domains, r, c, num, stats, board_wrapper):
    # Cắt tỉa hàng xóm 
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

    for (nr, nc) in neighbors:
        if num in domains[nr][nc]:
            domains[nr][nc].remove(num)
            stats["prunes_made"] += 1 
            pruned_log.append((nr, nc, num))
            if not domains[nr][nc]: 
                return (False, pruned_log) 
    return (True, pruned_log) 

def _restore_neighbors_domains(domains, pruned_log):
    for (r, c, num) in pruned_log:
        domains[r][c].add(num)