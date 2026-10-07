# Rà soát — <tên tính năng>

Mẫu cho **việc T5** (Tầng 3 — AI rà soát giới hạn phạm vi). Sao chép thành `ra-soat-<tên tính năng>.md` ở thư mục gốc rồi điền.

**Nguyên tắc** (theo `checklist.md` và mục 5.3 của kế hoạch):

- Rà soát chỉ dựa trên **tài liệu yêu cầu** và mã nguồn, không đưa prompt gốc cho mô hình rà soát.
- Dùng mô hình **khác** với mô hình đã sinh mã nguồn.
- Người rà soát chỉ ghi lại phát hiện, **không kết luận đúng hay sai**. Cột *Phân loại của con người* để trống cho tới khi tổng hợp ở việc T6.
- Vị trí ghi theo tệp / hàm / điểm truy cập, không ghi tên module nội bộ. Không chép giá trị khoá bí mật vào tệp.

---

## Thông tin rà soát

| Mục | Nội dung |
| --- | --- |
| Tính năng | <khớp đúng cột *Tính năng* trong `nhat-ky.csv`> |
| Mô hình sinh mã | <tên mô hình> |
| Mô hình rà soát | <tên mô hình — phải khác dòng trên> |
| Ngày rà soát | <YYYY-MM-DD> |
| Phạm vi tệp được rà | <danh sách tệp / thư mục> |

## Mô tả yêu cầu

> <dán nguyên văn cột *Yêu cầu* trong `nhat-ky.csv`>

---

## Kết quả theo 12 tiêu chí

*Đáp án đạt* lấy từ `checklist.md`. Cột *Trả lời* ghi đúng câu trả lời cho câu hỏi của tiêu chí (Có / Không / Không áp dụng), chưa phải kết luận lỗi.

| Mã | Tiêu chí (rút gọn) | Đáp án đạt | Trả lời | Số phát hiện |
| --- | --- | --- | --- | --- |
| C01 | Bí mật nằm trong mã nguồn / cấu hình được commit | Không | | |
| C02 | Thông báo lỗi chứa thông tin nội bộ | Không | | |
| C03 | Điểm truy cập dữ liệu kiểm tra quyền phía máy chủ | Có | | |
| C04 | Đổi ID sang của người khác thì bị từ chối | Có | | |
| C05 | Dữ liệu gửi lên được kiểm tra phía máy chủ | Có | | |
| C06 | Truy vấn số liệu đủ điều kiện lọc theo yêu cầu | Có | | |
| C07 | Tổng / đếm / tỷ lệ xử lý trường hợp không có dữ liệu | Có | | |
| C08 | Trạng thái danh sách rỗng được xử lý riêng | Có | | |
| C09 | Gửi trùng gây tạo trùng dữ liệu | Không | | |
| C10 | Phiên hết hạn / xác thực sai được phản hồi rõ ràng | Có | | |
| C11 | Phụ thuộc bên ngoài có giới hạn thời gian chờ và đường xử lý lỗi | Có | | |
| C12 | Truy vấn chạy lặp theo từng phần tử danh sách | Không | | |

---

## Danh sách phát hiện

Mỗi phát hiện một mục, đúng mẫu trong `checklist.md`:

```
- Tiêu chí: <mã tiêu chí, ví dụ C03>
  Vị trí: <tệp / hàm / điểm truy cập>
  Mức nghiêm trọng: Cao / Trung bình / Thấp
  Mô tả dấu hiệu: <quan sát được gì, 1-2 câu>
  Trùng với quét tự động: <Có — ghi mã quy tắc / Không>
  Phân loại của con người: <để trống — điền ở việc T6: Đúng / Báo động giả>
```

<!-- Phát hiện bắt đầu từ đây -->

---

## Dấu hiệu ngoài 12 tiêu chí

Vấn đề quan sát được mà chưa tiêu chí nào phủ. Nếu loại này lặp lại ở nhiều tính năng, bổ sung tiêu chí mới vào `checklist.md` kèm ngày bổ sung.

- <để trống nếu không có>
