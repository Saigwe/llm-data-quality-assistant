"""CLI: python -m dq_assistant --run-results target/run_results.json [--manifest ...] [--llm]"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import anthropic

from .parse import load_run_results
from .report import build_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarise dbt test results for data owners.")
    parser.add_argument("--run-results", required=True, help="Path to dbt target/run_results.json")
    parser.add_argument("--manifest", help="Path to dbt target/manifest.json (maps tests to models)")
    parser.add_argument("--llm", action="store_true", help="Add a Claude-written briefing")
    parser.add_argument("--out", help="Write the report to this markdown file")
    args = parser.parse_args(argv)

    results = load_run_results(args.run_results, args.manifest)
    report = build_report(results)

    if args.llm:
        from .llm import write_briefing

        try:
            report = "## Briefing\n\n" + write_briefing(results) + "\n\n---\n\n" + report
        except anthropic.AuthenticationError:
            print("No valid Anthropic credentials; showing the deterministic report only.", file=sys.stderr)
        except anthropic.APIConnectionError:
            print("Could not reach the Anthropic API; showing the deterministic report only.", file=sys.stderr)

    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"Report written to {args.out}")
    else:
        print(report)
    has_errors = any(r.status in {"error", "fail"} for r in results)
    return 1 if has_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
