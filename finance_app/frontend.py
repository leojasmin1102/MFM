from decimal import Decimal
from html import escape

from .domain import FinanceSummary


class FrontendAssets:
    STYLE = """
:root {
  --paper:#f7f0d8;
  --line:#cad6f0;
  --ink:#3a2f2f;
  --accent:#a9685f;
  --accent-dark:#7f4f48;
}
* { box-sizing: border-box; }
body {
  margin:0;
  font-family:"Segoe UI","PingFang SC",sans-serif;
  color:var(--ink);
  background:linear-gradient(140deg,#d9c9ab,#b7a48a);
  min-height:100vh;
  padding:20px;
}
main.notebook {
  width:min(1200px,100%);
  margin:0 auto;
  display:grid;
  grid-template-columns: minmax(360px, 430px) minmax(420px, 1fr);
  gap:20px;
}
.panel {
  background:repeating-linear-gradient(to bottom,transparent 0,transparent 37px,var(--line) 38px,var(--line) 39px),var(--paper);
  border-radius:12px;
  padding:24px 28px;
  box-shadow:0 20px 50px rgba(30,20,10,.25);
  border:1px solid #dbc89e;
}
header h1 { margin:0; font-size:1.8rem; }
header p { margin:8px 0 18px; color:#604f4f; }
.salary-row,.budget-item { display:grid; grid-template-columns:1fr; gap:10px; margin-bottom:12px; }
#budget-list { max-height:300px; overflow:auto; padding-right:4px; }
.budget-item { grid-template-columns:1.2fr 1.5fr 1fr; }
input {
  height:38px;
  border:1px solid #9f8c75;
  border-radius:8px;
  padding:8px 10px;
  background:rgba(255,255,255,.78);
  color:var(--ink);
}
button { border:none; border-radius:8px; padding:10px 14px; cursor:pointer; font-size:.95rem; }
.primary { background:var(--accent); color:#fff; margin-top:8px; }
.primary:hover { background:var(--accent-dark); }
.secondary { margin:6px 0 16px; background:#ece3cc; color:#4d3f3f; border:1px solid #b4a078; }
.result { margin-top:14px; }
.remaining { font-size:1.2rem; }
.negative { color:#a53b3b; }
#advice-content {
  margin-top:10px;
  padding:10px 12px;
  border-radius:8px;
  background:rgba(255,255,255,.55);
  border:1px dashed #b4a078;
  white-space:pre-wrap;
  line-height:1.55;
  min-height:54px;
}
.viewer {
  background: radial-gradient(circle at top, #f0e2cc, #ccb08e);
  border-radius:12px;
  border:1px solid #9f8869;
  box-shadow:0 20px 50px rgba(30,20,10,.25);
  padding:12px;
  display:flex;
  flex-direction:column;
  gap:10px;
}
#notebook-canvas {
  width:100%;
  min-height:640px;
  border-radius:10px;
  overflow:hidden;
}
.flip-controls {
  display:flex;
  justify-content:flex-end;
  gap:10px;
}
@media (max-width: 980px) {
  main.notebook { grid-template-columns:1fr; }
  #notebook-canvas { min-height:520px; }
}
"""


class FinancePageRenderer:
    @staticmethod
    def _budget_rows(budgets: dict[str, Decimal]) -> str:
        return "".join(
            f"""
            <div class=\"budget-item\">
                <input name=\"date\" type=\"date\" value=\"2026-03-01\" required />
                <input name=\"description\" value=\"{escape(label)}\" placeholder=\"Description\" required />
                <input name=\"amount\" type=\"number\" min=\"0\" step=\"0.01\" value=\"{amount}\" placeholder=\"金额\" required />
            </div>
            """
            for label, amount in budgets.items()
        )

    def render(self, summary: FinanceSummary) -> str:
        return f"""<!DOCTYPE html>
<html lang=\"zh-CN\">
<head>
<meta charset=\"UTF-8\" />
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
<title>每月工资理财本</title>
<style>{FrontendAssets.STYLE}</style>
</head>
<body>
<main class=\"notebook\">
<section class=\"panel\">
<header>
<h1>每月工资理财分布</h1>
<p>把流水写进 3D 皮革账本。点击右侧翻到下一页，点击左侧回到上一页。</p>
</header>
<section class=\"salary-row\">
<label for=\"salary\">本月工资（元）</label>
<input id=\"salary\" name=\"salary\" type=\"number\" step=\"0.01\" min=\"0\" value=\"{summary.salary}\" placeholder=\"例如 8000\" />
</section>
<section>
<h2>记账记录</h2>
<div id=\"budget-list\">{self._budget_rows(summary.budgets)}</div>
<button class=\"secondary\" type=\"button\" id=\"add-item\">+ 添加记录页</button>
</section>
<button class=\"primary\" type=\"button\" id=\"calculate-btn\">计算剩余金额</button>
<button class=\"secondary\" type=\"button\" id=\"advice-btn\">AI 消费建议</button>
<section class=\"result\">
<h2>结算结果</h2>
<p>总预算支出：<strong id=\"total-amount\">{summary.total} 元</strong></p>
<p class=\"remaining {'negative' if summary.remaining < 0 else ''}\">本月剩余：<strong id=\"remaining-amount\">{summary.remaining} 元</strong></p>
</section>

<dialog id=\"advice-dialog\">
  <h3>AI 大模型消费建议</h3>
  <div id=\"advice-content\">暂无建议</div>
  <details class=\"advice-wrap\">
    <summary>查看发送给大模型的提示词</summary>
    <pre id=\"advice-prompt\"></pre>
  </details>
  <button class=\"secondary\" type=\"button\" id=\"close-advice-btn\">关闭</button>
</dialog>
</section>

<section class=\"viewer\">
  <div class=\"flip-controls\">
    <button class=\"secondary\" type=\"button\" id=\"flip-prev\">上一页</button>
    <button class=\"secondary\" type=\"button\" id=\"flip-next\">下一页</button>
  </div>
  <div id=\"notebook-canvas\"></div>
</section>
</main>
<script type=\"module\" src=\"/static/js/app.js\"></script>
</body>
</html>"""