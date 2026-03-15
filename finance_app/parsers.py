from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from urllib.parse import parse_qs


class AmountParser:
    @staticmethod
    def parse(value: str | None) -> Decimal:
        if value is None:
            return Decimal("0")
        try:
            amount = Decimal(value.strip())
        except (InvalidOperation, AttributeError):
            return Decimal("0")
        return amount if amount >= 0 else Decimal("0")


class FinanceFormParser:
    @staticmethod
    def parse_form(raw_data: str) -> tuple[Decimal, dict[str, Decimal]]:
        form = parse_qs(raw_data)
        salary = AmountParser.parse(form.get("salary", ["0"])[0])
        labels = form.get("label", [])
        amounts = form.get("amount", [])

        budgets: dict[str, Decimal] = {}
        for i, label in enumerate(labels):
            clean_label = label.strip()
            if not clean_label:
                continue
            budgets[clean_label] = AmountParser.parse(amounts[i] if i < len(amounts) else "0")

        return salary, budgets


class FinanceApiParser:
    @staticmethod
    def parse_json(raw_data: str) -> tuple[Decimal, dict[str, Decimal]]:
        try:
            payload = json.loads(raw_data or "{}")
        except json.JSONDecodeError:
            return Decimal("0"), {}

        salary = AmountParser.parse(str(payload.get("salary", "0")))
        budgets: dict[str, Decimal] = {}
        for item in payload.get("budgets", []):
            label = str(item.get("label", "")).strip()
            if not label:
                continue
            budgets[label] = AmountParser.parse(str(item.get("amount", "0")))

        return salary, budgets