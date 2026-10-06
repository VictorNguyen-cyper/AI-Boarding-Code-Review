# Hướng dẫn cài và chạy bộ quét tự động (Tầng 1)

Tầng 1 lo ba loại vấn đề: **rò rỉ khoá bí mật**, **thư viện có lỗ hổng đã công bố**, **lỗi bảo mật theo mẫu**. Cài một lần, sau đó chạy tự động.

Môi trường hướng dẫn: macOS, dùng Homebrew. Đã có sẵn trên máy: `brew`, `git`, `npm`, `python3`.

---

## 0. Cài đặt một lần

```bash
brew install gitleaks semgrep trivy
```

Kiểm tra cài xong:

```bash
gitleaks version && semgrep --version && trivy --version
```

Ba công cụ này không gửi mã nguồn ra ngoài khi chạy ở chế độ dưới đây. `semgrep` và `trivy` có tải bộ quy tắc / cơ sở dữ liệu lỗ hổng từ mạng về máy — đó là chiều tải xuống, không phải chiều gửi mã nguồn lên.

---

## 1. Quét rò rỉ khoá bí mật — `gitleaks`

### Lệnh chạy

Quét các tệp đang có trong thư mục làm việc (kể cả tệp chưa commit):

```bash
gitleaks dir . --report-format json --report-path bao-cao-gitleaks.json
```

Quét toàn bộ lịch sử commit — dùng cho lần chạy đầu tiên, vì khoá đã bị commit rồi xoá đi thì vẫn còn trong lịch sử:

```bash
gitleaks git . --report-format json --report-path bao-cao-gitleaks-lich-su.json
```

### Cách đọc kết quả

Công cụ in ra số lượng phát hiện (`leaks found`) và trả **mã thoát khác 0** khi tìm thấy. Mỗi phát hiện trong tệp JSON có các trường cần đọc:

| Trường | Nghĩa |
| --- | --- |
| `RuleID` | Loại khoá bị nhận ra (khoá AWS, token GitHub, khoá riêng tư…) |
| `File`, `StartLine` | Vị trí |
| `Secret` | Giá trị bị phát hiện — **không dán giá trị này vào nhật ký hay báo cáo** |
| `Commit`, `Date` | Có mặt khi quét lịch sử: khoá bị đưa vào từ lúc nào |

Ghi vào cột *Quét tự động phát hiện* của `nhat-ky.csv` theo dạng: `gitleaks: <RuleID> tại <File>:<StartLine>`. Không ghi giá trị khoá.

### Trường hợp báo động giả

Chuỗi ngẫu nhiên trong dữ liệu kiểm thử, khoá công khai, mã băm có thể bị nhận nhầm. Khi xác định là báo động giả, khai báo vào tệp `.gitleaksignore` ở thư mục gốc, mỗi dòng một mã:

```
<Fingerprint của phát hiện, copy từ tệp JSON>
```

**Giữ lại con số báo động giả.** Tỷ lệ báo động giả của từng tầng là một trong bốn bảng kết quả (mục 8 của kế hoạch) — xoá đi là mất dữ liệu.

### Nếu thật sự có khoá bị lộ

Xoá khỏi mã nguồn **không đủ** — khoá vẫn còn trong lịch sử commit và phải coi như đã bị lộ. Việc cần làm: thu hồi và cấp lại khoá đó ở nơi phát hành. Báo người hướng dẫn trước khi xử lý.

---

## 2. Quét thư viện có lỗ hổng đã công bố

### 2a. Lệnh chung cho mọi ngôn ngữ — `trivy`

`trivy` tự nhận ra tệp khai báo thư viện có trong dự án:

```bash
trivy fs . --scanners vuln --format table
```

Chỉ hiện mức nghiêm trọng cao, và chỉ hiện lỗ hổng đã có bản sửa:

```bash
trivy fs . --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed
```

Xuất tệp JSON để lưu lại:

```bash
trivy fs . --scanners vuln --format json --output bao-cao-trivy.json
```

### 2b. Lệnh theo từng hệ sinh thái

Chạy thêm lệnh đúng với ngôn ngữ của dự án — kết quả thường cụ thể hơn về cách sửa:

```bash
# Dự án Node.js / JavaScript / TypeScript
npm audit
npm audit --json > bao-cao-npm-audit.json
npm audit fix            # chỉ nâng cấp trong phạm vi an toàn

# Dự án Python
pip3 install pip-audit
pip-audit -r requirements.txt
```

### Cách đọc kết quả

| Cần đọc | Ý nghĩa |
| --- | --- |
| Mức nghiêm trọng | CRITICAL / HIGH xử lý trước |
| Đã có bản sửa chưa | Có bản sửa thì nâng phiên bản; chưa có thì ghi nhận và báo người hướng dẫn |
| Thư viện trực tiếp hay gián tiếp | Gián tiếp (thư viện của thư viện) thì phải nâng thư viện cha, không sửa trực tiếp được |
| Dùng ở môi trường nào | Chỉ dùng khi phát triển thì mức ưu tiên thấp hơn chạy thật |

Ghi vào nhật ký theo dạng: `trivy: <tên thư viện> <mã CVE> mức <HIGH>`.

### Lưu ý khi dùng công cụ AI sinh mã nguồn

Công cụ AI thường gắn phiên bản thư viện theo dữ liệu huấn luyện, nên có thể chỉ định một phiên bản cũ đã có lỗ hổng. Đây là loại vấn đề đặc trưng của mã nguồn do AI sinh ra — nên tách riêng khi tổng hợp bảng phân loại ở mục 8.

---

## 3. Quét lỗi bảo mật theo mẫu — `semgrep`

### Lệnh chạy

Dùng bộ quy tắc sẵn có, chạy cục bộ:

```bash
semgrep --config=p/security-audit --config=p/secrets .
```

Chỉ lấy phát hiện mức cao, xuất tệp JSON:

```bash
semgrep --config=p/security-audit --severity=ERROR --json --output=bao-cao-semgrep.json .
```

Bộ quy tắc theo ngôn ngữ — thay cho `p/security-audit` khi đã biết rõ ngôn ngữ dự án:

```bash
semgrep --config=p/javascript .
semgrep --config=p/python .
```

Nếu lần chạy đầu quá nhiều kết quả, giới hạn vào phần mới thay đổi:

```bash
semgrep --config=p/security-audit --baseline-commit=HEAD~1 .
```

### Cách đọc kết quả

Mỗi phát hiện gồm: **tệp và dòng**, **mã quy tắc** (`check_id`), **mức** (`ERROR` / `WARNING` / `INFO`), và **mô tả** kèm hướng xử lý.

Những loại quy tắc liên quan trực tiếp tới các tiêu chí trong `checklist.md`:

| Loại phát hiện của semgrep | Tiêu chí tương ứng |
| --- | --- |
| Ghép chuỗi vào câu truy vấn cơ sở dữ liệu | C05 |
| Giá trị bí mật gán cứng trong mã nguồn | C01 |
| Lệnh gọi mạng không đặt giới hạn thời gian chờ | C11 |
| Trả nguyên văn nội dung lỗi gốc ra ngoài | C02 |
| Tắt kiểm tra chứng chỉ, dùng thuật toán băm yếu | — (ghi bổ sung) |

Khi một phát hiện của semgrep trùng với một tiêu chí trong checklist, **ghi cả hai nguồn vào nhật ký** (cột *Quét tự động phát hiện* và cột *AI rà soát phát hiện*). Chỗ hai tầng cùng bắt được và chỗ chỉ một tầng bắt được chính là dữ liệu dựng bảng phân loại ở mục 8.

### Bỏ qua một phát hiện

Thêm chú thích ngay trên dòng bị báo:

```
// nosemgrep: <check_id>
```

Luôn ghi lý do bỏ qua ở cùng dòng, và vẫn đếm phát hiện đó vào số báo động giả.

---

## 4. Chạy tự động

### 4a. Chặn trước khi commit

Ngăn khoá bí mật bị commit — nhanh nhất và quan trọng nhất, vì khoá đã vào lịch sử thì không rút lại được:

```bash
cat > .git/hooks/pre-commit <<'EOF'
#!/bin/sh
gitleaks protect --staged --verbose || {
  echo "Phát hiện khả năng rò rỉ khoá bí mật. Commit bị chặn."
  exit 1
}
EOF
chmod +x .git/hooks/pre-commit
```

### 4b. Chạy đầy đủ theo lệnh một dòng

Thêm vào `package.json` (dự án Node.js) để mỗi lần quét chỉ cần một lệnh:

```json
{
  "scripts": {
    "quet": "gitleaks dir . && trivy fs . --scanners vuln --severity HIGH,CRITICAL && semgrep --config=p/security-audit ."
  }
}
```

Chạy: `npm run quet`

### 4c. Chạy tự động trên GitHub

Nếu mã nguồn đặt trên GitHub, tạo `.github/workflows/quet.yml`:

```yaml
name: quet-tu-dong
on: [push, pull_request]
jobs:
  quet:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          severity: HIGH,CRITICAL
      - uses: semgrep/semgrep-action@v1
        with:
          config: p/security-audit
```

Lưu ý: cấu hình này đưa mã nguồn lên dịch vụ chạy của GitHub. **Chỉ dùng khi đã được đơn vị thực tập xác nhận phạm vi dữ liệu được phép đưa ra ngoài** (rủi ro số 1, mục 9 của kế hoạch). Chưa xác nhận thì chỉ chạy cục bộ theo mục 4a và 4b.

---

## 5. Thứ tự chạy cho mỗi tính năng

1. Hoàn thành tính năng, chạy thử bằng tay.
2. **Điền cột *Kiểm tra bằng mắt* vào `nhat-ky.csv` — làm bước này trước bước 3.** Điền sau khi đã thấy kết quả quét thì toàn bộ cột đối chứng mất giá trị (mục 5.1 của kế hoạch).
3. Chạy `gitleaks` → `trivy` → `semgrep`.
4. Ghi tất cả phát hiện vào cột *Quét tự động phát hiện*. Ghi cả phát hiện mà sau đó xác định là báo động giả, có đánh dấu.
5. Không tự kết luận phát hiện nào là đúng hay sai ở bước này (quy tắc A.1). Việc phân loại làm khi tổng hợp ở việc T6.

---

## 6. Ghi nhận khi cài đặt

Lần cài đầu tiên, ghi lại ba thông tin sau để đưa vào báo cáo:

- Phiên bản của từng công cụ (`gitleaks version`, `semgrep --version`, `trivy --version`).
- Thời gian cài đặt và cấu hình, tính bằng phút.
- Thời gian chạy một lượt quét đầy đủ, tính bằng giây.

Mục 5.2 của kế hoạch nói Tầng 1 là *"chi phí thấp nhất, phát hiện loại lỗi tốn kém nhất"*. Ba con số trên là bằng chứng cho mệnh đề đó — không có chúng thì mệnh đề chỉ là nhận định.
