from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class FinanceSummary:
    salary: Decimal
    budgets: dict[str, Decimal]

    @property
    def total(self) -> Decimal:
        return sum(self.budgets.values(), Decimal("0"))

    @property
    def remaining(self) -> Decimal:
        return self.salary - self.total