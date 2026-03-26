import { NotebookScene } from '/static/js/scene.js';

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
const flipNextBtn = document.getElementById('flip-next');
const flipPrevBtn = document.getElementById('flip-prev');

const notebookScene = new NotebookScene(document.getElementById('notebook-canvas'));

function todayISO(offset = 0) {
  const d = new Date();
  d.setDate(d.getDate() + offset);
  return d.toISOString().slice(0, 10);
}

function createBudgetRow(date = todayISO(), description = '', amount = '0') {
  const row = document.createElement('div');
  row.className = 'budget-item';
  row.innerHTML = `
    <input name="date" type="date" value="${date}" required />
    <input name="description" value="${description}" placeholder="Description" required />
    <input name="amount" type="number" min="0" step="0.01" value="${amount}" placeholder="Amount" required />
  `;
  return row;
}

function collectRows() {
  return [...list.querySelectorAll('.budget-item')].map((row) => ({
    date: row.querySelector('input[name="date"]').value,
    description: row.querySelector('input[name="description"]').value,
    amount: row.querySelector('input[name="amount"]').value,
  }));
}

function collectBudgets() {
  return collectRows().map((entry) => ({ label: entry.description, amount: entry.amount }));
}

function syncNotebook() {
  const records = collectRows().map((entry) => ({
    date: entry.date || 'N/A',
    description: entry.description || 'No description',
    amount: `${Number(entry.amount || 0).toFixed(2)} CNY`,
  }));

  notebookScene.setRecords(records);
}

function renderResult(result) {
  totalText.textContent = `${result.total} 元`;
  remainingText.textContent = `${result.remaining} 元`;
  remainingText.classList.toggle('negative', result.remaining.startsWith('-'));
}

addBtn.addEventListener('click', () => {
  list.appendChild(createBudgetRow(todayISO(list.children.length), '', '0'));
  syncNotebook();
});

list.addEventListener('input', () => {
  syncNotebook();
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
  syncNotebook();
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

flipNextBtn.addEventListener('click', () => notebookScene.flipForward());
flipPrevBtn.addEventListener('click', () => notebookScene.flipBackward());

syncNotebook();