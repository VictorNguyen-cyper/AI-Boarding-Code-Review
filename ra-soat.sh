#!/bin/sh
# Chuẩn bị rà soát Tầng 3 trên web Gemini theo checklist.md — xem ra-soat-ai.md.
# Dùng: ./ra-soat.sh <tên-tính-năng> <tệp-yêu-cầu> <thư-mục-mã>
# Tạo: dau-vao/ra-soat-<tên>.txt (tải lên Gemini, không commit) và ra-soat-<tên>.md (khung để dán kết quả).
set -eu

if [ $# -ne 3 ]; then
  echo "Dùng: $0 <tên-tính-năng> <tệp-yêu-cầu> <thư-mục-mã>" >&2
  exit 2
fi

TEN=$1
YEU_CAU=$2
MA=$3
GOC=$(cd "$(dirname "$0")" && pwd)
RA="$GOC/ra-soat-$TEN.md"
DAU_VAO="$GOC/dau-vao/ra-soat-$TEN.txt"

[ -f "$YEU_CAU" ] || { echo "Không thấy tệp yêu cầu: $YEU_CAU" >&2; exit 1; }
[ -d "$MA" ] || { echo "Không thấy thư mục mã: $MA" >&2; exit 1; }
[ -e "$RA" ] && { echo "Đã có $RA — không ghi đè kết quả rà soát cũ." >&2; exit 1; }

# Tệp bí mật chỉ đưa tên (để xét C01), không bao giờ đưa nội dung ra ngoài.
la_tep_bi_mat() {
  case "$(basename "$1")" in
    .env|.env.*|*.pem|*.key|*.p12|*.pfx|id_rsa*|id_ed25519*) return 0 ;;
  esac
  return 1
}

DS_TEP=$(find "$MA" -type f \
  -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/dist/*' \
  -not -path '*/build/*' -not -path '*/.next/*' -not -path '*/venv/*' \
  -not -path '*/.venv/*' -not -path '*/__pycache__/*' | sort)

mkdir -p "$GOC/dau-vao"

LENH='Bạn là người rà soát Tầng 3 của một quy trình nghiệm thu phần mềm. Mã nguồn bên dưới do một mô hình AI khác sinh ra.

Tệp này gồm: CHECKLIST, TÀI LIỆU YÊU CẦU, DANH SÁCH TỆP, rồi nội dung từng tệp mã.

Việc cần làm: rà mã nguồn theo đúng 12 tiêu chí C01–C12 trong CHECKLIST, đối chiếu với TÀI LIỆU YÊU CẦU.

Quy tắc bắt buộc:
- Chỉ rà theo 12 tiêu chí. Không nhận xét chung về chất lượng mã nguồn, cách đặt tên, cách trình bày.
- Không tự kết luận phát hiện là đúng hay sai, không đánh giá tính năng đạt hay không đạt. Chỉ ghi dấu hiệu quan sát được; việc phân loại thuộc về con người.
- Không trích nguyên văn giá trị khoá bí mật, mật khẩu, chuỗi kết nối. Chỉ ghi vị trí.
- Không đưa tên khách hàng, tên công ty hay tên dự án nội bộ vào đầu ra.
- Không bịa vị trí. Mọi vị trí phải là tệp và dòng có thật trong đầu vào.
- Nếu đầu vào không đủ để xét một tiêu chí (ví dụ không có mã phía máy chủ), ghi "Không đủ thông tin" và nêu cần thêm gì. Không suy đoán.
- Không viết lại hay sửa mã nguồn.

Định dạng đầu ra (Markdown, tiếng Việt):

## Tổng quan theo tiêu chí

| Mã | Trả lời (Có / Không / Không đủ thông tin) | Số phát hiện |
| --- | --- | --- |
(đủ 12 dòng C01–C12)

## Phát hiện

Mỗi phát hiện theo đúng mẫu:

- Tiêu chí: <mã>
  Vị trí: <tệp:dòng hoặc hàm>
  Mức nghiêm trọng: Cao / Trung bình / Thấp (theo thang trong CHECKLIST)
  Mô tả dấu hiệu: <1-2 câu>

Không có phát hiện thì ghi "Không có phát hiện".

## Câu hỏi còn mở

Liệt kê thông tin còn thiếu để rà soát đầy đủ. Không có thì ghi "Không có".'

{
  echo "===== HƯỚNG DẪN ====="
  echo "$LENH"
  echo
  echo "===== CHECKLIST ====="
  cat "$GOC/checklist.md"
  echo
  echo "===== TÀI LIỆU YÊU CẦU ====="
  cat "$YEU_CAU"
  echo
  echo "===== DANH SÁCH TỆP ====="
  echo "$DS_TEP"
  echo
  echo "$DS_TEP" | while IFS= read -r t; do
    [ -n "$t" ] || continue
    if la_tep_bi_mat "$t"; then
      echo "===== TỆP: $t (tệp bí mật — nội dung không được gửi) ====="
    elif grep -Iq '' "$t" 2>/dev/null; then
      echo "===== TỆP: $t ====="
      cat "$t"
      echo
    fi
  done
} > "$DAU_VAO"

SO_TEP=$(echo "$DS_TEP" | grep -c . || true)

{
  echo "# Rà soát Tầng 3 — $TEN"
  echo
  echo "- Mô hình: *(điền đúng tên đã ghi ở ra-soat-ai.md mục 2)*"
  echo "- Ngày chạy: $(date '+%Y-%m-%d')"
  echo "- Tệp yêu cầu: $(basename "$YEU_CAU")"
  echo "- Số tệp mã gửi đi: $SO_TEP"
  echo "- Thời gian chờ Gemini trả lời: *(điền, tính bằng giây)*"
  echo
  echo "> Kết quả dưới đây do AI sinh ra, chưa được con người phân loại đúng/sai."
  echo
  echo "<!-- Dán nguyên văn câu trả lời của Gemini vào dưới dòng này. Không sửa, không chạy lại để lấy kết quả khác. -->"
} > "$RA"

echo "Đã tạo:"
echo "  $DAU_VAO  — tải tệp này lên gemini.google.com (không commit tệp này)"
echo "  $RA  — dán câu trả lời của Gemini vào đây"
