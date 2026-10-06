#!/bin/sh
# Chạy đủ ba công cụ quét Tầng 1 cho một tính năng, theo thứ tự ở mục 5 của
# quet-tu-dong.md: gitleaks -> trivy -> semgrep.
#
# Cách dùng:
#   scripts/quet.sh "<tên tính năng>" [thư mục mã nguồn]    # mặc định: .
#
# Kết quả nằm trong ket-qua-quet/<tên tính năng>/:
#   bao-cao-gitleaks.json, bao-cao-trivy.json, bao-cao-semgrep.json
#   tom-tat.txt  — từng phát hiện viết sẵn theo dạng ghi vào cột
#                  "Quét tự động phát hiện" của nhat-ky.csv.
#
# Script KHÔNG ghi vào nhat-ky.csv và KHÔNG kết luận phát hiện nào đúng hay sai
# (quy tắc A.1). Con người tự chép tom-tat.txt vào nhật ký.

set -u

TEN="${1:-}"
NGUON="${2:-.}"
GOC="$(cd "$(dirname "$0")/.." && pwd)"
NHAT_KY="${NHAT_KY:-$GOC/nhat-ky.csv}"

if [ -z "$TEN" ]; then
  echo "Cách dùng: scripts/quet.sh \"<tên tính năng>\" [thư mục mã nguồn]" >&2
  exit 2
fi

# Chặn quét khi chưa ghi kết quả kiểm tra bằng mắt — nếu không, cột đối chứng mất giá trị.
if ! python3 "$GOC/scripts/kiem-tra-nhat-ky.py" --da-dien "$TEN" "$NHAT_KY"; then
  echo "Chưa có dòng '$TEN' trong nhat-ky.csv, hoặc cột 'Kiểm tra bằng mắt' chưa được điền." >&2
  echo "Hãy điền 'Đạt' / 'Không đạt' TRƯỚC khi quét (mục 5.1 của kế hoạch)." >&2
  exit 1
fi

for cong_cu in gitleaks trivy semgrep; do
  command -v "$cong_cu" >/dev/null 2>&1 || {
    echo "Thiếu $cong_cu. Cài theo mục 0 của quet-tu-dong.md." >&2
    exit 2
  }
done

THU_MUC_TEN=$(printf '%s' "$TEN" | tr ' /' '--')
RA="$GOC/ket-qua-quet/$THU_MUC_TEN"
mkdir -p "$RA"

bat_dau=$(date +%s)

echo "[1/3] gitleaks"
# --redact: không để giá trị khoá xuất hiện trong báo cáo.
gitleaks dir "$NGUON" --redact --no-banner --exit-code 0 \
  --report-format json --report-path "$RA/bao-cao-gitleaks.json"

echo "[2/3] trivy"
trivy fs "$NGUON" --scanners vuln --severity HIGH,CRITICAL --quiet \
  --format json --output "$RA/bao-cao-trivy.json"

echo "[3/3] semgrep"
semgrep --config=p/security-audit --config=p/secrets --quiet --metrics=off \
  --json --output="$RA/bao-cao-semgrep.json" "$NGUON"

ket_thuc=$(date +%s)

python3 - "$RA" "$TEN" "$((ket_thuc - bat_dau))" "$(cd "$NGUON" && pwd)" <<'PY'
import json, os, sys
from pathlib import Path

ra, ten, giay, nguon = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]

def tuong_doi(duong_dan):
    # Ghi đường dẫn tương đối với thư mục mã nguồn, không lộ đường dẫn trên máy.
    return os.path.relpath(os.path.abspath(duong_dan), nguon) if duong_dan else duong_dan

def doc(tep):
    p = ra / tep
    if not p.exists() or p.stat().st_size == 0:
        return None
    return json.loads(p.read_text(encoding="utf-8"))

dong = []
# Định dạng từng dòng theo mục 1, 2, 3 của quet-tu-dong.md.
for f in doc("bao-cao-gitleaks.json") or []:
    dong.append(f"gitleaks: {f.get('RuleID')} tại {tuong_doi(f.get('File'))}:{f.get('StartLine')}")
for r in (doc("bao-cao-trivy.json") or {}).get("Results") or []:
    for v in r.get("Vulnerabilities") or []:
        dong.append(f"trivy: {v.get('PkgName')} {v.get('VulnerabilityID')} mức {v.get('Severity')}")
for f in (doc("bao-cao-semgrep.json") or {}).get("results") or []:
    muc = (f.get("extra") or {}).get("severity")
    dong.append(f"semgrep: {f.get('check_id')} tại {tuong_doi(f.get('path'))}:{(f.get('start') or {}).get('line')} mức {muc}")

noi_dung = "\n".join([
    f"Tính năng: {ten}",
    f"Thời gian chạy một lượt quét: {giay} giây",
    f"Số phát hiện: {len(dong)}",
    "",
    "Dán vào cột 'Quét tự động phát hiện' (chưa phân loại đúng / báo động giả):",
    "; ".join(dong) if dong else "(không có phát hiện)",
    "",
    "Từng phát hiện:",
    *[f"- {d}" for d in dong],
]) + "\n"
(ra / "tom-tat.txt").write_text(noi_dung, encoding="utf-8")
print(noi_dung)
PY

echo "Báo cáo đầy đủ: $RA"
