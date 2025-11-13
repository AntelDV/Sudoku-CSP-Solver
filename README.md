# Ứng dụng Giải Sudoku bằng CSP

Đây là phần mềm giải Sudoku 9x9, ứng dụng mô hình **Bài toán Thỏa mãn Ràng buộc (Constraint Satisfaction Problem - CSP)** trong Trí tuệ Nhân tạo. Chương trình cho phép so sánh hiệu năng của nhiều thuật toán và trực quan hóa các bước giải.

## Tính năng chính

- **Mô hình hóa CSP:** Biểu diễn bài toán theo 3 thành phần: Biến, Miền giá trị, và Ràng buộc.
- **Các thuật toán giải:**
  - **Backtracking (Baseline):** Thuật toán quay lui cơ bản.
  - **Forward Checking (Cải tiến):** Cắt tỉa miền giá trị của các biến lân cận.
  - **Forward Checking + MRV (Nâng cao):** Cải tiến bằng heuristic _Minimum Remaining Values_.
- **Giao diện đồ họa:** Xây dựng bằng thư viện CustomTkinter.
- **Trực quan hóa (Demo):** Hiển thị trực quan từng bước "thử" (Try) và "quay lui" (Backtrack) của thuật toán.
- **Phân tích hiệu năng:**
  - **So sánh đơn lẻ:** So sánh 3 thuật toán trên 1 đề bài (Thời gian, Số bước lui, Số nút duyệt).
  - **Thực nghiệm hàng loạt:** Tự động chạy N đề bài từ file CSV, phân loại độ khó và vẽ biểu đồ so sánh.

## Công nghệ sử dụng

- **Ngôn ngữ:** Python 3.10+
- **Giao diện:** CustomTkinter
- **Phân tích & Biểu đồ:** Pandas, Matplotlib

## Hướng dẫn sử dụng

1.  **Cài đặt thư viện:**

    pip install -r requirements.txt

2.  **(Tùy chọn) Thêm dữ liệu:**

    - Đặt file `sudoku.csv` của bạn vào thư mục `/data`.
    - Tính năng này dùng cho "Lấy Đề" và "Thực nghiệm Hàng loạt".

3.  **Chạy ứng dụng:**

    python main.py
