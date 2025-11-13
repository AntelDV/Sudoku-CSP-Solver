from .sudoku_board import SudokuBoard

def _find_cell_with_mrv(board_wrapper: SudokuBoard, domains: list):
    """
    Tìm ô trống (giá trị 0) có miền giá trị (domain) nhỏ nhất.
    
    :param board_wrapper: Đối tượng SudokuBoard.
    :param domains: Cấu trúc miền giá trị.
    :return: (tuple) (r, c) của ô tốt nhất, hoặc None nếu không tìm thấy.
    """
    min_len = 10 
    best_cell = None
    board = board_wrapper.get_board()
    
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0: 
                current_len = len(domains[r][c])
                
                if current_len == 0: 
                    return None # Ngõ cụt
                
                if current_len < min_len:
                    min_len = current_len
                    best_cell = (r, c)
                    
                    if min_len == 1: 
                        return best_cell
                        
    return best_cell


def solve_forward_checking_mrv_profile(board_wrapper: SudokuBoard, stats: dict):
    """
    Hàm "public" để khởi chạy Forward Checking + MRV phiên bản Profiler.
    Đếm các số liệu: 'nodes_visited', 'prunes_made', 'backtracks'.
    
    :param board_wrapper: Đối tượng SudokuBoard.
    :param stats: Dictionary thống kê (sẽ được cập nhật).
    :return: (bool) True nếu tìm thấy lời giải.
    """
    
    if "nodes_visited" not in stats:
        stats["nodes_visited"] = 0
    if "prunes_made" not in stats:
        stats["prunes_made"] = 0
        
    try:
        # 1. Khởi tạo và cắt tỉa (pre-prune) miền giá trị
        domains = _initialize_domains(board_wrapper.get_board(), stats)
    except ValueError:
        return False # Đề bài gốc không hợp lệ

    # 2. Gọi hàm đệ quy chính
    return _solve_fc_recursive_mrv(board_wrapper, stats, domains)

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

def _solve_fc_recursive_mrv(board_wrapper: SudokuBoard, stats: dict, domains: list):
    """
    Hàm đệ quy chính cho Forward Checking + MRV (Profiler).
    
    :param board_wrapper: Đối tượng SudokuBoard.
    :param stats: Dictionary thống kê (sẽ được cập nhật).
    :param domains: Cấu trúc miền giá trị.
    :return: (bool) True nếu tìm thấy lời giải.
    """
    stats["nodes_visited"] += 1
    
    # 1. TÌM Ô TRỐNG BẰNG MRV (thay vì find_empty_cell)
    empty_cell = _find_cell_with_mrv(board_wrapper, domains)

    if not empty_cell:
        if board_wrapper.find_empty_cell() is None:
             return True # Đã giải xong
        else:
             return False # Ngõ cụt
        
    row, col = empty_cell
    
    # 2. Lặp qua miền giá trị của ô đã chọn
    domain_to_try = list(domains[row][col]) 
    
    for num in domain_to_try:
        # 3. Gán giá trị
        board_wrapper.set_cell(row, col, num)
        
        # 4. (FORWARD CHECKING) Cắt tỉa miền giá trị của hàng xóm
        is_consistent, pruned_log = _prune_neighbors_domains(domains, row, col, num, stats)
        
        # 5. Kiểm tra kết quả cắt tỉa
        if is_consistent:
            if _solve_fc_recursive_mrv(board_wrapper, stats, domains):
                return True 

        # 6. (BACKTRACK)
        stats["backtracks"] += 1
        _restore_neighbors_domains(domains, pruned_log)
        board_wrapper.set_cell(row, col, 0)
    
    # 7. Thử hết miền giá trị thất bại
    return False

def _prune_neighbors_domains(domains, r, c, num, stats):
    """Cắt tỉa 'num' khỏi miền giá trị của các hàng xóm."""
    pruned_log = [] 
    
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
            stats["prunes_made"] += 1 
            pruned_log.append((nr, nc, num))
            if not domains[nr][nc]: 
                return (False, pruned_log) 
                    
    return (True, pruned_log) 

def _restore_neighbors_domains(domains, pruned_log):
    """Khôi phục lại các miền giá trị từ log."""
    for (r, c, num) in pruned_log:
        domains[r][c].add(num)