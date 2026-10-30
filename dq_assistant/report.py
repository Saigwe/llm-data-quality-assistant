"""Deterministic markdown report, used offline and as grounding for the LLM."""
from __future__ import annotations

from .parse import TestResult, summarise_counts


def facts_table(results: list[TestResult]) -> str:
    """Markdown table of failing / warning tests. This is the only evidence the LLM sees."""
    problems = [r for r in results if r.is_problem]
    if not problems:
        return "No failing or warning tests."
    lines = ["| Status | Test | Model | Failing rows | Message |", "|---|---|---|---|---|"]
    for r in problems:
        msg = r.message.replace("|", "/").replace("\n", " ")[:160]
        lines.append(f"| {r.status} | {r.test_name} | {r.model} | {r.failures} | {msg} |")
    return "\n".join(lines)


def build_report(results: list[TestResult]) -> str:
    counts = summarise_counts(results)
    total = len(results)
    problems = [r for r in results if r.is_problem]
    affected = sorted({r.model for r in problems})
    header = (
        f"# Data quality report\n\n"
        f"**{total} tests run**: "
        + ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
        + "\n\n"
    )
    if not problems:
        return header + "All tests passed. No action needed.\n"
    return (
        header
        + f"**Models affected:** {', '.join(affected)}\n\n"
        + "## Findings\n\n"
        + facts_table(results)
        + "\n"
    )
