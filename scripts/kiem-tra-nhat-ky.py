#!/usr/bin/env python3
"""Kiểm tra nhat-ky.csv theo các quy tắc của mục 5.1 và A.1 trong kế hoạch.

Cách dùng:
    python3 scripts/kiem-tra-nhat-ky.py [đường dẫn tệp]       # mặc định: nhat-ky.csv
    python3 scripts/kiem-tra-nhat-ky.py --da-dien <tên tính năng>

Lệnh thứ hai chỉ trả về mã 0 khi tính năng đó đã có dòng trong nhật ký và cột
"Kiểm tra bằng mắt" đã được điền. scripts/quet.sh dùng lệnh này để chặn việc
chạy quét trước khi con người ghi kết quả kiểm tra bằng mắt.

Script chỉ đọc, không bao giờ sửa nhật ký.
"""
import csv
import sys
import unicodedata
from pathlib import Path

COT = [
    "Tính năng",
    "Yêu cầu",
    "Số vòng prompt",
    "Thời gian",
    "Kiểm tra bằng mắt",
    "Quét tự động phát hiện",
    "AI rà soát phát hiện",
    "Lỗi phát hiện về sau",
]
COT_MAT = "Kiểm tra bằng mắt"
COT_SAU_MAT = ["Quét tự động phát hiện", "AI rà soát phát hiện", "Lỗi phát hiện về sau"]
GIA_TRI_MAT = {"Đạt", "Không đạt"}


def chuan(s):
    # macOS và một số trình soạn thảo lưu tiếng Việt dạng NFD; so sánh theo NFC.
    return unicodedata.normalize("NFC", (s or "").strip())


def doc(duong_dan):
    with open(duong_dan, encoding="utf-8-sig", newline="") as f:
        hang = list(csv.reader(f))
    if not hang:
        return None, []
    tieu_de = [chuan(c) for c in hang[0]]
    du_lieu = [[chuan(c) for c in h] for h in hang[1:]]
    return tieu_de, du_lieu


def kiem_tra(duong_dan):
    loi = []
    tieu_de, du_lieu = doc(duong_dan)
    if tieu_de is None:
        return ["Tệp rỗng, thiếu dòng tiêu đề."]
    if tieu_de != COT:
        loi.append(
            "Tiêu đề cột không khớp 8 cột ở mục 5.1.\n"
            f"    Cần:   {','.join(COT)}\n"
            f"    Đang có: {','.join(tieu_de)}"
        )
        return loi

    i_mat = COT.index(COT_MAT)
    ten_da_gap = {}
    for so, h in enumerate(du_lieu, start=2):
        if not any(h):
            loi.append(f"Dòng {so}: dòng trống, hãy xoá.")
            continue
        if len(h) != len(COT):
            loi.append(f"Dòng {so}: có {len(h)} ô, cần đúng {len(COT)} ô.")
            continue
        o = dict(zip(COT, h))
        ten = o["Tính năng"]
        if not ten:
            loi.append(f"Dòng {so}: thiếu tên tính năng.")
        elif ten in ten_da_gap:
            loi.append(f"Dòng {so}: trùng tên tính năng với dòng {ten_da_gap[ten]} ('{ten}').")
        else:
            ten_da_gap[ten] = so

        mat = h[i_mat]
        if mat and mat not in GIA_TRI_MAT:
            loi.append(f"Dòng {so}: cột '{COT_MAT}' chỉ nhận 'Đạt' hoặc 'Không đạt', đang là '{mat}'.")
        if not mat:
            da_co = [c for c in COT_SAU_MAT if o[c]]
            if da_co:
                loi.append(
                    f"Dòng {so} ('{ten}'): đã có dữ liệu ở {', '.join(da_co)} "
                    f"nhưng cột '{COT_MAT}' còn trống. Cột này phải điền TRƯỚC khi quét (mục 5.1)."
                )
    return loi


def da_dien(duong_dan, ten):
    tieu_de, du_lieu = doc(duong_dan)
    if tieu_de != COT:
        return False
    i_mat = COT.index(COT_MAT)
    ten = chuan(ten)
    return any(len(h) == len(COT) and h[0] == ten and h[i_mat] in GIA_TRI_MAT for h in du_lieu)


def main(argv):
    if len(argv) >= 2 and argv[0] == "--da-dien":
        tep = argv[2] if len(argv) > 2 else "nhat-ky.csv"
        return 0 if da_dien(tep, argv[1]) else 1

    tep = argv[0] if argv else "nhat-ky.csv"
    if not Path(tep).exists():
        print(f"Không tìm thấy {tep}.", file=sys.stderr)
        return 2
    loi = kiem_tra(tep)
    if loi:
        print(f"{tep}: {len(loi)} vấn đề")
        for l in loi:
            print(f"  - {l}")
        return 1
    print(f"{tep}: hợp lệ.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
