from __future__ import annotations

from decimal import Decimal, InvalidOperation
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

DEFAULT_BUDGETS = {
    "住宿": Decimal("900"),
    "吃": Decimal("600"),
    "交通": Decimal("500"),
    "购物": Decimal("500"),
}


def parse_amount(value: str | None) -> Decimal:
    if value is None:
        return Decimal("0")
    try:
        amount = Decimal(value.strip())
    except (InvalidOperation, AttributeError):
        return Decimal("0")
    return amount if amount >= 0 else Decimal("0")


def make_html(salary: Decimal, budgets: dict[str, Decimal], total: Decimal, remaining: Decimal) -> str:
    budget_rows = "".join(
        f"""
        <div class=\"budget-item\">
            <input name=\"label\" value=\"{escape(label)}\" placeholder=\"标签名称\" required />
            <input name=\"amount\" type=\"number\" min=\"0\" step=\"0.01\" value=\"{amount}\" placeholder=\"金额\" required />
        </div>
        """
        for label, amount in budgets.items()
    )

    negative_class = "negative" if remaining < 0 else ""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>每月工资理财本</title>
<style>
:root {{ --paper:#f7f0d8; --line:#cad6f0; --ink:#3a2f2f; --accent:#a9685f; --accent-dark:#7f4f48; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; font-family:"Segoe UI","PingFang SC",sans-serif; color:var(--ink); background:linear-gradient(140deg,#d9c9ab,#b7a48a); min-height:100vh; display:grid; place-items:center; padding:24px; }}
.notebook {{ width:min(780px,100%); background:repeating-linear-gradient(to bottom,transparent 0,transparent 37px,var(--line) 38px,var(--line) 39px),var(--paper); border-radius:12px; padding:28px 32px; box-shadow:0 20px 50px rgba(30,20,10,.25); border:1px solid #dbc89e; position:relative; }}
.notebook::before {{ content:""; position:absolute; top:0; left:56px; bottom:0; width:2px; background:rgba(182,88,79,.55); }}
header h1 {{ margin:0; font-size:1.8rem; }}
header p {{ margin-top:8px; margin-bottom:20px; color:#604f4f; }}
.salary-row,.budget-item {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px; }}
.salary-row label {{ grid-column:1 / -1; font-weight:600; }}
input {{ height:38px; border:1px solid #9f8c75; border-radius:8px; padding:8px 10px; background:rgba(255,255,255,.78); color:var(--ink); }}
button {{ border:none; border-radius:8px; padding:10px 14px; cursor:pointer; font-size:.95rem; }}
.primary {{ background:var(--accent); color:#fff; margin-top:8px; }}
.primary:hover {{ background:var(--accent-dark); }}
.secondary {{ margin:6px 0 16px; background:#ece3cc; color:#4d3f3f; border:1px solid #b4a078; }}
.result {{ margin-top:20px; padding-top:10px; }}
.remaining {{ font-size:1.2rem; }}
.negative {{ color:#a53b3b; }}
</style>
</head>
<body>
<main class="notebook">
<header>
<h1>每月工资理财分布</h1>
<p>像记账本一样，记录并分配你的每月花销。</p>
</header>
<form method="post">
<section class="salary-row">
<label for="salary">本月工资（元）</label>
<input id="salary" name="salary" type="number" step="0.01" min="0" value="{salary}" placeholder="例如 8000" />
</section>
<section>
<h2>预算标签</h2>
<div id="budget-list">{budget_rows}</div>
<button class="secondary" type="button" id="add-item">+ 添加自定义标签</button>
</section>
<button class="primary" type="submit">计算剩余金额</button>
</form>
<section class="result">
<h2>结算结果</h2>
<p>总预算支出：<strong>{total} 元</strong></p>
<p class="remaining {negative_class}">本月剩余：<strong>{remaining} 元</strong></p>
</section>
</main>
<script>
const addBtn=document.getElementById('add-item');
const list=document.getElementById('budget-list');
addBtn.addEventListener('click',()=>{{
const row=document.createElement('div');
row.className='budget-item';
row.innerHTML=`<input name="label" placeholder="例如：玩乐 / 早餐 / 下馆子" required />\n<input name="amount" type="number" min="0" step="0.01" value="0" placeholder="金额" required />`;
list.appendChild(row);
}});
</script>
</body></html>"""


class FinanceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.render_page(Decimal("0"), DEFAULT_BUDGETS.copy())

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_data = self.rfile.read(content_length).decode("utf-8")
        form = parse_qs(raw_data)

        salary = parse_amount(form.get("salary", ["0"])[0])
        labels = form.get("label", [])
        amounts = form.get("amount", [])

        budgets = DEFAULT_BUDGETS.copy()
        for i, label in enumerate(labels):
            clean_label = label.strip()
            if not clean_label:
                continue
            budgets[clean_label] = parse_amount(amounts[i] if i < len(amounts) else "0")

        self.render_page(salary, budgets)

    def render_page(self, salary: Decimal, budgets: dict[str, Decimal]):
        total = sum(budgets.values(), Decimal("0"))
        remaining = salary - total
        html = make_html(salary, budgets, total, remaining).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), FinanceHandler)
    print("Server running at http://127.0.0.1:8000")
    server.serve_forever()