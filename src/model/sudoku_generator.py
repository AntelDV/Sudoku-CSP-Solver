import random
import copy
from .sudoku_board import SudokuBoard
from .algorithms_mrv import solve_forward_checking_mrv 

class SudokuGenerator:
    def __init__(self, size=9):
        self.n = size
        self.box_size = int(size ** 0.5)

    def generate_puzzle(self, difficulty='easy'):
        """
        Quy trình tạo đề Sudoku (Tối ưu hóa):
        1. Tạo bảng trống.
        2. Điền ngẫu nhiên các khối chéo.
        3. Dùng FC + MRV để điền đầy bảng (nhanh gấp bội so với Backtracking thường).
        4. Đục lỗ theo độ khó.
        """
        # 1. Tạo bảng trống
        board = [[0] * self.n for _ in range(self.n)]
        board_wrapper = SudokuBoard(board)

        # 2. Điền các khối chéo (Diagonal Boxes)
        for i in range(0, self.n, self.box_size):
            self._fill_box(board_wrapper, i, i)

        # 3. Giải để có Full Solution (Dùng MRV để chạy nhanh với size 25x25)
        stats = {"backtracks": 0}
        
        # Nếu dùng Backtracking thường ở đây với 25x25 sẽ bị treo máy
        success = solve_forward_checking_mrv(board_wrapper, stats)
        
        if not success:
            # Trường hợp hiếm hoi random khối chéo gây mâu thuẫn -> Thử lại
            return self.generate_puzzle(difficulty)

        full_solution = copy.deepcopy(board_wrapper.get_board())

        # 4. Đục lỗ (Xóa số)
        puzzle = copy.deepcopy(full_solution)
        self._remove_digits(puzzle, difficulty)

        return puzzle, full_solution

    def _fill_box(self, board_wrapper, row_start, col_start):
        # Trộn ngẫu nhiên dãy số từ 1 đến N
        num_pool = list(range(1, self.n + 1))
        random.shuffle(num_pool)
        
        idx = 0
        for r in range(row_start, row_start + self.box_size):
            for c in range(col_start, col_start + self.box_size):
                board_wrapper.set_cell(r, c, num_pool[idx])
                idx += 1

    def _remove_digits(self, grid, difficulty):
        total_cells = self.n * self.n
        
        # Tỷ lệ giữ lại số (càng khó càng ít số)
        if difficulty == 'easy': remove_ratio = 0.4     
        elif difficulty == 'medium': remove_ratio = 0.5 
        elif difficulty == 'hard': remove_ratio = 0.6   
        else: remove_ratio = 0.7                        

        remove_count = int(total_cells * remove_ratio)
        attempts = remove_count
        
        while attempts > 0:
            r = random.randint(0, self.n - 1)
            c = random.randint(0, self.n - 1)
            
            # Nếu ô chưa bị xóa thì xóa nó
            if grid[r][c] != 0:
                grid[r][c] = 0
                attempts -= 1