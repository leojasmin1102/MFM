from decimal import Decimal
from html import escape

from .domain import FinanceSummary


class FrontendAssets:
    STYLE = """
:root { --paper:#f7f0d8; --line:#cad6f0; --ink:#3a2f2f; --accent:#a9685f; --accent-dark:#7f4f48; }
* { box-sizing: border-box; }
body { margin:0; font-family:"Segoe UI","PingFang SC",sans-serif; color:var(--ink); background:linear-gradient(140deg,#d9c9ab,#b7a48a); min-height:100vh; display:grid; place-items:center; padding:24px; }
.notebook { width:min(780px,100%); background:repeating-linear-gradient(to bottom,transparent 0,transparent 37px,var(--line) 38px,var(--line) 39px),var(--paper); border-radius:12px; padding:28px 32px; box-shadow:0 20px 50px rgba(30,20,10,.25); border:1px solid #dbc89e; position:relative; }
header h1 { margin:0; font-size:1.8rem; }
header p { margin-top:8px; margin-bottom:20px; color:#604f4f; }
.salary-row,.budget-item { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px; }
.salary-row label { grid-column:1 / -1; font-weight:600; }
input { height:38px; border:1px solid #9f8c75; border-radius:8px; padding:8px 10px; background:rgba(255,255,255,.78); color:var(--ink); }
button { border:none; border-radius:8px; padding:10px 14px; cursor:pointer; font-size:.95rem; }
.primary { background:var(--accent); color:#fff; margin-top:8px; }
.primary:hover { background:var(--accent-dark); }
.secondary { margin:6px 0 16px; background:#ece3cc; color:#4d3f3f; border:1px solid #b4a078; }
.result { margin-top:20px; padding-top:10px; }
.remaining { font-size:1.2rem; }
.negative { color:#a53b3b; }
.advice-wrap { margin-top:16px; }
#advice-content { margin-top:10px; padding:10px 12px; border-radius:8px; background:rgba(255,255,255,.55); border:1px dashed #b4a078; white-space:pre-wrap; line-height:1.55; min-height:54px; }
"""

    SCRIPT = """
const addBtn = document.getElementById('add-item');
const calculateBtn = document.getElementById('calculate-btn');
const adviceBtn = document.getElementById('advice-btn');
const salaryInput = document.getElementById('salary');
const list = document.getElementById('budget-list');
const totalText = document.getElementById('total-amount');
const remainingText = document.getElementById('remaining-amount');
const adviceDialog = document.getElementById('advice-dialog');
const adviceText = document.getElementById('advice-content');
const advicePrompt = document.getElementById('advice-prompt');
const closeAdviceBtn = document.getElementById('close-advice-btn');

function createBudgetRow(label = '', amount = '0') {
  const row = document.createElement('div');
  row.className = 'budget-item';
  row.innerHTML = `<input name="label" value="${label}" placeholder="例如：玩乐 / 早餐 / 下馆子" required />\n<input name="amount" type="number" min="0" step="0.01" value="${amount}" placeholder="金额" required />`;
  return row;
}

function collectBudgets() {
  const rows = [...list.querySelectorAll('.budget-item')];
  return rows.map((row) => {
    const label = row.querySelector('input[name="label"]').value;
    const amount = row.querySelector('input[name="amount"]').value;
    return { label, amount };
  });
}

function renderResult(result) {
  totalText.textContent = `${result.total} 元`;
  remainingText.textContent = `${result.remaining} 元`;
  remainingText.classList.toggle('negative', result.remaining.startsWith('-'));
}

addBtn.addEventListener('click', () => {
  list.appendChild(createBudgetRow());
});

calculateBtn.addEventListener('click', async () => {
  const payload = {
    salary: salaryInput.value,
    budgets: collectBudgets(),
  };

  const response = await fetch('/api/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  renderResult(data);
});


adviceBtn.addEventListener('click', async () => {
  const payload = {
    salary: salaryInput.value,
    budgets: collectBudgets(),
  };

  adviceBtn.disabled = true;
  adviceBtn.textContent = '生成中...';

  const response = await fetch('/api/advice', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  adviceText.textContent = data.advice;
  advicePrompt.textContent = data.prompt;
  adviceDialog.showModal();

  adviceBtn.disabled = false;
  adviceBtn.textContent = 'AI 消费建议';
});

closeAdviceBtn.addEventListener('click', () => {
  adviceDialog.close();
});
"""


class FinancePageRenderer:
    @staticmethod
    def _budget_rows(budgets: dict[str, Decimal]) -> str:
        return "".join(
            f"""
            <div class=\"budget-item\">
                <input name=\"label\" value=\"{escape(label)}\" placeholder=\"标签名称\" required />
                <input name=\"amount\" type=\"number\" min=\"0\" step=\"0.01\" value=\"{amount}\" placeholder=\"金额\" required />
            </div>
            """
            for label, amount in budgets.items()
        )

    def render(self, summary: FinanceSummary) -> str:
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>每月工资理财本</title>
<style>{FrontendAssets.STYLE}</style>
</head>
<body>
<main class="notebook">
<header>
<h1>每月工资理财分布</h1>
<p>像记账本一样，记录并分配你的每月花销。</p>
</header>
<section class="salary-row">
<label for="salary">本月工资（元）</label>
<input id="salary" name="salary" type="number" step="0.01" min="0" value="{summary.salary}" placeholder="例如 8000" />
</section>
<section>
<h2>预算标签</h2>
<div id="budget-list">{self._budget_rows(summary.budgets)}</div>
<button class="secondary" type="button" id="add-item">+ 添加自定义标签</button>
</section>
<button class="primary" type="button" id="calculate-btn">计算剩余金额</button>
<button class="secondary" type="button" id="advice-btn">AI 消费建议</button>
<section class="result">
<h2>结算结果</h2>
<p>总预算支出：<strong id="total-amount">{summary.total} 元</strong></p>
<p class="remaining {'negative' if summary.remaining < 0 else ''}">本月剩余：<strong id="remaining-amount">{summary.remaining} 元</strong></p>
</section>

<dialog id="advice-dialog">
  <h3>AI 大模型消费建议</h3>
  <div id="advice-content">暂无建议</div>
  <details class="advice-wrap">
    <summary>查看发送给大模型的提示词</summary>
    <pre id="advice-prompt"></pre>
  </details>
  <button class="secondary" type="button" id="close-advice-btn">关闭</button>
</dialog>

</main>
<script>{FrontendAssets.SCRIPT}</script>
</body>
</html>"""