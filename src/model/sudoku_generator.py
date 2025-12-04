import random
import copy
from .sudoku_board import SudokuBoard
from .algorithms import solve_backtracking  # Dùng solver để tạo full solution

class SudokuGenerator:
    def __init__(self, size=9):
        self.n = size
        self.box_size = int(size ** 0.5)

    def generate_puzzle(self, difficulty='easy'):
        """
        Tạo một đề Sudoku mới.
        :param difficulty: 'easy', 'medium', 'hard', 'extreme'
        :return: (puzzle_grid, solution_grid)
        """
        # 1. Tạo bảng trống
        board = [[0] * self.n for _ in range(self.n)]
        board_wrapper = SudokuBoard(board)

        # 2. Điền ngẫu nhiên các khối chéo (Diagonal Boxes)
        # Các khối này độc lập nhau nên điền random an toàn
        for i in range(0, self.n, self.box_size):
            self._fill_box(board_wrapper, i, i)

        # 3. Giải để có Full Solution
        stats = {"backtracks": 0}
        solve_backtracking(board_wrapper, stats)
        full_solution = copy.deepcopy(board_wrapper.get_board())

        # 4. Đục lỗ (Xóa bớt số) để tạo đề
        puzzle = copy.deepcopy(full_solution)
        self._remove_digits(puzzle, difficulty)

        return puzzle, full_solution

    def _fill_box(self, board_wrapper, row_start, col_start):
        num_pool = list(range(1, self.n + 1))
        random.shuffle(num_pool) # Trộn số ngẫu nhiên
        
        idx = 0
        for r in range(row_start, row_start + self.box_size):
            for c in range(col_start, col_start + self.box_size):
                board_wrapper.set_cell(r, c, num_pool[idx])
                idx += 1

    def _remove_digits(self, grid, difficulty):
        # Xác định số lượng ô cần xóa dựa trên độ khó và kích thước
        total_cells = self.n * self.n
        
        # Tỷ lệ xóa (ước lượng)
        if difficulty == 'easy': remove_count = int(total_cells * 0.4)     # Giữ lại ~60%
        elif difficulty == 'medium': remove_count = int(total_cells * 0.5) # Giữ lại ~50%
        elif difficulty == 'hard': remove_count = int(total_cells * 0.6)   # Giữ lại ~40%
        else: remove_count = int(total_cells * 0.7)                        # Giữ lại ~30% (Extreme)

        attempts = remove_count
        while attempts > 0:
            r = random.randint(0, self.n - 1)
            c = random.randint(0, self.n - 1)
            
            if grid[r][c] != 0:
                grid[r][c] = 0
                attempts -= 1