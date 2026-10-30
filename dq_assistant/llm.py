"""Ask Claude to turn verified test facts into a plain-English briefing for data owners."""
from __future__ import annotations

import anthropic

from .parse import TestResult, summarise_counts
from .report import facts_table

MODEL = "claude-opus-5-5"

SYSTEM_PROMPT = """You are a senior analytics engineer writing a data quality briefing for business \
data owners after a nightly dbt run.

Work only from the test results provided. Do not invent row counts, causes, or tables that are not \
in the input. Where the likely cause is uncertain, say so and suggest how to confirm it.

Structure the briefing as:
1. Headline: one sentence on whether reporting can be trusted today.
2. Issues, most severe first: what failed, which model, how many rows, the business impact, and the \
likely cause.
3. Recommended next steps: concrete checks or fixes, and who should own each one.

Keep it under 300 words and avoid jargon a business stakeholder would not know."""


def build_user_message(results: list[TestResult]) -> str:
    counts = summarise_counts(results)
    return (
        f"Test counts by status: {counts}\n\n"
        f"Failing and warning tests:\n{facts_table(results)}"
    )


def write_briefing(results: list[TestResult], client: anthropic.Anthropic | None = None) -> str:
    client = client or anthropic.Anthropic()
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        output_config={"effort": "medium"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_message(results)}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("The model declined to write the briefing.")
    return "".join(block.text for block in response.content if block.type == "text").strip()
