from .sudoku_board import SudokuBoard

class DLXNode:
    """
    Đại diện cho một nút (số 1) trong ma trận thưa.
    Sử dụng danh sách liên kết đôi 4 chiều (Toroidal Doubly Linked List).
    """
    def __init__(self):
        self.left = self
        self.right = self
        self.up = self
        self.down = self
        
        self.column = None 
        self.row_data = None 

class DLXHeader(DLXNode):
    def __init__(self, name=""):
        super().__init__()
        self.size = 0      
        self.name = name   
        self.column = self 


class SudokuDLX:
    """
    Bộ giải Sudoku sử dụng thuật toán Dancing Links (Algorithm X).
    """
    def __init__(self, board_wrapper: SudokuBoard):
        self.wrapper = board_wrapper
        self.n = board_wrapper.n
        self.box_size = board_wrapper.box_size
        self.original_board = board_wrapper.get_board()
        

        self.head = DLXHeader("ROOT")
        
        self.solution = []     
        self.nodes_visited = 0  
        self.columns_list = []  


    def solve(self, stats: dict):

        # Biến đổi Sudoku thành bài toán Exact Cover (Ma trận 0-1)
        self._build_exact_cover_matrix()
        
        # Xử lý các số đề bài đã cho (Pre-cover)
        # Giúp giảm không gian tìm kiếm ngay từ đầu bằng cách loại bỏ các phương án mâu thuẫn.
        self._initialize_clues()
        
        # Đệ quy tìm lời giải
        if self._search(visualize=False):
            # Nếu tìm thấy: Tái tạo bàn cờ từ danh sách solution
            result_board = [row[:] for row in self.original_board]
            for node in self.solution:
                r, c, val = node.row_data
                result_board[r][c] = val
            
            # Cập nhật kết quả vào wrapper để Controller hiển thị
            for r in range(self.n):
                for c in range(self.n):
                    self.wrapper.set_cell(r, c, result_board[r][c])
            
            # Ghi nhận thống kê
            stats["nodes_visited"] = self.nodes_visited
            return True
        
        return False


    def solve_visual(self, wrapper, stats: dict):
        """
        Generator trả về từng bước chạy để vẽ lên giao diện.
        """
        self._build_exact_cover_matrix()
        self._initialize_clues() 
        
        yield from self._search_visual_generator(stats)


    def _initialize_clues(self):
       
        for r in range(self.n):
            for c in range(self.n):
                val = self.original_board[r][c]
                if val != 0:
                    # Tìm cột ràng buộc "Ô (r,c) phải có số"
                    # Index của cột này là: r * n + c
                    idx = r * self.n + c
                    col_header = self.columns_list[idx]
                    
                    # Duyệt dọc xuống để tìm Hàng (Row) chứa giá trị val đúng với đề bài
                    curr = col_header.down
                    target_row = None
                    
                    while curr != col_header:
                        if curr.row_data == (r, c, val):
                            target_row = curr
                            break
                        curr = curr.down
                    
                    # Nếu tìm thấy hàng đúng:
                    # Cover cột hiện tại
                    # Cover tất cả các cột khác mà hàng này thỏa mãn (Hàng, Cột, Khối)
                    if target_row:
                        self._cover(col_header)
                        r_node = target_row.right
                        while r_node != target_row:
                            self._cover(r_node.column)
                            r_node = r_node.right
                        
                        # Lưu vào lời giải (để sau này tái tạo nếu cần)
                        self.solution.append(target_row)

  
    def _search(self, visualize=False):
        # ĐK Dừng: Nếu Header trỏ về chính nó -> Hết cột -> Ma trận rỗng -> Đã phủ kín -> THÀNH CÔNG
        if self.head.right == self.head:
            return True
        
        self.nodes_visited += 1
        
        # Chọn cột tốt nhất (Heuristic: Cột có kích thước nhỏ nhất -> Dễ fail nhất)
        col = self._choose_column()
        
        # Cover cột này (Xóa cột và các hàng liên quan khỏi ma trận)
        self._cover(col)
        
        # Duyệt qua từng Hàng (Row) trong cột đó -> Đây là các phương án thử
        curr_row = col.down
        while curr_row != col:
            # Chọn phương án này -> Đẩy vào stack
            self.solution.append(curr_row)
            
            # Cover các cột khác mà hàng này cũng đi qua (Lan truyền ràng buộc)
            j = curr_row.right
            while j != curr_row:
                self._cover(j.column)
                j = j.right
            
            # Đệ quy xuống cấp sâu hơn
            if self._search(visualize):
                return True
            
            # Nếu thất bại -> BACKTRACK (Quay lui)
            # Uncover các cột theo thứ tự ngược lại (LIFO)
            self.solution.pop()
            j = curr_row.left
            while j != curr_row:
                self._uncover(j.column)
                j = j.left
            
            # Thử hàng tiếp theo
            curr_row = curr_row.down
            
        # Trả lại cột ban đầu nếu không tìm thấy lời giải ở nhánh này
        self._uncover(col)
        return False

    def _search_visual_generator(self, stats):
        if self.head.right == self.head:
            yield {"status": "solved", "stats": stats}
            return True

        self.nodes_visited += 1
        stats["nodes_visited"] = self.nodes_visited 

        col = self._choose_column()
        self._cover(col)
        
        curr_row = col.down
        while curr_row != col:
            self.solution.append(curr_row)
            r, c, val = curr_row.row_data
            
            # Chỉ báo hiệu nếu là ô trống (để tránh tô xanh ô đề bài)
            if self.original_board[r][c] == 0:
                self.wrapper.set_cell(r, c, val)
                yield {
                    "action": "try", 
                    "cell": (r, c), "num": val, 
                    "stats": stats, 
                    "status": "running"
                }

            j = curr_row.right
            while j != curr_row:
                self._cover(j.column)
                j = j.right
            
            # Đệ quy
            if (yield from self._search_visual_generator(stats)):
                return True
            
            # Backtrack
            self.solution.pop()
            j = curr_row.left
            while j != curr_row:
                self._uncover(j.column)
                j = j.left

            # Báo hiệu quay lui (Tô đỏ)
            if self.original_board[r][c] == 0:
                self.wrapper.set_cell(r, c, 0)
                stats["backtracks"] = stats.get("backtracks", 0) + 1
                yield {
                    "action": "backtrack", 
                    "cell": (r, c), 
                    "stats": stats, 
                    "status": "running"
                }
                
            curr_row = curr_row.down
            
        self._uncover(col)
        return False

 
    def _cover(self, col):

        #  Gỡ cột ra khỏi danh sách Header ngang
        col.right.left = col.left
        col.left.right = col.right
        
        # Duyệt xuống từng hàng của cột này
        i = col.down
        while i != col:
            # Duyệt ngang từng node của hàng đó -> Gỡ node ra khỏi cột dọc của nó
            j = i.right
            while j != i:
                j.down.up = j.up
                j.up.down = j.down
                j.column.size -= 1 
                j = j.right
            i = i.down

    def _uncover(self, col):

        i = col.up
        while i != col:
            j = i.left
            while j != i:
                j.column.size += 1
                j.down.up = j
                j.up.down = j
                j = j.left
            i = i.up
        
        # Nối lại cột vào danh sách Header
        col.right.left = col
        col.left.right = col

    def _choose_column(self):

        best_col = None
        min_size = float('inf')
        
        curr = self.head.right
        while curr != self.head:
            if curr.size < min_size:
                min_size = curr.size
                best_col = curr
            curr = curr.right
        return best_col

    def _build_exact_cover_matrix(self):
 
        # Reset lại cấu trúc
        self.head = DLXHeader("ROOT")
        self.columns_list = []
        
        # --- TẠO CỘT  ---
        # Có 4 loại ràng buộc cho mỗi ô Sudoku:
        # 1. Cell Constraint: Mỗi ô (r,c) phải chứa đúng 1 số.
        # 2. Row Constraint: Mỗi hàng r phải chứa số k đúng 1 lần.
        # 3. Col Constraint: Mỗi cột c phải chứa số k đúng 1 lần.
        # 4. Box Constraint: Mỗi khối b phải chứa số k đúng 1 lần.
        # Tổng cộng = N^2 * 4 cột.
        
        num_cols = self.n * self.n * 4
        prev = self.head
        
        for i in range(num_cols):
            col = DLXHeader(f"C{i}")
            # Liên kết đôi vòng tròn ngang
            col.left = prev
            prev.right = col
            col.right = self.head
            self.head.left = col
            prev = col
            self.columns_list.append(col) 

        # --- TẠO HÀNG ---
        # Mỗi nước đi "Điền số v vào ô (r,c)" tạo thành 1 hàng trong ma trận.
        # Hàng này sẽ có số 1 tại 4 cột ràng buộc tương ứng.
        
        for r in range(self.n):
            for c in range(self.n):
                val = self.original_board[r][c]
                
                # Nếu đề bài đã có số -> Chỉ tạo 1 hàng duy nhất cho số đó (Bắt buộc chọn)
                if val != 0:
                    self._add_row_node(r, c, val)
                else:
                    # Nếu ô trống -> Tạo N hàng cho các khả năng từ 1..N
                    for v in range(1, self.n + 1):
                        self._add_row_node(r, c, v)

    def _add_row_node(self, r, c, val):
        """Thêm một hàng vào ma trận, nối vào 4 cột ràng buộc."""
        
        # Tính toán Index của 4 cột ràng buộc
        
        # Cột 1: Ô (r,c) có 1 số
        # Index: 0 -> N^2 - 1
        idx1 = r * self.n + c 
        
        # Cột 2: Hàng r có số val
        # Index: N^2 -> 2*N^2 - 1
        idx2 = (self.n**2) + (r * self.n) + (val - 1)
        
        # Cột 3: Cột c có số val
        # Index: 2*N^2 -> 3*N^2 - 1
        idx3 = (2 * self.n**2) + (c * self.n) + (val - 1)
        
        # Cột 4: Box b có số val
        # Index: 3*N^2 -> 4*N^2 - 1
        b = (r // self.box_size) * self.box_size + (c // self.box_size)
        idx4 = (3 * self.n**2) + (b * self.n) + (val - 1)
        
        indices = [idx1, idx2, idx3, idx4]
        
        start_node = None
        prev_node = None
        
        # Tạo Node và Liên kết
        for idx in indices:
            col_header = self.columns_list[idx]
            new_node = DLXNode()
            new_node.column = col_header
            new_node.row_data = (r, c, val) 
            
            # Link Dọc (Vào cột)
            new_node.down = col_header     
            new_node.up = col_header.up     
            col_header.up.down = new_node  
            col_header.up = new_node        
            col_header.size += 1          
            
            # Link Ngang (Tạo thành hàng)
            if start_node is None:
                start_node = new_node
                start_node.left = new_node
                start_node.right = new_node
            else:
                new_node.left = prev_node
                new_node.right = start_node
                prev_node.right = new_node
                start_node.left = new_node
            
            prev_node = new_node