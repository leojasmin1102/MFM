from __future__ import annotations

from .domain import FinanceSummary


class AdvicePromptBuilder:
    @staticmethod
    def build(summary: FinanceSummary) -> str:
        budget_lines = "\n".join(
            f"- {label}: {amount} 元" for label, amount in summary.budgets.items()
        )
        return (
            "你是一位谨慎但务实的个人理财顾问。"
            "请基于用户的工资与预算分布，给出中文消费建议。\n"
            "要求：\n"
            "1) 先总结风险点；\n"
            "2) 给出 3 条可执行建议；\n"
            "3) 如果存在超支，说明优先削减项；\n"
            "4) 输出控制在 180 字以内。\n\n"
            f"本月工资: {summary.salary} 元\n"
            f"总预算: {summary.total} 元\n"
            f"本月剩余: {summary.remaining} 元\n"
            "预算标签与金额:\n"
            f"{budget_lines}"
        )


class AdviceGenerator:
    """默认实现：返回 prompt，方便后续接入真实大模型。"""

    def generate(self, prompt: str) -> str:
        return (
            "尚未接入 AI 大模型。你可以在 finance_app/ai.py 的 AdviceGenerator.generate "
            "中调用你的模型接口，并返回消费建议。\n\n"
            "当前发送给模型的提示词如下：\n"
            f"{prompt}"
        )