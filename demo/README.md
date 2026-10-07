# Demo — chạy thử quy trình nghiệm thu 3 tầng

> **Không phải dữ liệu nghiên cứu.** Thư mục này chỉ minh hoạ cách các công cụ trong repo phối hợp với nhau. Không đưa số liệu ở đây vào `nhat-ky.csv`, `ket-qua.md` hay báo cáo (quy tắc A.1).

## Hạn chế của bản demo

- Lỗi được **cố ý cài** vào ứng dụng giả lập, nên tỷ lệ phát hiện của Tầng 3 bị thổi phồng.
- Mã nguồn và rà soát do **cùng một mô hình** thực hiện, trái mục 5.3 của kế hoạch. Tầng 3 của demo được làm tay theo định dạng phát hiện của `checklist.md`, **không** qua `ra-soat.sh` và Gemini như quy trình thật (xem `ra-soat-ai.md`).
- Cột *Kiểm tra bằng mắt* trong `nhat-ky-DEMO.csv` là **giả định**, không do người thao tác điền.
- Hai khoá trong `app/app.py` (dòng 9 và 10) là **khoá giả**. Phát hiện của gitleaks ở dòng 10 được khai báo trong `.gitleaksignore` ở thư mục gốc để hook không chặn commit; nếu sửa `app.py` làm dịch dòng thì phải cập nhật lại tệp này.

## Nội dung

| Tệp | Tầng | Nội dung |
| --- | --- | --- |
| `app/` | — | Ứng dụng Flask giả lập tính năng "Xem đơn hàng" |
| `nhat-ky-DEMO.csv` | — | Một dòng nhật ký theo đúng 8 cột |
| `test-case-xem-don-hang-DEMO.md` | 2 | 14 tình huống theo 6 nhóm, kèm kết quả chạy thật |
| `ra-soat-xem-don-hang-DEMO.md` | 3 | Rà soát theo 12 tiêu chí, định dạng của `checklist.md` (không qua Gemini) |
| `bang-doi-chieu-DEMO.md` | — | Vấn đề nào bị tầng nào bắt được |
| `demo.html` | — | Trang tổng hợp, mở trực tiếp bằng trình duyệt |
| `chay_tang2.py`, `tao_trang.py`, `tang2.json` | — | Script chạy Tầng 2, script dựng trang, kết quả thô |

## Chạy lại

Từ thư mục gốc của repo:

```bash
python3 -m venv demo/.venv && demo/.venv/bin/pip install -r demo/app/requirements.txt

# Tầng 1 — báo cáo nằm ở ket-qua-quet/ (không commit).
# Lưu ý: vì .gitleaksignore đã khai báo khoá ở app.py:10, chạy lại sẽ KHÔNG thấy
# phát hiện gitleaks đó nữa (Tầng 1 còn 1/11 thay vì 2/11 trong bảng đối chiếu).
# Muốn tái hiện đúng, tạm đổi tên .gitleaksignore trước khi chạy rồi đổi lại.
NHAT_KY=demo/nhat-ky-DEMO.csv scripts/quet.sh "Xem đơn hàng" demo/app

# Tầng 2
demo/.venv/bin/python demo/chay_tang2.py

# Dựng lại trang tổng hợp
python3 demo/tao_trang.py
```
