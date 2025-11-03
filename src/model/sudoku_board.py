# Mô tả: Lớp này đóng vai trò là "Model" trong MVC.
#        Nó hiện thực hóa bài toán Sudoku theo lý thuyết CSP:
#        - Biến (Variables): 81 ô (self.board)
#        - Miền giá trị (Domain): {1-9}
#        - Ràng buộc (Constraints): Các hàm is_valid_...

import time  # Dùng để đo thời gian thực thi

class SudokuBoard:
    """
    Quản lý trạng thái và các ràng buộc của bàn cờ Sudoku 9x9.
    Đây là "API nội bộ" mà các thuật toán giải (Algorithms) sẽ sử dụng.
    """
    def __init__(self, initial_board):
        """
        Khởi tạo bàn cờ.
        :param initial_board: Một ma trận 9x9 (list[list[int]])
        """
        # Sao chép sâu (deep copy) để tránh tham chiếu đến đối tượng gốc
        self.board = [row[:] for row in initial_board]
        self.start_time = 0
        self.execution_time = 0

    def get_board(self):
        """Trả về trạng thái hiện tại của bàn cờ."""
        return self.board

    def set_cell(self, row, col, value):
        """Đặt giá trị cho một ô cụ thể."""
        self.board[row][col] = value

    def find_empty_cell(self):
        """
        Tìm ô trống (giá trị 0) tiếp theo để điền.
        :return: (tuple) (hàng, cột) hoặc None nếu không còn ô trống.
        """
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    return (r, c)
        return None  # Không còn ô trống, bàn cờ đã giải xong

    def is_valid(self, num, row, col):
        """
        Kiểm tra xem việc gán 'num' vào (row, col) có vi phạm
        bất kỳ ràng buộc nào (hàng, cột, khối 3x3) hay không.
        Đây là hàm kiểm tra Constraints cốt lõi.
        """
        # 1. Ràng buộc Hàng (Row Constraint)
        for c in range(9):
            if self.board[row][c] == num:
                return False

        # 2. Ràng buộc Cột (Column Constraint)
        for r in range(9):
            if self.board[r][col] == num:
                return False

        # 3. Ràng buộc Khối 3x3 (Box Constraint)
        # Tìm tọa độ bắt đầu của khối 3x3
        box_start_row = (row // 3) * 3
        box_start_col = (col // 3) * 3

        for r in range(box_start_row, box_start_row + 3):
            for c in range(box_start_col, box_start_col + 3):
                if self.board[r][c] == num:
                    return False

        # Nếu vượt qua cả 3 kiểm tra -> Hợp lệ
        return True

    def start_timer(self):
        """Bắt đầu đếm thời gian giải."""
        self.start_time = time.perf_counter()
        self.execution_time = 0

    def stop_timer(self):
        """Dừng đếm thời gian và lưu kết quả."""
        if self.start_time != 0:
            self.execution_time = time.perf_counter() - self.start_time

    def get_stats(self):
        """
        Trả về các thông số cơ bản.
        Sẽ được mở rộng bởi các thuật toán (ví dụ: đếm số bước quay lui).
        """
        return {
            "execution_time_sec": self.execution_time
        }

    def __str__(self):
        """Biểu diễn bàn cờ dưới dạng string (hữu ích cho việc test)."""
        s = ""
        for r in range(9):
            if r % 3 == 0 and r != 0:
                s += "- - - - - - - - - - -\n"
            for c in range(9):
                if c % 3 == 0 and c != 0:
                    s += "| "
                s += str(self.board[r][c]) + " "
            s += "\n"
        return s