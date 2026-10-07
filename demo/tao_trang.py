# DEMO — dựng demo.html từ bang-doi-chieu-DEMO.md và tang2.json.
import html
import json
import re
from pathlib import Path

d = Path(__file__).parent


def md_table(text):
    lines = [l for l in text.splitlines() if l.startswith("|")]
    rows = [[c.strip() for c in re.split(r"(?<!\\)\|", l)[1:-1]] for l in lines]
    head, body = rows[0], rows[2:]

    def cell(c):
        c = html.escape(c.replace("\\|", "|"))
        c = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", c)
        c = c.replace("✓", '<span class="ok">✓</span>')
        return '<span class="no">—</span>' if c == "—" else c

    t = "<table><thead><tr>" + "".join(f"<th>{html.escape(h)}</th>" for h in head) + "</tr></thead><tbody>"
    for r in body:
        cls = ' class="total"' if "Tổng" in r[1] else ""
        t += f"<tr{cls}>" + "".join(f"<td>{cell(c)}</td>" for c in r) + "</tr>"
    return t + "</tbody></table>"


def bo_escape(s):
    s = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)
    return re.sub(r"<!doctype.*", "trang lỗi HTML Internal Server Error", s)


doi_chieu = md_table((d / "bang-doi-chieu-DEMO.md").read_text(encoding="utf-8"))
t2 = json.load(open(d / "tang2.json", encoding="utf-8"))
t2_html = "<table><thead><tr><th>Mã</th><th>Nhóm</th><th>Bước thao tác</th><th>Mong đợi</th><th>Thực tế</th><th>Kết quả</th></tr></thead><tbody>"
for c in t2:
    badge = '<span class="badge pass">Đạt</span>' if c["dat"] else '<span class="badge fail">Không đạt</span>'
    t2_html += (f"<tr><td>{c['ma']}</td><td>{c['nhom']}</td><td>{html.escape(c['buoc'])}</td>"
                f"<td>{html.escape(c['mong_doi'])}</td><td><code>{html.escape(bo_escape(c['thuc_te']))}</code></td><td>{badge}</td></tr>")
t2_html += "</tbody></table>"
dat = sum(c["dat"] for c in t2)

page = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Demo nghiệm thu 3 tầng</title><style>
:root{{--bg:#f7f7f5;--fg:#1d1d1b;--muted:#6b6b66;--card:#fff;--line:#e3e2dc;--ok:#1f7a4d;--bad:#b3261e;--warn:#8a5a00;--warnbg:#fff4d6}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161615;--fg:#ecebe6;--muted:#a3a29b;--card:#1f1f1d;--line:#34332f;--ok:#5cc28c;--bad:#f0817a;--warn:#f2c46b;--warnbg:#2e2615}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,system-ui,sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:32px 16px 64px}}h1{{font-size:26px;margin:0 0 4px}}h2{{font-size:18px;margin:36px 0 10px}}
.sub{{color:var(--muted);margin:0 0 20px}}.note{{background:var(--warnbg);color:var(--warn);border-radius:8px;padding:12px 14px;font-size:14px}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:20px 0}}
.kpi{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}}.kpi b{{display:block;font-size:28px}}.kpi span{{color:var(--muted);font-size:13px}}
.wrap{{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px}}
table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{padding:9px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}
th{{font-weight:600;color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.03em}}tr:last-child td{{border-bottom:0}}
tr.total td{{font-weight:600;border-top:2px solid var(--line)}}.ok{{color:var(--ok);font-weight:700}}.no{{color:var(--muted)}}
code{{font-size:12.5px;word-break:break-word}}.badge{{font-size:12px;padding:2px 8px;border-radius:99px;white-space:nowrap;font-weight:600}}
.pass{{color:var(--ok);border:1px solid var(--ok)}}.fail{{color:var(--bad);border:1px solid var(--bad)}}
</style></head><body><main>
<h1>Demo quy trình nghiệm thu 3 tầng</h1><p class="sub">Tính năng: <strong>Xem đơn hàng</strong> · chạy ngày 2026-10-06</p>
<p class="note"><strong>DEMO — không phải dữ liệu nghiên cứu.</strong> Lỗi được cố ý cài vào ứng dụng giả lập; mã nguồn và rà soát do cùng một mô hình thực hiện (trái mục 5.3); cột "Kiểm tra bằng mắt" là giả định. Không dùng các con số này trong báo cáo.</p>
<div class="kpis"><div class="kpi"><b>0/11</b><span>Kiểm tra bằng mắt</span></div><div class="kpi"><b>2/11</b><span>Tầng 1 — quét tự động</span></div>
<div class="kpi"><b>9/11</b><span>Tầng 2 — kiểm thử hành vi</span></div><div class="kpi"><b>11/11</b><span>Tầng 3 — rà soát (bị thổi phồng)</span></div></div>
<h2>Bảng đối chiếu</h2><div class="wrap">{doi_chieu}</div>
<h2>Tầng 2 — {len(t2)} tình huống, đạt {dat}, không đạt {len(t2) - dat}</h2><div class="wrap">{t2_html}</div>
<p class="sub" style="margin-top:20px">Chi tiết rà soát Tầng 3: ra-soat-xem-don-hang-DEMO.md · Báo cáo quét: ket-qua-quet/</p>
</main></body></html>"""
(d / "demo.html").write_text(page, encoding="utf-8")
print(d / "demo.html")
