from .sudoku_board import SudokuBoard
import random

def solve_forward_checking_mrv_visual(board_wrapper: SudokuBoard, stats: dict):
    try:
        domains = _initialize_domains(board_wrapper)
    except ValueError:
        yield {"status": "failed", "message": "Đề bài gốc không hợp lệ", "stats": stats}
        return False 

    yield from _solve_fc_recursive_mrv_visual(board_wrapper, stats, domains)

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

def _count_unassigned_neighbors(board, n, box_size, r, c):
    degree = 0
    for col in range(n):
        if col != c and board[r][col] == 0: degree += 1
    for row in range(n):
        if row != r and board[row][c] == 0: degree += 1
    box_r = (r // box_size) * box_size
    box_c = (c // box_size) * box_size
    for br in range(box_r, box_r + box_size):
        for bc in range(box_c, box_c + box_size):
            if (br, bc) != (r, c) and board[br][bc] == 0:
                degree += 1
    return degree

def _find_cell_with_mrv(board_wrapper: SudokuBoard, domains: list):
    min_len = board_wrapper.n + 1 
    candidates = [] 
    board = board_wrapper.get_board()
    n = board_wrapper.n
    box_size = board_wrapper.box_size
    
    for r in range(n):
        for c in range(n):
            if board[r][c] == 0: 
                current_len = len(domains[r][c])
                if current_len == 0: return None 
                
                if current_len < min_len:
                    min_len = current_len
                    candidates = [(r, c)] 
                elif current_len == min_len:
                    candidates.append((r, c)) 
    
    if not candidates: return None
    if len(candidates) == 1: return candidates[0]
    
    best_candidate = candidates[0]
    max_degree = -1
    for (r, c) in candidates:
        deg = _count_unassigned_neighbors(board, n, box_size, r, c)
        if deg > max_degree:
            max_degree = deg
            best_candidate = (r, c)
    return best_candidate

def _solve_fc_recursive_mrv_visual(board_wrapper: SudokuBoard, stats: dict, domains: list):
    empty_cell = _find_cell_with_mrv(board_wrapper, domains)

    if not empty_cell:
        if board_wrapper.find_empty_cell() is None:
            yield {"status": "solved", "stats": stats}
            return True
        else:
            return False 

    row, col = empty_cell
    domain_to_try = list(domains[row][col]) 
    
    for num in domain_to_try:
        board_wrapper.set_cell(row, col, num)
        
        yield {"action": "try", "cell": (row, col), "num": num, "status": "running", "stats": stats}

        is_consistent, pruned_log = yield from _prune_neighbors_visual(domains, row, col, num, board_wrapper, stats)
        
        if is_consistent:
            result = yield from _solve_fc_recursive_mrv_visual(board_wrapper, stats, domains)
            if result: return True 

        stats["backtracks"] = stats.get("backtracks", 0) + 1
        yield from _restore_neighbors_visual(domains, pruned_log, stats)
        board_wrapper.set_cell(row, col, 0)
        
        yield {"action": "backtrack", "cell": (row, col), "stats": stats, "status": "running"}
    
    return False 

def _prune_neighbors_visual(domains, r, c, num, board_wrapper, stats):
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
    
    yield {"action": "prune_start", "neighbors": list(neighbors), "status": "running", "stats": stats}

    for (nr, nc) in neighbors:
        if num in domains[nr][nc]:
            domains[nr][nc].remove(num)
            pruned_log.append((nr, nc, num))
            if not domains[nr][nc]:
                yield {"action": "prune_fail", "cell": (nr, nc), "status": "running", "stats": stats}
                return (False, pruned_log)
    return (True, pruned_log)

def _restore_neighbors_visual(domains, pruned_log, stats):
    yield {"action": "restore_start", "neighbors": [], "status": "running", "stats": stats}
    for (r, c, num) in pruned_log:
        domains[r][c].add(num)