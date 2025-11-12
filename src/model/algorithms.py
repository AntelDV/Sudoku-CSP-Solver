
from .sudoku_board import SudokuBoard
import copy 


def solve_backtracking(board_wrapper: SudokuBoard, stats: dict):
    """
    Giải Sudoku bằng thuật toán Backtracking cơ bản (Baseline).
    Đây là hàm đệ quy.
    :param board_wrapper: Đối tượng SudokuBoard chứa bàn cờ.
    :param stats: Dictionary để theo dõi số liệu (ví dụ: số bước quay lui).
    :return: (bool) True nếu tìm thấy lời giải, False nếu không.
    """
    # 1. Tìm ô trống tiếp theo
    empty_cell = board_wrapper.find_empty_cell()

    if not empty_cell:
        return True  # Không còn ô trống, đã giải xong

    row, col = empty_cell

    # 2. Thử các giá trị từ 1 đến 9 (Miền giá trị)
    for num in range(1, 10):
        # 3. Kiểm tra ràng buộc
        if board_wrapper.is_valid(num, row, col):
            # 3.1. Gán giá trị nếu hợp lệ
            board_wrapper.set_cell(row, col, num)

            # 3.2. Gọi đệ quy
            if solve_backtracking(board_wrapper, stats):
                return True  # Tìm thấy lời giải, thoát khỏi đệ quy

            # 3.3. Nếu đệ quy trả về False -> Đây là một "NGÕ CỤT"
            # Cập nhật bộ đếm "Quay lui" (Backtrack)
            stats["backtracks"] += 1
            
            # Quay lui: Đặt lại giá trị ô về 0
            board_wrapper.set_cell(row, col, 0)

    # 4. Nếu thử hết 9 số mà không số nào hợp lệ
    return False  # Kích hoạt quay lui ở cấp đệ quy cao hơn


def solve_forward_checking(board_wrapper: SudokuBoard, stats: dict):
    """
    Hàm "public" để khởi chạy thuật toán Forward Checking.
    Hàm này sẽ khởi tạo miền giá trị (domains) và gọi hàm đệ quy.
    
    :param board_wrapper: Đối tượng SudokuBoard chứa bàn cờ.
    :param stats: Dictionary để theo dõi số liệu.
    :return: (bool) True nếu tìm thấy lời giải.
    """
    
    # 1. Khởi tạo cấu trúc dữ liệu "Miền giá trị" (Domains)
    # domains[r][c] = một set chứa các số {1..9} có thể điền vào ô (r, c)
    try:
        domains = _initialize_domains(board_wrapper.get_board())
    except ValueError:
        return False # Đề bài gốc đã vi phạm, không thể giải

    # 2. Gọi hàm đệ quy
    return _solve_fc_recursive(board_wrapper, stats, domains)

def _initialize_domains(board):
    """
    Tạo và tiền xử lý (pre-prune) các miền giá trị dựa trên đề bài.
    :param board: Ma trận 9x9.
    :return: Cấu trúc domains (list[list[set]]).
    :raises: ValueError nếu đề bài gốc không hợp lệ.
    """
    # Tạo 81 set, mỗi set chứa {1, 2, ..., 9}
    full_domain = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    domains = [[full_domain.copy() for _ in range(9)] for _ in range(9)]
    
    # Bắt đầu cắt tỉa dựa trên các số cho sẵn
    for r in range(9):
        for c in range(9):
            num = board[r][c]
            if num != 0:
                # Ô này đã được gán, miền của nó chỉ chứa chính nó
                domains[r][c] = {num}
                
                # Cắt tỉa 'num' khỏi tất cả "hàng xóm"
                # (Chúng ta không cần lưu log ở đây vì đây là bước setup)
                if not _prune_domains_on_setup(domains, r, c, num):
                    # Nếu việc setup thất bại -> đề bài vô lý
                    raise ValueError("Invalid initial puzzle")
    
    return domains

def _prune_domains_on_setup(domains, r, c, num):
    """Hàm cắt tỉa riêng cho bước khởi tạo (không cần log)."""
    # 1. Cắt tỉa hàng
    for col in range(9):
        if col != c and num in domains[r][col]:
            domains[r][col].remove(num)
            if not domains[r][col]: return False # Phát hiện ngõ cụt

    # 2. Cắt tỉa cột
    for row in range(9):
        if row != r and num in domains[row][c]:
            domains[row][c].remove(num)
            if not domains[row][c]: return False

    # 3. Cắt tỉa khối 3x3
    box_r, box_c = (r // 3) * 3, (c // 3) * 3
    for br in range(box_r, box_r + 3):
        for bc in range(box_c, box_c + 3):
            if (br, bc) != (r, c) and num in domains[br][bc]:
                domains[br][bc].remove(num)
                if not domains[br][bc]: return False
                
    return True # Cắt tỉa thành công

def _solve_fc_recursive(board_wrapper: SudokuBoard, stats: dict, domains: list):
    """
    Hàm đệ quy chính cho Forward Checking.
    """
    # 1. Tìm ô trống (giống Backtracking)
    empty_cell = board_wrapper.find_empty_cell()
    if not empty_cell:
        return True  # Đã giải xong

    row, col = empty_cell

    # 2. Lặp qua MIỀN GIÁ TRỊ (đã được cắt tỉa)
    # Đây là điểm khác biệt mấu chốt so với 'for num in range(1, 10)'
    # Chúng ta phải lặp trên 1 bản sao, vì domain[row][col] có thể bị
    # thay đổi bởi các lời gọi đệ quy sâu hơn (nếu là hàng xóm)
    
    # Tạo bản sao của domain[row][col] để lặp
    domain_to_try = list(domains[row][col]) 
    
    for num in domain_to_try:
        # 3. Gán giá trị
        board_wrapper.set_cell(row, col, num)
        
        # 4. (FORWARD CHECKING) Cắt tỉa miền giá trị của hàng xóm
        #    và ghi lại những gì đã cắt tỉa để khôi phục sau
        
        # (pruned_log) là một list các (r, c, num) đã bị xóa
        is_consistent, pruned_log = _prune_neighbors_domains(domains, row, col, num)
        
        # 5. Kiểm tra kết quả cắt tỉa
        if is_consistent:
            # Nếu cắt tỉa OK (không có domain nào rỗng) -> đi sâu hơn
            if _solve_fc_recursive(board_wrapper, stats, domains):
                return True # Tìm thấy lời giải!

        # 6. (BACKTRACK)
        # Nếu (is_consistent == False) -> ngõ cụt do FC phát hiện
        # Hoặc nếu lời gọi đệ quy thất bại
        
        stats["backtracks"] += 1
        
        # 6.1. Khôi phục lại các domain đã bị cắt tỉa
        _restore_neighbors_domains(domains, pruned_log)
        
        # 6.2. Đặt lại giá trị ô
        board_wrapper.set_cell(row, col, 0)
    
    # 7. Nếu lặp hết domain của ô này mà không tìm được lời giải
    return False

def _prune_neighbors_domains(domains, r, c, num):
    """
    Cắt tỉa 'num' khỏi miền giá trị của các hàng xóm (hàng, cột, khối)
    của ô (r, c).
    :return: (tuple) (bool: is_consistent, list: pruned_log)
             is_consistent: False nếu có bất kỳ domain hàng xóm nào rỗng.
             pruned_log: Danh sách các (r, c, num) đã bị xóa.
    """
    pruned_log = [] # Lưu lại những gì đã xóa
    
    # 1. Cắt tỉa hàng
    for col in range(9):
        if col != c and num in domains[r][col]:
            domains[r][col].remove(num)
            pruned_log.append((r, col, num))
            if not domains[r][col]: return (False, pruned_log) # Phát hiện ngõ cụt

    # 2. Cắt tỉa cột
    for row in range(9):
        if row != r and num in domains[row][c]:
            domains[row][c].remove(num)
            pruned_log.append((row, c, num))
            if not domains[row][c]: return (False, pruned_log)

    # 3. Cắt tỉa khối 3x3
    box_r, box_c = (r // 3) * 3, (c // 3) * 3
    for br in range(box_r, box_r + 3):
        for bc in range(box_c, box_c + 3):
            # Chỉ cắt tỉa nếu ô đó không phải là (r,c) VÀ
            # nó không nằm trong hàng r hoặc cột c (vì đã cắt tỉa ở trên)
            if (br, bc) != (r, c) and br != r and bc != c:
                if num in domains[br][bc]:
                    domains[br][bc].remove(num)
                    pruned_log.append((br, bc, num))
                    if not domains[br][bc]: return (False, pruned_log)
                    
    return (True, pruned_log) # Cắt tỉa thành công

def _restore_neighbors_domains(domains, pruned_log):
    """
    Khôi phục lại các miền giá trị từ log.
    Đây là thao tác ngược của _prune_neighbors_domains.
    """
    for (r, c, num) in pruned_log:
        domains[r][c].add(num)