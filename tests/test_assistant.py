from pathlib import Path
from types import SimpleNamespace

from dq_assistant.__main__ import main
from dq_assistant.llm import build_user_message, write_briefing
from dq_assistant.parse import load_run_results, summarise_counts
from dq_assistant.report import build_report

SAMPLES = Path(__file__).resolve().parent.parent / "sample_artifacts"
RUN_RESULTS = SAMPLES / "run_results.json"
MANIFEST = SAMPLES / "manifest.json"


def test_only_tests_are_parsed_and_sorted_worst_first():
    results = load_run_results(RUN_RESULTS, MANIFEST)
    assert len(results) == 6  # the model node is skipped
    assert [r.status for r in results[:4]] == ["error", "fail", "fail", "warn"]
    assert results[1].failures == 1342  # bigger failure ranks first within a status


def test_manifest_maps_tests_to_models():
    results = {r.test_name: r for r in load_run_results(RUN_RESULTS, MANIFEST)}
    assert results["not_null_fct_orders_customer_id"].model == "fct_orders"
    assert results["source_freshness_raw_payments"].model == "stg_payments"
    # relationships tests depend on two models; the one under test is named first
    rel = "relationships_fct_orders_customer_id__customer_id__ref_dim_customers_"
    assert results[rel].model == "fct_orders"


def test_without_manifest_model_is_unknown():
    assert {r.model for r in load_run_results(RUN_RESULTS)} == {"unknown"}


def test_counts_and_report():
    results = load_run_results(RUN_RESULTS, MANIFEST)
    assert summarise_counts(results) == {"error": 1, "fail": 2, "warn": 1, "pass": 2}
    report = build_report(results)
    assert "6 tests run" in report
    assert "fct_orders" in report and "1342" in report
    assert "unique_dim_customers_customer_id" not in report  # passing tests stay out of findings


def test_llm_gets_only_problem_rows():
    msg = build_user_message(load_run_results(RUN_RESULTS, MANIFEST))
    assert "not_null_fct_orders_customer_id" in msg
    assert "not_null_dim_customers_country" not in msg


def test_write_briefing_uses_claude_and_returns_text():
    calls = {}

    def create(**kwargs):
        calls.update(kwargs)
        return SimpleNamespace(
            stop_reason="end_turn",
            content=[SimpleNamespace(type="thinking"), SimpleNamespace(type="text", text=" Briefing ")],
        )

    fake = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(create=create)))
    out = write_briefing(load_run_results(RUN_RESULTS, MANIFEST), client=fake)
    assert out == "Briefing"
    assert calls["model"] == "claude-opus-5-5"
    assert "1342" in calls["messages"][0]["content"]


def test_cli_writes_report_and_fails_on_errors(tmp_path):
    out = tmp_path / "report.md"
    code = main(["--run-results", str(RUN_RESULTS), "--manifest", str(MANIFEST), "--out", str(out)])
    assert code == 1
    assert out.read_text(encoding="utf-8").startswith("# Data quality report")
