from .sudoku_board import SudokuBoard
import copy 

def solve_backtracking(board_wrapper: SudokuBoard, stats: dict):
    # Tìm ô trống đầu tiên trên bàn cờ để bắt đầu điền thử
    empty_cell = board_wrapper.find_empty_cell()
    
    # Nếu không còn ô trống nào, tức là bàn cờ đã được giải xong hoàn toàn
    if not empty_cell:
        return True  
    
    row, col = empty_cell
    
    # Thử lần lượt các giá trị từ 1 đến N vào ô trống vừa tìm được
    for num in range(1, board_wrapper.n + 1):
        # Kiểm tra xem số này có vi phạm quy tắc hàng, cột hay khối không
        if board_wrapper.is_valid(num, row, col):
            # Nếu hợp lệ, tạm thời điền số này vào ô
            board_wrapper.set_cell(row, col, num)
            
            # Gọi đệ quy để tiếp tục giải các ô tiếp theo
            if solve_backtracking(board_wrapper, stats):
                return True  
            
            # Nếu nhánh đệ quy phía sau thất bại (gặp ngõ cụt), tăng biến đếm quay lui
            stats["backtracks"] = stats.get("backtracks", 0) + 1
            
            # Trả lại giá trị 0 (xóa số) để thử số khác ở vòng lặp tiếp theo
            board_wrapper.set_cell(row, col, 0)
            
    # Nếu đã thử hết các số mà không có số nào thỏa mãn, trả về False để kích hoạt quay lui ở bước trước
    return False

def solve_forward_checking(board_wrapper: SudokuBoard, stats: dict):
    try:
        # Trước khi giải, khởi tạo tập hợp các giá trị khả dĩ (domain) cho từng ô
        # và loại bỏ ngay những giá trị không hợp lệ dựa trên các số đã có sẵn
        domains = _initialize_domains(board_wrapper)
    except ValueError:
        # Nếu ngay từ đầu đề bài đã mâu thuẫn, trả về False
        return False 
        
    # Bắt đầu quá trình giải đệ quy với tập domains đã được chuẩn bị
    return _solve_fc_recursive(board_wrapper, stats, domains)

def _initialize_domains(board_wrapper):
    n = board_wrapper.n
    board = board_wrapper.get_board()
    
    # Tạo miền giá trị ban đầu là tất cả các số từ 1 đến N cho mọi ô
    full_domain = set(range(1, n + 1))
    domains = [[full_domain.copy() for _ in range(n)] for _ in range(n)]
    
    # Duyệt qua bàn cờ, nếu ô nào đã có số (đề bài), chốt domain của nó chỉ còn số đó
    # Đồng thời loại bỏ số đó khỏi domain của các ô hàng xóm (hàng, cột, khối)
    for r in range(n):
        for c in range(n):
            num = board[r][c]
            if num != 0:
                domains[r][c] = {num}
                # Thực hiện lan truyền ràng buộc ngay lập tức
                if not _prune_domains_on_setup(domains, r, c, num, board_wrapper):
                    raise ValueError("Invalid initial puzzle")
    return domains

def _prune_domains_on_setup(domains, r, c, num, board_wrapper):
    n = board_wrapper.n
    box_size = board_wrapper.box_size
    
    # Loại bỏ số 'num' khỏi domain của tất cả các ô trong cùng hàng
    for col in range(n):
        if col != c and num in domains[r][col]:
            domains[r][col].remove(num)
            # Nếu sau khi loại bỏ mà ô đó không còn giá trị nào để điền -> Mâu thuẫn
            if not domains[r][col]: return False

    # Loại bỏ số 'num' khỏi domain của tất cả các ô trong cùng cột
    for row in range(n):
        if row != r and num in domains[row][c]:
            domains[row][c].remove(num)
            if not domains[row][c]: return False

    # Loại bỏ số 'num' khỏi domain của tất cả các ô trong cùng khối (Box)
    box_r = (r // box_size) * box_size
    box_c = (c // box_size) * box_size
    for br in range(box_r, box_r + box_size):
        for bc in range(box_c, box_c + box_size):
            if (br, bc) != (r, c) and num in domains[br][bc]:
                domains[br][bc].remove(num)
                if not domains[br][bc]: return False
    return True

def _solve_fc_recursive(board_wrapper: SudokuBoard, stats: dict, domains: list):
    # Tìm ô trống tiếp theo để điền
    empty_cell = board_wrapper.find_empty_cell()
    if not empty_cell:
        return True
    row, col = empty_cell
    
    # Thay vì thử 1..N, chỉ thử các giá trị còn lại trong domain của ô này
    # vì các giá trị khác đã bị loại bỏ do vi phạm ràng buộc trước đó
    domain_to_try = list(domains[row][col]) 
    
    for num in domain_to_try:
        board_wrapper.set_cell(row, col, num)
        
        # Sau khi điền thử, thực hiện cắt tỉa (Forward Checking) các ô hàng xóm
        # Hàm trả về danh sách các thay đổi để có thể khôi phục nếu cần quay lui
        is_consistent, pruned_log = _prune_neighbors_domains(domains, row, col, num, board_wrapper)
        
        # Nếu việc cắt tỉa không gây ra mâu thuẫn (không làm rỗng domain nào)
        if is_consistent:
            # Tiếp tục đệ quy sâu hơn
            if _solve_fc_recursive(board_wrapper, stats, domains):
                return True

        # Nếu đi vào ngõ cụt, thực hiện quay lui
        stats["backtracks"] = stats.get("backtracks", 0) + 1
        
        # Khôi phục lại các giá trị đã bị cắt tỉa khỏi domain hàng xóm
        _restore_neighbors_domains(domains, pruned_log)
        
        # Xóa số vừa điền
        board_wrapper.set_cell(row, col, 0)
    
    return False

def _prune_neighbors_domains(domains, r, c, num, board_wrapper):
    pruned_log = [] 
    n = board_wrapper.n
    box_size = board_wrapper.box_size
    
    # Xác định tất cả các ô hàng xóm chịu ảnh hưởng (hàng, cột, khối)
    neighbors = set()
    for col in range(n): neighbors.add((r, col))
    for row in range(n): neighbors.add((row, c))
    box_r = (r // box_size) * box_size
    box_c = (c // box_size) * box_size
    for br in range(box_r, box_r + box_size):
        for bc in range(box_c, box_c + box_size):
            neighbors.add((br, bc))
    neighbors.remove((r, c))

    # Duyệt qua từng hàng xóm và loại bỏ số vừa điền khỏi domain của chúng
    for (nr, nc) in neighbors:
        if num in domains[nr][nc]:
            domains[nr][nc].remove(num)
            pruned_log.append((nr, nc, num)) # Ghi nhật ký để khôi phục sau này
            
            # Nếu domain của hàng xóm trở nên rỗng -> Phát hiện ngõ cụt sớm
            if not domains[nr][nc]: 
                return (False, pruned_log) 
    return (True, pruned_log) 

def _restore_neighbors_domains(domains, pruned_log):
    # Dựa vào nhật ký, thêm lại các giá trị vào domain của các ô tương ứng
    for (r, c, num) in pruned_log:
        domains[r][c].add(num)