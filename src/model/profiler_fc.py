from .sudoku_board import SudokuBoard

def solve_forward_checking_profile(board_wrapper: SudokuBoard, stats: dict):
    """
    Hàm "public" để khởi chạy Forward Checking Profiler.
    """
    
    if "nodes_visited" not in stats:
        stats["nodes_visited"] = 0
    if "prunes_made" not in stats:
        stats["prunes_made"] = 0
        
    try:
        domains = _initialize_domains(board_wrapper.get_board(), stats)
    except ValueError:
        return False 

    return _solve_fc_recursive(board_wrapper, stats, domains)

def _initialize_domains(board, stats):
    """Tạo và tiền xử lý (pre-prune) các miền giá trị."""
    full_domain = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    domains = [[full_domain.copy() for _ in range(9)] for _ in range(9)]
    
    for r in range(9):
        for c in range(9):
            num = board[r][c]
            if num != 0:
                domains[r][c] = {num}
                if not _prune_domains_on_setup(domains, r, c, num, stats):
                    raise ValueError("Invalid initial puzzle")
    
    return domains

def _prune_domains_on_setup(domains, r, c, num, stats):
    """Hàm cắt tỉa riêng cho bước khởi tạo."""
    for col in range(9):
        if col != c and num in domains[r][col]:
            domains[r][col].remove(num)
            stats["prunes_made"] += 1 
            if not domains[r][col]: return False 

    for row in range(9):
        if row != r and num in domains[row][c]:
            domains[row][c].remove(num)
            stats["prunes_made"] += 1 
            if not domains[row][c]: return False

    box_r, box_c = (r // 3) * 3, (c // 3) * 3
    for br in range(box_r, box_r + 3):
        for bc in range(box_c, box_c + 3):
            if (br, bc) != (r, c) and num in domains[br][bc]:
                domains[br][bc].remove(num)
                stats["prunes_made"] += 1 
                if not domains[br][bc]: return False
                
    return True

def _solve_fc_recursive(board_wrapper: SudokuBoard, stats: dict, domains: list):
    stats["nodes_visited"] += 1
    
    empty_cell = board_wrapper.find_empty_cell()
    if not empty_cell:
        return True  

    row, col = empty_cell
    domain_to_try = list(domains[row][col]) 
    
    for num in domain_to_try:
        board_wrapper.set_cell(row, col, num)
        
        is_consistent, pruned_log = _prune_neighbors_domains(domains, row, col, num, stats)
        
        if is_consistent:
            if _solve_fc_recursive(board_wrapper, stats, domains):
                return True 

        stats["backtracks"] += 1
        _restore_neighbors_domains(domains, pruned_log)
        board_wrapper.set_cell(row, col, 0)
    
    return False

def _prune_neighbors_domains(domains, r, c, num, stats):
    """Cắt tỉa 'num' khỏi miền giá trị của các hàng xóm."""
    pruned_log = [] 
    
    for col in range(9):
        if col != c and num in domains[r][col]:
            domains[r][col].remove(num)
            stats["prunes_made"] += 1 
            pruned_log.append((r, col, num))
            if not domains[r][col]: return (False, pruned_log) 

    for row in range(9):
        if row != r and num in domains[row][c]:
            domains[row][c].remove(num)
            stats["prunes_made"] += 1 
            pruned_log.append((row, c, num))
            if not domains[row][c]: return (False, pruned_log)

    box_r, box_c = (r // 3) * 3, (c // 3) * 3
    for br in range(box_r, box_r + 3):
        for bc in range(box_c, box_c + 3):
            if (br, bc) != (r, c) and br != r and bc != c:
                if num in domains[br][bc]:
                    domains[br][bc].remove(num)
                    stats["prunes_made"] += 1 
                    pruned_log.append((br, bc, num))
                    if not domains[br][bc]: return (False, pruned_log)
                    
    return (True, pruned_log) 

def _restore_neighbors_domains(domains, pruned_log):
    """Khôi phục lại các miền giá trị từ log."""
    for (r, c, num) in pruned_log:
        domains[r][c].add(num)