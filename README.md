# Ứng dụng Giải Sudoku & Game (CSP Solver)

Đây là phần mềm giải Sudoku đa năng, ứng dụng mô hình **Bài toán Thỏa mãn Ràng buộc (Constraint Satisfaction Problem - CSP)** trong Trí tuệ Nhân tạo. Chương trình không chỉ là công cụ mô phỏng thuật toán mà còn là một trò chơi Sudoku hoàn chỉnh hỗ trợ nhiều kích thước bàn cờ.

## Tính năng chính

### 1. Đa dạng Kích thước & Dữ liệu

Hỗ trợ 4 loại kích thước bàn cờ:

- **4x4 (Mini):** Dành cho người mới bắt đầu.
- **9x9 (Tiêu chuẩn):** Kích thước phổ biến nhất.
- **16x16 (Hexadoku):** Thử thách nâng cao.
- **25x25 (Siêu Lớn):** Thử thách cực đại.

**Nguồn dữ liệu:**

- **9x9:** Nạp từ kho dữ liệu CSV (Kaggle dataset).
- **4x4, 16x16, 25x25:** Tự động sinh đề (Generator) vô tận với độ khó tùy chọn.

### 2. Các Chế độ Sử dụng

Chương trình cung cấp 2 chế độ riêng biệt:

#### 🤖 Chế độ Máy Giải (Solver Mode)

Dành cho việc học tập và nghiên cứu thuật toán:

- **Các thuật toán hỗ trợ:**
  - **Backtracking (Baseline):** Vét cạn quay lui cơ bản.
  - **Forward Checking:** Cắt tỉa miền giá trị của các ô lân cận.
  - **FC + MRV (Tối ưu):** Kết hợp Forward Checking với chiến lược chọn biến _Minimum Remaining Values_ (Ưu tiên ô ít lựa chọn nhất).
- **Trực quan hóa (Demo):** Xem máy giải từng bước (tô màu xanh khi thử, đỏ khi quay lui).
- **So sánh Hiệu năng:** Chạy đua 3 thuật toán cùng lúc để so sánh thời gian, số bước quay lui và số nút đã duyệt.

#### 👤 Chế độ Người Chơi (Play Mode)

Biến ứng dụng thành game Sudoku thực thụ:

- **Giao diện chơi:** Các ô đề bài được khóa, chỉ nhập vào ô trống.
- **Hỗ trợ nhập liệu:** Bàn phím số ảo (Numpad) hoặc bàn phím máy tính.
- **Kiểm tra lỗi tức thì:** Tự động báo viền đỏ nếu nhập số sai luật (trùng hàng/cột/khối).
- **Kiểm tra đáp án (Check):** So sánh bài làm với lời giải chuẩn, báo lỗi các ô sai.

## Công nghệ sử dụng

- **Ngôn ngữ:** Python 3.10+
- **Giao diện (GUI):** CustomTkinter (Giao diện hiện đại, Dark mode).
- **Xử lý dữ liệu:** Pandas.
- **Kỹ thuật AI:** Backtracking, Constraint Propagation, Heuristics (MRV).

## Hướng dẫn cài đặt & Sử dụng

1.  **Cài đặt thư viện:**
    Mở terminal và chạy lệnh:

    pip install -r requirements.txt

2.  **Chuẩn bị dữ liệu (Tùy chọn cho 9x9):**

    - Đặt file `sudoku.csv` vào thư mục `/data` nếu muốn dùng tính năng "Lấy Đề" cho size 9x9.
    - Với các size khác, chương trình tự sinh đề nên không cần file.

3.  **Chạy ứng dụng:**

    python main.py

## Cấu trúc thư mục

- `src/model`: Chứa logic thuật toán (Backtracking, FC, MRV), bộ sinh đề (Generator) và cấu trúc bàn cờ.
- `src/view`: Chứa mã nguồn giao diện (Main Window, Popup so sánh).
- `src/controller`: Điều phối luồng hoạt động giữa giao diện và thuật toán.
- `data/`: Thư mục chứa file dữ liệu CSV/TXT.
