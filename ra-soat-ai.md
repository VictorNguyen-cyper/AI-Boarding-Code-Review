# Hướng dẫn rà soát bằng AI (Tầng 3) — dùng Gemini

Tầng 3 dùng **Gemini trên web** (gemini.google.com) làm mô hình rà soát. Mục 5.3 của kế hoạch yêu cầu mô hình rà soát phải khác mô hình sinh mã nguồn, và Gemini thuộc họ khác với công cụ đang dùng để sinh mã.

Lý do chọn Gemini: sinh viên được dùng gói Pro miễn phí, nên thực tập sinh khoá sau có thể làm lại quy trình này mà không tốn chi phí.

Lý do dùng bản web thay vì Gemini CLI (ghi ngày 2026-10-06): khi đăng nhập Gemini CLI bằng tài khoản Google cá nhân, Google báo gói "Gemini Code Assist for individuals" **không còn hỗ trợ Gemini CLI** và yêu cầu chuyển sang Antigravity. Gói Pro sinh viên không áp dụng cho đường này. Dùng khoá API miễn phí thì Google có thể dùng nội dung gửi lên để huấn luyện, không hợp với mã của công ty.

---

## 0. Trước khi gửi mã đi — bắt buộc đọc

Khi rà soát, **mã nguồn của tính năng sẽ được tải lên máy chủ của Google**.

1. **Phải được người hướng dẫn cho phép gửi mã tới Gemini.** Chưa được phép thì không làm. Có thể hỏi miệng, nhưng nên ghi lại ngày được đồng ý ở mục 2.
2. **Tắt lưu hoạt động.** Trên gemini.google.com, vào **Cài đặt → Hoạt động** (Gemini Apps Activity) và **tắt**. Khi tắt, cuộc trò chuyện không được dùng để cải thiện mô hình. Google vẫn giữ tạm cuộc trò chuyện trong thời gian ngắn để vận hành dịch vụ.
3. **Script tự loại nội dung các tệp bí mật** (`.env`, `*.pem`, `*.key`…) và chỉ ghi tên tệp. Dù vậy, vẫn **chạy `gitleaks` trước** (xem `quet-tu-dong.md`). Khoá nằm trong mã thường thì vẫn bị gửi đi cùng mã.
4. Tệp đầu vào nằm trong thư mục `dau-vao/` và **không được commit** (đã khai báo trong `.gitignore`), vì tệp này chứa nguyên mã nguồn.

---

## 1. Chuẩn bị tài khoản (một lần)

1. Đăng nhập gemini.google.com bằng tài khoản Google có gói Pro sinh viên.
2. Tắt hoạt động như mục 0.2.

---

## 2. Chọn và cố định mô hình

Ở ô chọn mô hình trên gemini.google.com, **chọn bản Pro** vì tầng 3 cần suy luận sâu.

**Giữ đúng một mô hình suốt dự án.** Đổi mô hình giữa chừng thì số liệu tầng 3 của các tính năng không so sánh được với nhau.

| Mục | Giá trị |
| --- | --- |
| Mô hình rà soát | *(điền đúng tên hiển thị trên Gemini)* |
| Ngày chọn | *(điền)* |
| Người hướng dẫn đồng ý gửi mã ra ngoài | *(điền ngày)* |

---

## 3. Chuẩn bị cho mỗi tính năng

Cần hai thứ:

1. **Tệp yêu cầu**, ví dụ `yeu-cau-<tên tính năng>.md`: mô tả tính năng **phải làm gì**, viết như tài liệu yêu cầu.
   - **Không dán prompt gốc đã dùng để sinh mã** (mục 5.3). Đưa prompt gốc vào thì mô hình rà soát dễ chỉ xác nhận lại đúng những gì đã yêu cầu.
   - Ghi rõ các điều kiện nghiệp vụ, ví dụ "chỉ người tạo được sửa", "chỉ tính đơn đã duyệt". Tiêu chí C04 và C06 dựa vào các điều kiện này.
2. **Thư mục chứa mã nguồn** của tính năng.

---

## 4. Chạy rà soát

Chỉ làm **sau khi** đã điền cột *Kiểm tra bằng mắt* và đã chạy quét tầng 1.

**Bước 1 — Tạo tệp đầu vào:**

```bash
./ra-soat.sh <tên-tính-năng> yeu-cau-<tên>.md <thư-mục-mã>
```

Script tạo hai tệp:

- `dau-vao/ra-soat-<tên>.txt`: gồm **câu lệnh rà soát cố định**, checklist, tệp yêu cầu và mã nguồn (đã bỏ `node_modules`, `.git`, thư mục build). Câu lệnh giống nhau cho mọi tính năng nên kết quả so sánh được với nhau.
- `ra-soat-<tên>.md`: khung kết quả, có sẵn phần thông tin đầu tệp.

Nếu `ra-soat-<tên>.md` đã tồn tại, script dừng và không ghi đè. Kết quả lần đầu là dữ liệu nghiên cứu, không chạy lại để lấy kết quả "đẹp hơn".

**Bước 2 — Gửi cho Gemini:**

1. Mở **cuộc trò chuyện mới** trên gemini.google.com. Mỗi tính năng dùng một cuộc trò chuyện riêng để Gemini không nhớ nội dung các lần trước.
2. Chọn đúng mô hình đã ghi ở mục 2.
3. Tải tệp `dau-vao/ra-soat-<tên>.txt` lên, rồi gõ đúng câu: **`Làm đúng theo phần HƯỚNG DẪN ở đầu tệp đính kèm.`**
4. Bấm giờ từ lúc gửi đến khi Gemini trả lời xong.

**Bước 3 — Lưu kết quả:**

1. Bấm nút sao chép câu trả lời của Gemini và dán **nguyên văn** vào cuối `ra-soat-<tên>.md`, không sửa.
2. Điền tên mô hình và thời gian chờ vào phần đầu tệp.

---

## 5. Đọc kết quả và ghi nhật ký

1. Ghi từng phát hiện vào cột *AI rà soát phát hiện* của `nhat-ky.csv` theo dạng `<mã tiêu chí> tại <vị trí>, mức <Cao/TB/Thấp>`.
2. **Chưa phân loại đúng/sai ở bước này.** Việc phân loại làm khi tổng hợp (việc T6), để tính tỷ lệ phát hiện đúng và tỷ lệ báo động giả (bảng độ tin cậy, mục 8).
3. Phát hiện nào trùng với kết quả của `semgrep` thì ghi ở cả hai cột (xem `quet-tu-dong.md` mục 3).
4. Đọc kỹ mục *Câu hỏi còn mở*. Nếu phần lớn tiêu chí là "Không đủ thông tin" thì có thể đã gửi thiếu mã phía máy chủ.

---

## 6. Đối chiếu chéo (tuỳ chọn)

Mục 5.3 gợi ý đối chiếu chéo hai mô hình. Có thể tải cùng tệp đầu vào lên một mô hình thứ hai và so hai kết quả. **Chỗ hai mô hình kết luận khác nhau là chỗ cần con người xem kỹ.**

---

## 7. Hạn chế đã biết

- Gói Pro **giới hạn số lượt dùng mô hình Pro mỗi ngày**. Hết lượt thì đợi sang ngày hôm sau, **không đổi sang mô hình khác** để làm tiếp.
- Mã quá lớn có thể vượt giới hạn tệp tải lên. Khi đó chỉ đưa thư mục chứa mã của đúng tính năng đang xét.
- Mô hình có thể bịa vị trí không có thật. Câu lệnh đã cấm việc này, nhưng vẫn phải mở đúng tệp và dòng để kiểm tra trước khi tin.
- Bước gửi và dán kết quả làm bằng tay, nên dễ quên điền thời gian chờ. Điền ngay khi dán kết quả.
