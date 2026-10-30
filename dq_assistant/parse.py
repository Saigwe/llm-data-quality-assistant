"""Parse dbt run_results.json into structured test findings."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

SEVERITY_ORDER = {"error": 0, "fail": 1, "warn": 2, "pass": 3, "skipped": 4}


@dataclass(frozen=True)
class TestResult:
    unique_id: str
    test_name: str
    model: str
    status: str
    failures: int
    message: str
    execution_time: float

    @property
    def is_problem(self) -> bool:
        return self.status in {"error", "fail", "warn"}


def _test_name(unique_id: str) -> str:
    # e.g. test.shop.not_null_fct_orders_customer_id.8a3f1 -> not_null_fct_orders_customer_id
    parts = unique_id.split(".")
    return parts[2] if len(parts) >= 3 else unique_id


def _model_for(unique_id: str, depends_on: dict[str, list[str]]) -> str:
    nodes = depends_on.get(unique_id, [])
    models = [n.split(".")[-1] for n in nodes if n.startswith("model.")]
    # A relationships test depends on both models; the one named in the test is the one under test.
    name = _test_name(unique_id)
    named = [m for m in models if m in name]
    if named:
        return min(named, key=name.find)
    return models[0] if models else "unknown"


def load_run_results(path: str | Path, manifest_path: str | Path | None = None) -> list[TestResult]:
    """Return test results sorted worst-first.

    The manifest is optional; when given it is used to map each test to the model it checks.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    depends_on: dict[str, list[str]] = {}
    if manifest_path:
        manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        for uid, node in manifest.get("nodes", {}).items():
            depends_on[uid] = node.get("depends_on", {}).get("nodes", [])

    results = []
    for r in data.get("results", []):
        uid = r["unique_id"]
        if not uid.startswith("test."):
            continue
        results.append(
            TestResult(
                unique_id=uid,
                test_name=_test_name(uid),
                model=_model_for(uid, depends_on),
                status=r.get("status", "unknown"),
                failures=int(r.get("failures") or 0),
                message=r.get("message") or "",
                execution_time=float(r.get("execution_time") or 0.0),
            )
        )
    return sorted(results, key=lambda t: (SEVERITY_ORDER.get(t.status, 9), -t.failures))


def summarise_counts(results: list[TestResult]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in results:
        counts[r.status] = counts.get(r.status, 0) + 1
    return counts
