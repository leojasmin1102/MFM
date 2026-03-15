from __future__ import annotations

from decimal import Decimal

from .domain import FinanceSummary


class FinanceService:
    def __init__(self, default_budgets: dict[str, Decimal]):
        self.default_budgets = default_budgets

    def build_summary(self, salary: Decimal, budgets: dict[str, Decimal]) -> FinanceSummary:
        merged = self.default_budgets.copy()
        merged.update(budgets)
        return FinanceSummary(salary=salary, budgets=merged)