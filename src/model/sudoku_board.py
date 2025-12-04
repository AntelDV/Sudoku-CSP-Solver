import time 
import math

class SudokuBoard:

    def __init__(self, initial_board):
        """
        Khởi tạo bàn cờ với kích thước động.
        :param initial_board: Ma trận NxN (ví dụ 9x9, 16x16).
        """
        self.board = [row[:] for row in initial_board]
        self.n = len(initial_board) # Kích thước lưới (9, 16, 25...)
        self.box_size = int(math.isqrt(self.n)) # Kích thước khối (3, 4, 5...)
        
        self.start_time = 0
        self.execution_time = 0

    def get_board(self):
        return self.board

    def set_cell(self, row, col, value):
        self.board[row][col] = value

    def find_empty_cell(self):
        """Tìm ô trống (giá trị 0)."""
        for r in range(self.n):
            for c in range(self.n):
                if self.board[r][c] == 0:
                    return (r, c)
        return None 

    def is_valid(self, num, row, col):
        """Kiểm tra hợp lệ tổng quát cho NxN."""
        # 1. Ràng buộc Hàng
        for c in range(self.n):
            if self.board[row][c] == num:
                return False

        # 2. Ràng buộc Cột
        for r in range(self.n):
            if self.board[r][col] == num:
                return False

        # 3. Ràng buộc Khối (Box)
        # Công thức tổng quát: (r // box_size) * box_size
        box_start_row = (row // self.box_size) * self.box_size
        box_start_col = (col // self.box_size) * self.box_size

        for r in range(box_start_row, box_start_row + self.box_size):
            for c in range(box_start_col, box_start_col + self.box_size):
                if self.board[r][c] == num:
                    return False

        return True

    def start_timer(self):
        self.start_time = time.perf_counter()
        self.execution_time = 0

    def stop_timer(self):
        if self.start_time != 0:
            self.execution_time = time.perf_counter() - self.start_time

    def get_stats(self):
        return {"execution_time_sec": self.execution_time}

    def __str__(self):
        return "\n".join([" ".join(map(str, row)) for row in self.board])