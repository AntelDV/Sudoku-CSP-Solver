from .sudoku_board import SudokuBoard

def solve_forward_checking_visual(board_wrapper: SudokuBoard, stats: dict):
    try:
        domains = _initialize_domains(board_wrapper.get_board())
    except ValueError:
        yield {"status": "failed", "message": "Đề bài gốc không hợp lệ"}
        return False 

    yield from _solve_fc_recursive_visual(board_wrapper, stats, domains)

def _initialize_domains(board):
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
    empty_cell = board_wrapper.find_empty_cell()
    if not empty_cell:
        yield {"status": "solved"}
        return True  

    row, col = empty_cell
    domain_to_try = list(domains[row][col]) 
    
    for num in domain_to_try:
        
        board_wrapper.set_cell(row, col, num)
        
        yield {
            "action": "try",
            "cell": (row, col),
            "num": num,
            "status": "running"
        }

        is_consistent, pruned_log = yield from _prune_neighbors_visual(domains, row, col, num)
        
        if is_consistent:
            if (yield from _solve_fc_recursive_visual(board_wrapper, stats, domains)):
                return True 

        stats["backtracks"] += 1
        
        yield from _restore_neighbors_visual(domains, pruned_log)
        board_wrapper.set_cell(row, col, 0)
        
        yield {
            "action": "backtrack",
            "cell": (row, col),
            "stats": stats, 
            "status": "running"
        }
    
    return False 

def _prune_neighbors_visual(domains, r, c, num):
    pruned_log = [] 
    
    neighbors = set()
    for col in range(9): neighbors.add((r, col))
    for row in range(9): neighbors.add((row, c))
    box_r, box_c = (r // 3) * 3, (c // 3) * 3
    for br in range(box_r, box_r + 3):
        for bc in range(box_c, box_c + 3):
            neighbors.add((br, bc))
    neighbors.remove((r, c)) 

    yield {
        "action": "prune_start",
        "neighbors": list(neighbors),
        "status": "running"
    }

    for (nr, nc) in neighbors:
        if num in domains[nr][nc]:
            domains[nr][nc].remove(num)
            pruned_log.append((nr, nc, num))
            
            if not domains[nr][nc]:
                yield {
                    "action": "prune_fail", 
                    "cell": (nr, nc),
                    "status": "running"
                }
                return (False, pruned_log) 
                    
    return (True, pruned_log) 

def _restore_neighbors_visual(domains, pruned_log):
    restored_cells = set((r, c) for (r, c, num) in pruned_log)
    
    yield {
        "action": "restore_start",
        "neighbors": list(restored_cells),
        "status": "running"
    }
    
    for (r, c, num) in pruned_log:
        domains[r][c].add(num)