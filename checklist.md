# Checklist rà soát — 12 tiêu chí

Checklist này dùng cho **Tầng 3 (AI rà soát giới hạn phạm vi)** và cho phần rà soát của con người.

**Nguyên tắc chọn tiêu chí:** chỉ đưa vào những câu hỏi mà **quan sát trực tiếp trên giao diện không trả lời được**. Không có tiêu chí chung chung về chất lượng mã nguồn (kiểu "mã nguồn có dễ đọc không", "có đặt tên biến tốt không") — những câu đó không tạo ra bằng chứng kiểm chứng được.

**Cách dùng:**

- Mỗi tiêu chí trả lời bằng **Có / Không**. Cột *Đáp án đạt* nói rõ đáp án nào là đạt, để tránh nhầm chiều.
- Rà soát chỉ dựa trên **tài liệu yêu cầu**, không dựa trên prompt gốc (mục 5.3 của kế hoạch).
- Người rà soát **không tự kết luận** một phát hiện là đúng hay sai — chỉ ghi lại phát hiện. Việc phân loại thuộc về con người (quy tắc A.1).

**Mẫu ghi một phát hiện** (dùng cho tệp `ra-soat-<tên tính năng>.md` ở việc T5):

```
- Tiêu chí: <mã tiêu chí, ví dụ C03>
  Vị trí: <tệp / hàm / điểm truy cập — không ghi tên module nội bộ>
  Mức nghiêm trọng: Cao / Trung bình / Thấp
  Mô tả dấu hiệu: <quan sát được gì, 1-2 câu>
```

**Thang mức nghiêm trọng:**

| Mức | Nghĩa |
| --- | --- |
| Cao | Có thể làm lộ dữ liệu, lộ khoá bí mật, hoặc cho phép truy cập vượt quyền |
| Trung bình | Làm sai số liệu hiển thị, hoặc gây lỗi ở trạng thái người dùng thật sẽ gặp |
| Thấp | Chỉ ảnh hưởng khi điều kiện hiếm xảy ra, hoặc chỉ ảnh hưởng vận hành |

---

## Nhóm A — Khoá bí mật và thông tin nhạy cảm

### C01. Có giá trị bí mật nào nằm trực tiếp trong mã nguồn hoặc trong tệp cấu hình được commit không?

**Đáp án đạt: Không**

Dấu hiệu nhận biết:

- Chuỗi ký tự dài ngẫu nhiên gán trực tiếp vào biến, không đọc từ biến môi trường.
- Chuỗi kết nối cơ sở dữ liệu có kèm tên người dùng và mật khẩu.
- Tệp `.env`, `.env.local`, tệp khoá, tệp chứng chỉ xuất hiện trong danh sách tệp được commit.
- Khoá nằm trong mã nguồn chạy ở phía trình duyệt (bất kỳ giá trị nào gửi xuống trình duyệt đều coi như đã công khai).

### C02. Thông báo lỗi trả ra cho người dùng có chứa thông tin nội bộ không?

**Đáp án đạt: Không**

Dấu hiệu nhận biết:

- Phản hồi lỗi chứa đường dẫn tệp trên máy chủ, dấu vết lỗi (stack trace), hoặc câu truy vấn cơ sở dữ liệu.
- Bắt lỗi rồi trả nguyên văn nội dung lỗi gốc ra ngoài.
- Thông báo lỗi đăng nhập phân biệt rõ "không tồn tại người dùng" và "sai mật khẩu".

---

## Nhóm B — Phân quyền và kiểm soát truy cập

### C03. Mọi điểm truy cập dữ liệu người dùng có kiểm tra quyền của người gọi ở phía máy chủ không?

**Đáp án đạt: Có**

Dấu hiệu nhận biết:

- Có điểm truy cập (endpoint) đọc hoặc ghi dữ liệu mà không có bước xác định người gọi là ai.
- Việc giới hạn quyền chỉ được thực hiện bằng cách ẩn nút hoặc ẩn menu trên giao diện.
- Có kiểm tra "đã đăng nhập chưa" nhưng không kiểm tra "có quyền với đúng bản ghi này không".

### C04. Khi tham số định danh (ID) trong đường dẫn hoặc trong request bị đổi sang giá trị thuộc về người khác, hệ thống có từ chối không?

**Đáp án đạt: Có**

Dấu hiệu nhận biết:

- Truy vấn lấy bản ghi chỉ lọc theo ID nhận từ request, không lọc kèm theo định danh người dùng đang đăng nhập.
- Định danh bản ghi là số tăng dần, dễ đoán giá trị của người khác.
- Hành động xoá hoặc sửa nhận ID từ request mà không kiểm tra lại chủ sở hữu.

### C05. Dữ liệu người dùng gửi lên có được kiểm tra và ràng buộc ở phía máy chủ không?

**Đáp án đạt: Có**

Dấu hiệu nhận biết:

- Việc kiểm tra dữ liệu chỉ tồn tại ở giao diện (bắt buộc nhập, giới hạn độ dài, chọn từ danh sách).
- Máy chủ nhận cả đối tượng dữ liệu từ request rồi lưu thẳng, không chọn lọc từng trường được phép sửa.
- Các trường lẽ ra hệ thống tự quyết (vai trò, trạng thái duyệt, giá, số dư) có thể bị đặt giá trị từ request.

---

## Nhóm C — Tính đúng của số liệu hiển thị

### C06. Các truy vấn hiển thị số liệu có đủ điều kiện lọc theo đúng mô tả yêu cầu không?

**Đáp án đạt: Có**

Dấu hiệu nhận biết:

- Yêu cầu nêu một điều kiện (chỉ tính bản ghi đã duyệt, chỉ trong kỳ hiện tại, chỉ thuộc một đơn vị) nhưng truy vấn không có điều kiện đó.
- Bản ghi đã xoá mềm vẫn được đếm vào tổng.
- Số liệu trông hợp lý về độ lớn nên không ai đối chiếu lại — đây là loại lỗi quan sát bằng mắt không bắt được.

### C07. Việc tính tổng, đếm, chia tỷ lệ có xử lý trường hợp không có dữ liệu không?

**Đáp án đạt: Có**

Dấu hiệu nhận biết:

- Phép chia không kiểm tra mẫu số bằng 0.
- Tổng của danh sách rỗng hiển thị thành giá trị trống thay vì 0.
- Giá trị trung bình được tính trên tập đã bị lọc bớt nhưng vẫn chia cho tổng số ban đầu.

---

## Nhóm D — Các trạng thái không ai thao tác tới

### C08. Trạng thái danh sách rỗng / không có kết quả có được xử lý riêng không?

**Đáp án đạt: Có**

Dấu hiệu nhận biết:

- Giao diện chỉ được thử với dữ liệu mẫu có sẵn, chưa thử với tài khoản mới chưa có dữ liệu.
- Không có nhánh xử lý riêng cho trường hợp danh sách trả về rỗng.

### C09. Thao tác gửi trùng (bấm hai lần, gửi lại request) có gây tạo trùng dữ liệu không?

**Đáp án đạt: Không**

Dấu hiệu nhận biết:

- Nút gửi không bị khoá trong lúc đang xử lý.
- Không có ràng buộc duy nhất ở cơ sở dữ liệu, cũng không có khoá chống trùng cho yêu cầu.
- Hành động có hệ quả tài chính hoặc gửi thông báo ra ngoài nhưng không có cơ chế chống lặp.

### C10. Khi phiên đăng nhập hết hạn hoặc thông tin xác thực không hợp lệ, hệ thống có phản hồi rõ ràng không?

**Đáp án đạt: Có**

Dấu hiệu nhận biết:

- Hết phiên dẫn tới trang trắng, hoặc lỗi không hiểu được, thay vì chuyển về trang đăng nhập.
- Thông tin xác thực hết hạn vẫn được dùng để gọi tiếp mà không có bước làm mới hoặc đăng xuất.

### C11. Khi phụ thuộc bên ngoài chậm hoặc lỗi, có giới hạn thời gian chờ và đường xử lý thất bại không?

**Đáp án đạt: Có**

Dấu hiệu nhận biết:

- Lệnh gọi ra ngoài (API, dịch vụ thanh toán, gửi thư) không đặt giới hạn thời gian chờ.
- Không có nhánh xử lý khi lệnh gọi thất bại — lỗi lan thẳng ra người dùng.
- Việc thử lại không giới hạn số lần, hoặc thử lại cả những hành động không an toàn khi lặp.

---

## Nhóm E — Hành vi với dữ liệu thật

### C12. Có truy vấn nào chạy lặp theo từng phần tử của danh sách không?

**Đáp án đạt: Không**

Dấu hiệu nhận biết:

- Trong vòng lặp qua danh sách có một lệnh truy vấn cơ sở dữ liệu hoặc một lệnh gọi mạng.
- Danh sách trả về toàn bộ bản ghi, không phân trang và không giới hạn số lượng.
- Chạy nhanh với vài chục bản ghi mẫu — chỉ tắc khi dữ liệu thật lớn lên, nên quan sát bằng mắt ở giai đoạn phát triển không phát hiện được.

---

## Ghi chú về phạm vi checklist

Checklist này **không** thay thế việc kiểm thử hành vi ở Tầng 2. Tầng 2 trả lời "tính năng có làm đúng việc được yêu cầu không". Checklist này trả lời "có vấn đề nào tồn tại mà vẫn làm đúng việc được yêu cầu không".

Nếu trong quá trình thực hiện phát hiện một loại lỗi lặp lại nhiều lần nhưng chưa có tiêu chí nào phủ, hãy bổ sung tiêu chí mới vào đây và **ghi lại ngày bổ sung** — bản thân việc checklist phải mở rộng cũng là một kết quả nghiên cứu.
