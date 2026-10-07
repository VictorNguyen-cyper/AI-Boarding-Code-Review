# Tình huống kiểm thử — <tên tính năng>

Mẫu cho **việc T4** (Tầng 2 — kiểm thử hành vi có hệ thống). Sao chép thành `test-case-<tên tính năng>.md` ở thư mục gốc rồi điền.

**Nguyên tắc:**

- Tình huống được sinh **chỉ từ mô tả yêu cầu** bên dưới, không từ prompt gốc hay mã nguồn.
- Đủ 6 nhóm bắt buộc. Nhóm nào thật sự không áp dụng thì giữ tiêu đề và ghi lý do, không xoá.
- Cột *Kết quả thực tế* và *Đạt?* do **con người** điền khi thao tác thử. AI sinh danh sách thì để trống hai cột này.
- Không ghi dữ liệu thật của người dùng, tên khách hàng hay tên module nội bộ vào tệp (quy tắc A.1).

---

## Mô tả yêu cầu

> <dán nguyên văn cột *Yêu cầu* của dòng tương ứng trong `nhat-ky.csv`>

## Điều kiện chuẩn bị

- Tài khoản dùng để thử: <ví dụ: 2 tài khoản thường A, B và 1 tài khoản quản trị>
- Dữ liệu cần có sẵn: <ví dụ: tài khoản A có 0 bản ghi, tài khoản B có ≥ 1 000 bản ghi>
- Cách tạo mạng chậm: <ví dụ: DevTools → Network → Slow 3G>

---

## 1. Luồng chính

| Mã | Bước thao tác | Kết quả mong đợi | Kết quả thực tế | Đạt? |
| --- | --- | --- | --- | --- |
| TC-01 | | | | |

## 2. Dữ liệu rỗng

Danh sách không có phần tử, bộ lọc không khớp kết quả nào, trường để trống, tài khoản mới tạo chưa có dữ liệu.

| Mã | Bước thao tác | Kết quả mong đợi | Kết quả thực tế | Đạt? |
| --- | --- | --- | --- | --- |
| TC-1x | | | | |

## 3. Dữ liệu sai

Sai kiểu, quá dài, ký tự đặc biệt, số âm, ngày không tồn tại, **ID thuộc về người khác** (đổi tham số trên URL / trong request).

| Mã | Bước thao tác | Kết quả mong đợi | Kết quả thực tế | Đạt? |
| --- | --- | --- | --- | --- |
| TC-2x | | | | |

## 4. Mạng chậm

Phản hồi chậm, mất kết nối giữa chừng, dịch vụ bên ngoài không trả lời.

| Mã | Bước thao tác | Kết quả mong đợi | Kết quả thực tế | Đạt? |
| --- | --- | --- | --- | --- |
| TC-3x | | | | |

## 5. Thao tác trùng

Bấm nút gửi hai lần, tải lại trang sau khi gửi, mở hai tab cùng sửa một bản ghi.

| Mã | Bước thao tác | Kết quả mong đợi | Kết quả thực tế | Đạt? |
| --- | --- | --- | --- | --- |
| TC-4x | | | | |

## 6. Phiên hết hạn

Đăng xuất ở tab khác rồi thao tác, xoá cookie phiên, dùng token đã hết hạn.

| Mã | Bước thao tác | Kết quả mong đợi | Kết quả thực tế | Đạt? |
| --- | --- | --- | --- | --- |
| TC-5x | | | | |

---

## Ghi nhận sau khi thử

- Số tình huống: <tổng> — đạt: <số> — không đạt: <số>
- Tình huống không đạt nào **không** lộ ra khi kiểm tra bằng mắt lần đầu: <liệt kê mã>
