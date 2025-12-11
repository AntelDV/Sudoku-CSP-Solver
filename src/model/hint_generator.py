from .sudoku_board import SudokuBoard
import random

class HintGenerator:

    @staticmethod
    def get_hint(current_board_data, known_solution=None):

        board_wrapper = SudokuBoard(current_board_data)
        n = board_wrapper.n
        
        # 1. Tính toán Domain (Miền giá trị khả dĩ) cho tất cả ô trống
        # Logic này vay mượn từ Forward Checking nhưng không chạy đệ quy
        domains = HintGenerator._get_all_domains(board_wrapper)
        
        # 2. CHIẾN LƯỢC 1: Tìm "Naked Single" (Ô chỉ còn đúng 1 khả năng)
        # Đây là gợi ý tốt nhất vì người chơi có thể tự suy luận được.
        for r in range(n):
            for c in range(n):
                if current_board_data[r][c] == 0:
                    possible_values = domains[r][c]
                    if len(possible_values) == 1:
                        val = list(possible_values)[0]
                        return (r, c, val, 'naked_single')

        # 3. CHIẾN LƯỢC 2: Fallback (Dùng đáp án chuẩn)
        # Nếu không có ô nào "dễ" (Naked Single), ta buộc phải hé lộ 1 ô
        # dựa trên lời giải chuẩn (known_solution) để người chơi không bị kẹt.
        if known_solution:
            # Ưu tiên chọn ô có ít lựa chọn nhất (MRV) để gợi ý có giá trị cao
            min_len = n + 1
            best_cell = None
            
            for r in range(n):
                for c in range(n):
                    if current_board_data[r][c] == 0:
                        domain_len = len(domains[r][c])
                        if 0 < domain_len < min_len:
                            min_len = domain_len
                            best_cell = (r, c)
            
            if best_cell:
                r, c = best_cell
                val = known_solution[r][c]
                return (r, c, val, 'fallback')
        
        return None

    @staticmethod
    def _get_all_domains(board_wrapper):
        """
        Khởi tạo và cắt tỉa domain cho toàn bộ bàn cờ.
        """
        n = board_wrapper.n
        board = board_wrapper.get_board()
        full_domain = set(range(1, n + 1))
        domains = [[full_domain.copy() for _ in range(n)] for _ in range(n)]
        
        # Loại bỏ các giá trị không hợp lệ dựa trên các số đã có
        for r in range(n):
            for c in range(n):
                num = board[r][c]
                if num != 0:
                    domains[r][c] = {num} # Ô đã điền thì domain là chính nó
                    # Lan truyền ràng buộc (Cắt tỉa hàng xóm)
                    HintGenerator._prune_neighbors(domains, r, c, num, board_wrapper)
        
        return domains

    @staticmethod
    def _prune_neighbors(domains, r, c, num, board_wrapper):
        """Loại bỏ 'num' khỏi domain của hàng, cột, khối liên quan."""
        n = board_wrapper.n
        box_size = board_wrapper.box_size
        
        # Cắt tỉa Hàng
        for col in range(n):
            if col != c and num in domains[r][col]:
                domains[r][col].discard(num)

        # Cắt tỉa Cột
        for row in range(n):
            if row != r and num in domains[row][c]:
                domains[row][c].discard(num)

        # Cắt tỉa Khối
        box_r = (r // box_size) * box_size
        box_c = (c // box_size) * box_size
        for br in range(box_r, box_r + box_size):
            for bc in range(box_c, box_c + box_size):
                if (br, bc) != (r, c) and num in domains[br][bc]:
                    domains[br][bc].discard(num)