from .sudoku_board import SudokuBoard
import copy 

# --- Thuật toán Backtracking (Giữ nguyên) ---
def solve_backtracking(board_wrapper: SudokuBoard, stats: dict):
    empty_cell = board_wrapper.find_empty_cell()
    if not empty_cell:
        return True  
    row, col = empty_cell
    for num in range(1, 10):
        if board_wrapper.is_valid(num, row, col):
            board_wrapper.set_cell(row, col, num)
            if solve_backtracking(board_wrapper, stats):
                return True  
            stats["backtracks"] += 1
            board_wrapper.set_cell(row, col, 0)
    return False

# --- BẮT ĐẦU LOGIC FORWARD CHECKING + MRV ---

def solve_forward_checking_mrv(board_wrapper: SudokuBoard, stats: dict):
    """
    Hàm "public" để khởi chạy thuật toán Forward Checking + MRV.
    """
    try:
        domains = _initialize_domains(board_wrapper.get_board())
    except ValueError:
        return False 
    return _solve_fc_recursive_mrv(board_wrapper, stats, domains)

def _initialize_domains(board):
    """
    Tạo và tiền xử lý (pre-prune) các miền giá trị dựa trên đề bài.
    (Giống hệt file algorithms.py)
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
    """(Giống hệt file algorithms.py)"""
    for col in range(9):
        if col != c and num in domains[r][col]:
            domains[r][col].remove(num)
            if not domains[r][col]: return False 
    for row in range(9):
        if row != r and num in domains[row][c]:
            domains[row][c].remove(num)
            if not domains[row][c]: return False
    box_r, box_c = (r // 3) * 3, (c // 3) * 3
    for br in range(box_r, box_r + 3):
        for bc in range(box_c, box_c + 3):
            if (br, bc) != (r, c) and num in domains[br][bc]:
                domains[br][bc].remove(num)
                if not domains[br][bc]: return False
    return True

# --- HÀM MỚI (CỐT LÕI CỦA MRV) ---
def _find_cell_with_mrv(board_wrapper: SudokuBoard, domains: list):
    """
    Tìm ô trống (giá trị 0) có miền giá trị (domain) nhỏ nhất.
    """
    min_len = 10 # Bắt đầu với số lớn hơn 9
    best_cell = None
    board = board_wrapper.get_board()
    
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0: # Nếu là ô trống
                current_len = len(domains[r][c])
                
                if current_len == 0: # Tối ưu: Phát hiện ngõ cụt ngay lập tức
                    return None # Không còn ô nào để chọn (vì domain rỗng)
                
                if current_len < min_len:
                    min_len = current_len
                    best_cell = (r, c)
                    
                    if min_len == 1: # Tối ưu: Không thể nhỏ hơn 1
                        return best_cell
                        
    return best_cell # Trả về ô có domain nhỏ nhất

# --- HÀM ĐỆ QUY ĐÃ SỬA ĐỔI ---
def _solve_fc_recursive_mrv(board_wrapper: SudokuBoard, stats: dict, domains: list):
    """
    Hàm đệ quy chính cho Forward Checking, sử dụng MRV.
    """
    # 1. TÌM Ô TRỐNG BẰNG MRV (THAY ĐỔI CHÍNH)
    empty_cell = _find_cell_with_mrv(board_wrapper, domains)
    
    if not empty_cell:
        # Nếu _find_cell_with_mrv trả về None VÀ BẢNG CHƯA ĐẦY
        # -> nghĩa là có ô trống nhưng domain rỗng -> NGÕ CỤT
        # Nếu bảng đã đầy -> GIẢI XONG
        if board_wrapper.find_empty_cell() is None:
             return True # Đã giải xong
        else:
             return False # Ngõ cụt do MRV phát hiện
        
    row, col = empty_cell

    # 2. Lặp qua MIỀN GIÁ TRỊ (đã được cắt tỉa)
    domain_to_try = list(domains[row][col]) 
    
    for num in domain_to_try:
        # 3. Gán giá trị
        board_wrapper.set_cell(row, col, num)
        
        # 4. Cắt tỉa hàng xóm (Logic này đã được sửa đúng ở lần trước)
        is_consistent, pruned_log = _prune_neighbors_domains(domains, row, col, num)
        
        # 5. Kiểm tra kết quả cắt tỉa
        if is_consistent:
            if _solve_fc_recursive_mrv(board_wrapper, stats, domains):
                return True 

        # 6. (BACKTRACK)
        stats["backtracks"] += 1
        _restore_neighbors_domains(domains, pruned_log)
        board_wrapper.set_cell(row, col, 0)
    
    # 7. Nếu lặp hết domain của ô này
    return False

# --- CÁC HÀM HỖ TRỢ (Giống hệt file algorithms.py) ---
def _prune_neighbors_domains(domains, r, c, num):
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
            pruned_log.append((nr, nc, num))
            if not domains[nr][nc]: 
                return (False, pruned_log) 
                    
    return (True, pruned_log) 

def _restore_neighbors_domains(domains, pruned_log):
    for (r, c, num) in pruned_log:
        domains[r][c].add(num)