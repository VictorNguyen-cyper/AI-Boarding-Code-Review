# Tier 3 review — notes-PRACTICE

- Model: 3.1 Pro, with "Extended thinking" on
- Run date: 2026-10-07
- Output language: vi
- Requirements file: requirements-notes-PRACTICE.md
- Code files sent: 2
- Time waiting for Gemini's answer: not timed

> The result below is AI-generated and has not yet been classified true/false by a human.

<!-- Paste Gemini's answer verbatim below this line. Do not edit it, and do not re-run to get a different result. -->
<!-- Copied from the Gemini page text on 2026-10-07; table markup rebuilt and the "TXT" source chips removed. Wording unchanged. -->

## Tổng quan theo tiêu chí

| Mã | Câu trả lời (Yes / No / Insufficient information) | Phát hiện |
| --- | --- | --- |
| C01 | Yes | 1 phát hiện |
| C02 | No | Không có phát hiện |
| C03 | Yes | Không có phát hiện |
| C04 | Yes | Không có phát hiện |
| C05 | Yes | Không có phát hiện |
| C06 | Yes | Không có phát hiện |
| C07 | Yes | Không có phát hiện |
| C08 | Insufficient information | Thiếu thông tin giao diện |
| C09 | Yes | 1 phát hiện |
| C10 | Insufficient information | Thiếu thông tin giao diện |
| C11 | Yes | Không có phát hiện |
| C12 | No | Không có phát hiện |

## Các phát hiện

- Criterion: C01
  Location: practice/app/app.py:16
  Severity: High
  Description: Biến TOKENS chứa các mã thông báo (token) kiểm thử được gán cứng trực tiếp trong mã nguồn thay vì được đọc từ các biến môi trường.

- Criterion: C09
  Location: practice/app/app.py:create_note
  Severity: Low
  Description: Hàm xử lý không có cơ chế khóa lũy đẳng (idempotency key) và cơ sở dữ liệu không có ràng buộc duy nhất (unique constraint), cho phép tạo ra các bản ghi trùng lặp nếu người dùng gửi yêu cầu nhiều lần.

## Các câu hỏi mở

- Cần cung cấp mã nguồn của phần giao diện người dùng (frontend/UI) để kiểm tra xem hệ thống có nhánh xử lý hiển thị riêng biệt nào dành cho trạng thái danh sách trống hay không (liên quan đến tiêu chí C08).
- Cần có mã nguồn giao diện người dùng (frontend/UI) để xác minh xem khi gặp phản hồi lỗi 401 do hết hạn phiên, hệ thống có điều hướng người dùng về trang đăng nhập một cách rõ ràng thay vì hiển thị lỗi khó hiểu hay không (liên quan đến tiêu chí C10).
