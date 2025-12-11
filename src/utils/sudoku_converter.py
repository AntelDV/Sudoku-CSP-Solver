
class SudokuConverter:

    @staticmethod
    def int_to_char(value: int) -> str:
        """
        Chuyển số nguyên (Model) sang ký tự (View).
        Ví dụ: 1 -> '1', 10 -> 'A'
        """
        if value == 0:
            return ""
        if 1 <= value <= 9:
            return str(value)
        else:
            # 10 -> A (65), 11 -> B (66)...
            # ord('A') = 65. Công thức: 65 + (value - 10)
            return chr(ord('A') + value - 10)

    @staticmethod
    def char_to_int(char: str) -> int:
        """
        Chuyển ký tự (View) sang số nguyên (Model).
        Ví dụ: '1' -> 1, 'A' -> 10, 'a' -> 10
        """
        if not char:
            return 0
        
        char = char.upper() # Chấp nhận cả chữ thường
        
        if char.isdigit():
            return int(char)
        elif 'A' <= char <= 'Z':
            # 'A' (65) -> 10. Công thức: ord - 55
            return ord(char) - 55
        else:
            return 0 # Ký tự rác không hợp lệ

    @staticmethod
    def is_valid_input(char: str) -> bool:
        """
        Kiểm tra xem ký tự nhập vào từ bàn phím có hợp lệ không.
        Chỉ cho phép: Số (0-9) hoặc Chữ cái (A-Z).
        """
        if not char: return True # Cho phép xóa trắng (chuỗi rỗng)
        if len(char) > 1: return False # Mỗi ô Sudoku chỉ chứa 1 ký tự
        
        char = char.upper()
        return char.isdigit() or ('A' <= char <= 'Z')