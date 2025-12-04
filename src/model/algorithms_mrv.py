from .sudoku_board import SudokuBoard

def solve_forward_checking_mrv(board_wrapper: SudokuBoard, stats: dict):
    """
    Hàm khởi chạy thuật toán Forward Checking kết hợp MRV (Minimum Remaining Values).
    
    Quy trình tổng quát:
    1. Khởi tạo miền giá trị (Domain) cho tất cả các ô trống.
    2. Thực hiện cắt tỉa ban đầu dựa trên các số đề bài đã cho.
    3. Gọi hàm đệ quy để giải quyết bài toán.
    """
    try:
        # Khởi tạo và cắt tỉa domain ban đầu
        domains = _initialize_domains(board_wrapper)
    except ValueError:
        # Nếu đề bài ban đầu đã vi phạm luật chơi -> Trả về False
        return False
        
    # Bắt đầu quá trình giải đệ quy
    return _solve_fc_recursive_mrv(board_wrapper, stats, domains)

def _initialize_domains(board_wrapper):
    """
    Khởi tạo miền giá trị {1..N} cho mọi ô và loại bỏ các giá trị không hợp lệ
    dựa trên các số đã có sẵn trên bàn cờ.
    """
    n = board_wrapper.n
    board = board_wrapper.get_board()
    
    # Tạo domain đầy đủ ban đầu cho tất cả các ô
    full_domain = set(range(1, n + 1))
    domains = [[full_domain.copy() for _ in range(n)] for _ in range(n)]
    
    # Duyệt qua các ô đã có số (đề bài)
    for r in range(n):
        for c in range(n):
            num = board[r][c]
            if num != 0:
                # Nếu ô đã có số, domain của nó chỉ còn chính số đó
                domains[r][c] = {num}
                
                # Cắt tỉa số này khỏi domain của các ô hàng xóm (Hàng, Cột, Khối)
                if not _prune_domains_on_setup(domains, r, c, num, board_wrapper):
                    raise ValueError("Invalid initial puzzle")
    return domains

def _prune_domains_on_setup(domains, r, c, num, board_wrapper):
    """
    Hàm cắt tỉa dùng riêng cho bước khởi tạo.
    Nhiệm vụ: Loại bỏ số 'num' khỏi miền giá trị của tất cả các ô liên quan (Hàng, Cột, Khối).
    """
    n = board_wrapper.n
    box_size = board_wrapper.box_size
    
    # 1. Cắt tỉa trên Hàng
    for col in range(n):
        if col != c and num in domains[r][col]:
            domains[r][col].remove(num)
            if not domains[r][col]: return False # Mâu thuẫn: Ô hàng xóm hết giá trị để điền

    # 2. Cắt tỉa trên Cột
    for row in range(n):
        if row != r and num in domains[row][c]:
            domains[row][c].remove(num)
            if not domains[row][c]: return False
            
    # 3. Cắt tỉa trong Khối (Box)
    box_r = (r // box_size) * box_size
    box_c = (c // box_size) * box_size
    for br in range(box_r, box_r + box_size):
        for bc in range(box_c, box_c + box_size):
            if (br, bc) != (r, c) and num in domains[br][bc]:
                domains[br][bc].remove(num)
                if not domains[br][bc]: return False
    return True

def _find_cell_with_mrv(board_wrapper: SudokuBoard, domains: list):
    """
    Chiến lược chọn biến MRV (Minimum Remaining Values).
    
    Thay vì chọn ô trống đầu tiên tìm thấy, hàm này sẽ:
    1. Quét toàn bộ bàn cờ.
    2. Tìm ô trống có miền giá trị (domain) NHỎ NHẤT (ít lựa chọn nhất).
    3. Ưu tiên giải ô này trước ("Fail-First" principle).
    """
    min_len = board_wrapper.n + 1 
    best_cell = None
    board = board_wrapper.get_board()
    n = board_wrapper.n
    
    for r in range(n):
        for c in range(n):
            if board[r][c] == 0: # Chỉ xét ô chưa điền
                current_len = len(domains[r][c])
                
                # Nếu gặp ô có domain rỗng -> Ngõ cụt chắc chắn -> Báo ngay
                if current_len == 0: return None 
                
                # Cập nhật ô tốt nhất nếu tìm thấy ô có domain nhỏ hơn
                if current_len < min_len:
                    min_len = current_len
                    best_cell = (r, c)
                    
                    # Tối ưu: Nếu domain chỉ còn 1 giá trị -> Chọn luôn vì không thể tốt hơn
                    if min_len == 1: return best_cell
    return best_cell

def _solve_fc_recursive_mrv(board_wrapper: SudokuBoard, stats: dict, domains: list):
    """
    Hàm đệ quy chính thực hiện FC + MRV.
    
    Quy trình hoạt động:
    1. Chọn ô trống tối ưu nhất bằng MRV.
    2. Nếu không còn ô trống -> Giải xong (Thành công).
    3. Lặp qua các giá trị trong domain của ô đó.
    4. Thử điền -> Cắt tỉa domain hàng xóm -> Gọi đệ quy.
    5. Nếu thất bại -> Khôi phục domain (Undo) -> Quay lui.
    """
    # Bước 1: Chọn ô cần điền bằng MRV
    empty_cell = _find_cell_with_mrv(board_wrapper, domains)
    
    if not empty_cell:
        # Nếu hàm tìm kiếm trả về None:
        # - Hoặc là bàn cờ đã đầy (Thành công).
        # - Hoặc là bàn cờ còn trống nhưng có ô bị rỗng domain (Thất bại).
        if board_wrapper.find_empty_cell() is None: return True 
        else: return False 
        
    row, col = empty_cell
    
    # Bước 2: Lấy danh sách các giá trị khả dĩ để thử
    domain_to_try = list(domains[row][col])
    
    for num in domain_to_try:
        # Bước 3: Gán giá trị thử
        board_wrapper.set_cell(row, col, num)
        
        # Bước 4: Lan truyền ràng buộc (Cắt tỉa domain hàng xóm)
        is_consistent, pruned_log = _prune_neighbors_domains(domains, row, col, num, board_wrapper)
        
        # Bước 5: Nếu cắt tỉa thành công (không gây mâu thuẫn), tiếp tục đệ quy
        if is_consistent:
            if _solve_fc_recursive_mrv(board_wrapper, stats, domains):
                return True 

        # Bước 6: Nếu đi vào ngõ cụt -> Quay lui (Backtrack)
        stats["backtracks"] = stats.get("backtracks", 0) + 1
        
        # Khôi phục lại các giá trị đã bị cắt tỉa
        _restore_neighbors_domains(domains, pruned_log)
        
        # Xóa số vừa điền khỏi bàn cờ
        board_wrapper.set_cell(row, col, 0)
    
    # Đã thử hết các giá trị trong domain mà không thành công
    return False

def _prune_neighbors_domains(domains, r, c, num, board_wrapper):
    """
    Thực hiện Forward Checking: Loại bỏ 'num' khỏi domain của hàng xóm.
    Trả về danh sách (log) các giá trị đã xóa để phục vụ việc khôi phục.
    """
    pruned_log = [] 
    n = board_wrapper.n
    box_size = board_wrapper.box_size
    neighbors = set()
    
    # Xác định các ô hàng xóm (Hàng, Cột, Khối)
    for col in range(n): neighbors.add((r, col))
    for row in range(n): neighbors.add((row, c))
    box_r = (r // box_size) * box_size
    box_c = (c // box_size) * box_size
    for br in range(box_r, box_r + box_size):
        for bc in range(box_c, box_c + box_size):
            neighbors.add((br, bc))
    neighbors.discard((r, c)) # Loại bỏ chính ô đang xét

    # Duyệt và cắt tỉa
    for (nr, nc) in neighbors:
        if num in domains[nr][nc]:
            domains[nr][nc].remove(num)
            pruned_log.append((nr, nc, num)) # Ghi nhật ký
            
            # Nếu domain hàng xóm trở nên rỗng -> Phát hiện mâu thuẫn ngay lập tức
            if not domains[nr][nc]: 
                return (False, pruned_log) 
    return (True, pruned_log) 

def _restore_neighbors_domains(domains, pruned_log):
    """
    Hoàn tác quá trình cắt tỉa: Trả lại các giá trị đã xóa vào domain tương ứng.
    """
    for (r, c, num) in pruned_log:
        domains[r][c].add(num)