# Rà soát — Xem đơn hàng (DEMO)

> **DEMO** — chạy thử quy trình trên ứng dụng giả lập. Không phải dữ liệu nghiên cứu, không đưa vào `nhat-ky.csv` hay `ket-qua.md`.
> Giới hạn của bản demo: mã nguồn và rà soát do **cùng một mô hình** thực hiện, trái với mục 5.3. Khi làm thật phải dùng mô hình rà soát khác.

## Thông tin rà soát

| Mục | Nội dung |
| --- | --- |
| Tính năng | Xem đơn hàng |
| Mô hình sinh mã | Claude Opus 5.5 (demo) |
| Mô hình rà soát | Claude Opus 5.5 (demo — vi phạm mục 5.3) |
| Ngày rà soát | 2026-10-06 |
| Phạm vi tệp được rà | `app/app.py`, `app/requirements.txt` |

## Kết quả theo 12 tiêu chí

| Mã | Tiêu chí (rút gọn) | Đáp án đạt | Trả lời | Số phát hiện |
| --- | --- | --- | --- | --- |
| C01 | Bí mật nằm trong mã nguồn / cấu hình được commit | Không | Có | 2 |
| C02 | Thông báo lỗi chứa thông tin nội bộ | Không | Có | 1 |
| C03 | Điểm truy cập dữ liệu kiểm tra quyền phía máy chủ | Có | Không | 1 |
| C04 | Đổi ID sang của người khác thì bị từ chối | Có | Không | 1 |
| C05 | Dữ liệu gửi lên được kiểm tra phía máy chủ | Có | Không | 1 |
| C06 | Truy vấn số liệu đủ điều kiện lọc theo yêu cầu | Có | Không | 1 |
| C07 | Tổng / đếm / tỷ lệ xử lý trường hợp không có dữ liệu | Có | Không | 1 |
| C08 | Trạng thái danh sách rỗng được xử lý riêng | Có | Có | 0 |
| C09 | Gửi trùng gây tạo trùng dữ liệu | Không | Có | 1 |
| C10 | Phiên hết hạn / xác thực sai được phản hồi rõ ràng | Có | Không | 1 |
| C11 | Phụ thuộc bên ngoài có giới hạn thời gian chờ và đường xử lý lỗi | Có | Không | 1 |
| C12 | Truy vấn chạy lặp theo từng phần tử danh sách | Không | Có | 1 |

## Danh sách phát hiện

```
- Tiêu chí: C01
  Vị trí: app/app.py:9 — cấu hình SECRET_KEY
  Mức nghiêm trọng: Cao
  Mô tả dấu hiệu: Khoá ký phiên gán trực tiếp bằng chuỗi ngẫu nhiên, không đọc từ biến môi trường.
  Trùng với quét tự động: Có — semgrep avoid_hardcoded_config_SECRET_KEY
  Phân loại của con người:

- Tiêu chí: C01
  Vị trí: app/app.py:10 — hằng SHIPPING_API_KEY
  Mức nghiêm trọng: Cao
  Mô tả dấu hiệu: Khoá API dịch vụ vận chuyển gán trực tiếp bằng chuỗi ngẫu nhiên trong mã nguồn.
  Trùng với quét tự động: Có — gitleaks generic-api-key
  Phân loại của con người:

- Tiêu chí: C02
  Vị trí: app/app.py:92 — GET /orders/<id>/tracking
  Mức nghiêm trọng: Trung bình
  Mô tả dấu hiệu: Nhánh lỗi trả nguyên văn str(e) và địa chỉ dịch vụ nội bộ cho người dùng.
  Trùng với quét tự động: Không
  Phân loại của con người:

- Tiêu chí: C03
  Vị trí: app/app.py:54 — GET /orders/<id>
  Mức nghiêm trọng: Cao
  Mô tả dấu hiệu: Hàm chỉ xác định người gọi, không so user_id của đơn với người gọi trước khi trả dữ liệu.
  Trùng với quét tự động: Không
  Phân loại của con người:

- Tiêu chí: C04
  Vị trí: app/app.py:54 — GET /orders/<id>
  Mức nghiêm trọng: Cao
  Mô tả dấu hiệu: Truy vấn chỉ lọc theo id, đổi id sang đơn của người khác vẫn trả về 200.
  Trùng với quét tự động: Không
  Phân loại của con người:

- Tiêu chí: C05
  Vị trí: app/app.py:68 — POST /orders
  Mức nghiêm trọng: Trung bình
  Mô tả dấu hiệu: Trường note không được kiểm tra có tồn tại, kiểu dữ liệu hay độ dài.
  Trùng với quét tự động: Không
  Phân loại của con người:

- Tiêu chí: C06
  Vị trí: app/app.py:77 — GET /stats
  Mức nghiêm trọng: Trung bình
  Mô tả dấu hiệu: Truy vấn đếm tổng thiếu điều kiện deleted=0, trong khi yêu cầu nêu "không gồm đơn đã xoá".
  Trùng với quét tự động: Không
  Phân loại của con người:

- Tiêu chí: C07
  Vị trí: app/app.py:81 — GET /stats
  Mức nghiêm trọng: Trung bình
  Mô tả dấu hiệu: Phép chia done / total không xử lý total = 0.
  Trùng với quét tự động: Không
  Phân loại của con người:

- Tiêu chí: C09
  Vị trí: app/app.py:63 — POST /orders
  Mức nghiêm trọng: Trung bình
  Mô tả dấu hiệu: Không có khoá chống gửi trùng hay ràng buộc duy nhất; mỗi request tạo một bản ghi.
  Trùng với quét tự động: Không
  Phân loại của con người:

- Tiêu chí: C10
  Vị trí: app/app.py:37 — hàm xác định người gọi
  Mức nghiêm trọng: Trung bình
  Mô tả dấu hiệu: Thiếu header hoặc token không hợp lệ gây KeyError thay vì phản hồi 401.
  Trùng với quét tự động: Không
  Phân loại của con người:

- Tiêu chí: C11
  Vị trí: app/app.py:90 — GET /orders/<id>/tracking
  Mức nghiêm trọng: Thấp
  Mô tả dấu hiệu: urlopen không truyền timeout; khi dịch vụ treo, request treo theo.
  Trùng với quét tự động: Có một phần — semgrep dynamic-urllib-use-detected (cảnh báo khác, cùng vị trí)
  Phân loại của con người:

- Tiêu chí: C12
  Vị trí: app/app.py:48 — GET /orders
  Mức nghiêm trọng: Thấp
  Mô tả dấu hiệu: Mỗi đơn hàng chạy thêm một truy vấn lấy items bên trong vòng lặp.
  Trùng với quét tự động: Không
  Phân loại của con người:
```

## Dấu hiệu ngoài 12 tiêu chí

- Không có.
