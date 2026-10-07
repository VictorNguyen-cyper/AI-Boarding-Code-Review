# Bảng đối chiếu — DEMO (1 tính năng, ứng dụng giả lập)

> DEMO — không phải dữ liệu nghiên cứu. Cột "Kiểm tra bằng mắt" là giả định demo (luồng chính chạy đúng).

| # | Vấn đề | Tiêu chí | Mức | Mắt | Tầng 1 — quét | Tầng 2 — kiểm thử | Tầng 3 — rà soát |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | SECRET_KEY gán cứng | C01 | Cao | — | ✓ semgrep | — | ✓ |
| 2 | Khoá API vận chuyển trong mã | C01 | Cao | — | ✓ gitleaks | — | ✓ |
| 3 | Xem được đơn của người khác khi sửa ID | C03, C04 | Cao | — | — | ✓ TC-21 | ✓ |
| 4 | Lỗi trả nguyên văn + URL nội bộ | C02 | TB | — | — | ✓ TC-31 | ✓ |
| 5 | Không kiểm tra dữ liệu gửi lên | C05 | TB | — | — | ✓ TC-22, TC-23 | ✓ |
| 6 | Tỷ lệ tính cả đơn đã xoá | C06 | TB | — | — | ✓ TC-04 | ✓ |
| 7 | Chia cho 0 khi chưa có đơn | C07 | TB | — | — | ✓ TC-12 | ✓ |
| 8 | Bấm hai lần tạo hai đơn | C09 | TB | — | — | ✓ TC-41 | ✓ |
| 9 | Thiếu / sai token trả 500 thay vì 401 | C10 | TB | — | — | ✓ TC-51, TC-52 | ✓ |
| 10 | Gọi dịch vụ ngoài không có timeout | C11 | Thấp | — | ~ cảnh báo khác cùng dòng | ✓ TC-32 | ✓ |
| 11 | Truy vấn lặp theo từng đơn (N+1) | C12 | Thấp | — | — | — (dữ liệu nhỏ) | ✓ |
| | **Tổng** | | | **0/11** | **2/11** | **9/11** | **11/11** |

Phát hiện của Tầng 1 chưa khớp vấn đề nào ở trên: semgrep dynamic-urllib-use-detected (app.py:90) — chưa phân loại, để con người quyết định (quy tắc A.1). trivy: 0 phát hiện với Flask 3.1.3 / Werkzeug 3.1.9.
