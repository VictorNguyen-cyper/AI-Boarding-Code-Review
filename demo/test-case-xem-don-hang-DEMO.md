# Tình huống kiểm thử — Xem đơn hàng (DEMO)

> DEMO — không phải dữ liệu nghiên cứu. Sinh bằng `python chay_tang2.py`.

| Mã | Nhóm | Bước thao tác | Kết quả mong đợi | Kết quả thực tế | Đạt? |
| --- | --- | --- | --- | --- | --- |
| TC-01 | Luồng chính | An xem danh sách đơn | 200, 2 đơn chưa xoá của An | 200, 2 đơn | Đạt |
| TC-02 | Luồng chính | An xem chi tiết đơn 1 | 200, đơn 1 | 200 {"deleted":0,"id":1,"note":"\u0110\u01a1n c\u1ee7a An","status":"done" | Đạt |
| TC-03 | Luồng chính | An tạo đơn mới | 201, có id | 201 {"id":5} | Đạt |
| TC-04 | Luồng chính | An xem tỷ lệ hoàn thành | total=2, rate=50.0 (không tính đơn đã xoá) | 200 total=3 rate=33.3 | **Không đạt** |
| TC-11 | Dữ liệu rỗng | Tài khoản mới xem danh sách | 200, danh sách rỗng | 200 [] | Đạt |
| TC-12 | Dữ liệu rỗng | Tài khoản mới xem thống kê | 200, rate=0 hoặc thông báo chưa có dữ liệu | 500 <!doctype html> <html lang=en> <title>500 Internal Server Error</title | **Không đạt** |
| TC-21 | Dữ liệu sai | An mở đơn 4 (của Bình) bằng cách sửa ID | 403 hoặc 404 | 200 {"deleted":0,"id":4,"note":"\u0110\u01a1n c\u1ee7a B\u00ecnh","status" | **Không đạt** |
| TC-22 | Dữ liệu sai | Tạo đơn thiếu trường note | 400, báo thiếu trường | 500 <!doctype html> <html lang=en> <title>500 Internal Server Error</title | **Không đạt** |
| TC-23 | Dữ liệu sai | Tạo đơn với note dài 100 000 ký tự | 400, báo quá dài | 201 {"id":5} | **Không đạt** |
| TC-31 | Mạng chậm | Dịch vụ vận chuyển không kết nối được | 502/503, thông báo chung, không lộ địa chỉ nội bộ | 500 {"error":"<urlopen error [Errno 61] Connection refused>","url":"http:/ (lộ URL nội bộ) | **Không đạt** |
| TC-32 | Mạng chậm | Dịch vụ vận chuyển treo không trả lời | Trả lỗi trong vài giây | vẫn chờ sau 8 giây, không có giới hạn thời gian chờ | **Không đạt** |
| TC-41 | Thao tác trùng | Bấm Gửi hai lần với cùng nội dung | Chỉ 1 đơn được tạo | tạo ra 2 đơn | **Không đạt** |
| TC-51 | Phiên hết hạn | Gọi /orders không có token | 401, thông báo cần đăng nhập | 500 <!doctype html> <html lang=en> <title>500 Internal Server Error</title | **Không đạt** |
| TC-52 | Phiên hết hạn | Gọi /orders với token đã hết hạn | 401, thông báo phiên hết hạn | 500 <!doctype html> <html lang=en> <title>500 Internal Server Error</title | **Không đạt** |

Tổng: 14 — đạt: 4 — không đạt: 10
