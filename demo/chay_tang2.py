# DEMO — chạy tự động các tình huống Tầng 2 cho tính năng "Xem đơn hàng".
# Tình huống sinh từ mô tả yêu cầu theo 6 nhóm của mau/test-case-mau.md.
import json
import sqlite3
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "app"))
import app as demo  # noqa: E402

AN = {"Authorization": "Bearer token-an"}
MOI = {"Authorization": "Bearer token-moi"}


def moi_db():
    tep = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
    conn = sqlite3.connect(tep)
    demo.init_db(conn)
    conn.commit()
    conn.close()
    demo.app.config.update(DB=tep, TESTING=False, PROPAGATE_EXCEPTIONS=False)
    return demo.app.test_client()


def tom(r):
    body = r.get_data(as_text=True).strip().replace("\n", " ")
    return f"{r.status_code} {body[:70]}"


ca = []


def tc(ma, nhom, buoc, mong_doi, ham):
    c = moi_db()
    try:
        thuc_te, dat = ham(c)
    except Exception as e:  # lỗi của chính bước thử
        thuc_te, dat = f"lỗi khi thử: {e}", False
    ca.append((ma, nhom, buoc, mong_doi, thuc_te, dat))


# 1. Luồng chính
tc("TC-01", "Luồng chính", "An xem danh sách đơn", "200, 2 đơn chưa xoá của An",
   lambda c: (lambda r: (f"{r.status_code}, {len(r.json)} đơn", r.status_code == 200 and len(r.json) == 2))(c.get("/orders", headers=AN)))
tc("TC-02", "Luồng chính", "An xem chi tiết đơn 1", "200, đơn 1",
   lambda c: (lambda r: (tom(r), r.status_code == 200 and r.json["id"] == 1))(c.get("/orders/1", headers=AN)))
tc("TC-03", "Luồng chính", "An tạo đơn mới", "201, có id",
   lambda c: (lambda r: (tom(r), r.status_code == 201))(c.post("/orders", headers=AN, json={"note": "mới"})))


def tc04(c):
    r = c.get("/stats", headers=AN)
    # An có 2 đơn chưa xoá, 1 đơn done -> yêu cầu nói "không gồm đơn đã xoá" -> 50.0
    return f"{r.status_code} total={r.json['total']} rate={r.json['rate']}", r.json["total"] == 2 and r.json["rate"] == 50.0


tc("TC-04", "Luồng chính", "An xem tỷ lệ hoàn thành", "total=2, rate=50.0 (không tính đơn đã xoá)", tc04)

# 2. Dữ liệu rỗng
tc("TC-11", "Dữ liệu rỗng", "Tài khoản mới xem danh sách", "200, danh sách rỗng",
   lambda c: (lambda r: (tom(r), r.status_code == 200 and r.json == []))(c.get("/orders", headers=MOI)))
tc("TC-12", "Dữ liệu rỗng", "Tài khoản mới xem thống kê", "200, rate=0 hoặc thông báo chưa có dữ liệu",
   lambda c: (lambda r: (tom(r), r.status_code == 200))(c.get("/stats", headers=MOI)))

# 3. Dữ liệu sai
tc("TC-21", "Dữ liệu sai", "An mở đơn 4 (của Bình) bằng cách sửa ID", "403 hoặc 404",
   lambda c: (lambda r: (tom(r), r.status_code in (403, 404)))(c.get("/orders/4", headers=AN)))
tc("TC-22", "Dữ liệu sai", "Tạo đơn thiếu trường note", "400, báo thiếu trường",
   lambda c: (lambda r: (tom(r), r.status_code == 400))(c.post("/orders", headers=AN, json={})))
tc("TC-23", "Dữ liệu sai", "Tạo đơn với note dài 100 000 ký tự", "400, báo quá dài",
   lambda c: (lambda r: (tom(r), r.status_code == 400))(c.post("/orders", headers=AN, json={"note": "x" * 100000})))


# 4. Mạng chậm / phụ thuộc lỗi
def tc31(c):
    r = c.get("/orders/1/tracking", headers=AN)
    lo = "127.0.0.1" in r.get_data(as_text=True)
    return tom(r) + (" (lộ URL nội bộ)" if lo else ""), r.status_code in (502, 503) and not lo


tc("TC-31", "Mạng chậm", "Dịch vụ vận chuyển không kết nối được", "502/503, thông báo chung, không lộ địa chỉ nội bộ", tc31)


def tc32(c):
    # Giả lập dịch vụ treo: socket nhận kết nối nhưng không bao giờ trả lời.
    import socket
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    s.listen()
    demo.SHIPPING_URL = f"http://127.0.0.1:{s.getsockname()[1]}/track"
    kq = {}

    def goi():
        t0 = time.time()
        kq["r"] = c.get("/orders/1/tracking", headers=AN)
        kq["t"] = time.time() - t0

    th = threading.Thread(target=goi, daemon=True)
    th.start()
    th.join(8)
    demo.SHIPPING_URL = "http://127.0.0.1:9/track"
    if th.is_alive():
        return "vẫn chờ sau 8 giây, không có giới hạn thời gian chờ", False
    return f"{tom(kq['r'])} sau {kq['t']:.1f}s", kq["t"] < 8


tc("TC-32", "Mạng chậm", "Dịch vụ vận chuyển treo không trả lời", "Trả lỗi trong vài giây", tc32)


# 5. Thao tác trùng
def tc41(c):
    c.post("/orders", headers=AN, json={"note": "bấm 2 lần"})
    c.post("/orders", headers=AN, json={"note": "bấm 2 lần"})
    n = len([o for o in c.get("/orders", headers=AN).json if o["note"] == "bấm 2 lần"])
    return f"tạo ra {n} đơn", n == 1


tc("TC-41", "Thao tác trùng", "Bấm Gửi hai lần với cùng nội dung", "Chỉ 1 đơn được tạo", tc41)

# 6. Phiên hết hạn
tc("TC-51", "Phiên hết hạn", "Gọi /orders không có token", "401, thông báo cần đăng nhập",
   lambda c: (lambda r: (tom(r), r.status_code == 401))(c.get("/orders")))
tc("TC-52", "Phiên hết hạn", "Gọi /orders với token đã hết hạn", "401, thông báo phiên hết hạn",
   lambda c: (lambda r: (tom(r), r.status_code == 401))(c.get("/orders", headers={"Authorization": "Bearer het-han"})))

# Xuất bảng
dong = ["| Mã | Nhóm | Bước thao tác | Kết quả mong đợi | Kết quả thực tế | Đạt? |", "| --- | --- | --- | --- | --- | --- |"]
for ma, nhom, buoc, md, tt, dat in ca:
    tt = tt.replace("|", "\\|")
    dong.append(f"| {ma} | {nhom} | {buoc} | {md} | {tt} | {'Đạt' if dat else '**Không đạt**'} |")
so_dat = sum(1 for x in ca if x[5])
print("\n".join(dong))
print(f"\nTổng: {len(ca)} — đạt: {so_dat} — không đạt: {len(ca) - so_dat}")
json.dump([dict(zip(["ma", "nhom", "buoc", "mong_doi", "thuc_te", "dat"], x)) for x in ca],
          open(Path(__file__).parent / "tang2.json", "w"), ensure_ascii=False, indent=1)
