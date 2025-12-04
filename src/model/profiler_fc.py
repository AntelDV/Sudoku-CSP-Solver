from .sudoku_board import SudokuBoard

def solve_forward_checking_profile(board_wrapper: SudokuBoard, stats: dict):
    """
    Thuật toán Forward Checking có đo hiệu năng (đếm số lần cắt tỉa).
    """
    if "nodes_visited" not in stats: stats["nodes_visited"] = 0
    if "prunes_made" not in stats: stats["prunes_made"] = 0
        
    try:
        # Khởi tạo miền giá trị và cắt tỉa ban đầu
        domains = _initialize_domains(board_wrapper, stats)
    except ValueError:
        return False 

    return _solve_fc_recursive(board_wrapper, stats, domains)

def _initialize_domains(board_wrapper, stats):
    """
    Tạo miền giá trị {1..N} cho mọi ô và loại bỏ các số đã có sẵn khỏi miền giá trị của hàng xóm.
    """
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
    """Cắt tỉa số đã điền khỏi miền giá trị của Hàng, Cột và Khối."""
    n = board_wrapper.n
    box_size = board_wrapper.box_size
    
    # Cắt tỉa Hàng
    for col in range(n):
        if col != c and num in domains[r][col]:
            domains[r][col].remove(num)
            stats["prunes_made"] += 1 
            if not domains[r][col]: return False 

    # Cắt tỉa Cột
    for row in range(n):
        if row != r and num in domains[row][c]:
            domains[row][c].remove(num)
            stats["prunes_made"] += 1 
            if not domains[row][c]: return False

    # Cắt tỉa Khối
    box_r = (r // box_size) * box_size
    box_c = (c // box_size) * box_size
    for br in range(box_r, box_r + box_size):
        for bc in range(box_c, box_c + box_size):
            if (br, bc) != (r, c) and num in domains[br][bc]:
                domains[br][bc].remove(num)
                stats["prunes_made"] += 1 
                if not domains[br][bc]: return False
    return True

def _solve_fc_recursive(board_wrapper: SudokuBoard, stats: dict, domains: list):
    """
    Quy trình Forward Checking:
    1. Tìm ô trống.
    2. Thử các giá trị trong domain của ô đó.
    3. Điền số -> Cắt tỉa domain hàng xóm.
    4. Nếu cắt tỉa ổn -> Đệ quy.
    5. Nếu thất bại -> Khôi phục domain (Undo cắt tỉa) và Quay lui.
    """
    stats["nodes_visited"] += 1
    
    empty_cell = board_wrapper.find_empty_cell()
    if not empty_cell:
        return True 

    row, col = empty_cell
    domain_to_try = list(domains[row][col]) 
    
    for num in domain_to_try:
        board_wrapper.set_cell(row, col, num)
        
        # Cắt tỉa (Forward Checking)
        is_consistent, pruned_log = _prune_neighbors_domains(domains, row, col, num, stats, board_wrapper)
        
        if is_consistent:
            if _solve_fc_recursive(board_wrapper, stats, domains):
                return True 

        # Quay lui và Khôi phục
        stats["backtracks"] = stats.get("backtracks", 0) + 1
        _restore_neighbors_domains(domains, pruned_log)
        board_wrapper.set_cell(row, col, 0)
    
    return False

def _prune_neighbors_domains(domains, r, c, num, stats, board_wrapper):
    """Loại bỏ số vừa điền khỏi miền giá trị các ô liên quan."""
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
    """Hoàn tác việc cắt tỉa (trả lại giá trị vào domain)."""
    for (r, c, num) in pruned_log:
        domains[r][c].add(num)