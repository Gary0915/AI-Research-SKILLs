from thesis_deck_system.qa import CANONICAL_PIPELINE, run_pipeline


def test_pipeline_has_exact_canonical_order_and_blocks_release_on_critical():
    report = run_pipeline(critical_findings=[{"finding_id": "QF-1", "severity": "critical", "status": "open"}], native_available=False)
    assert report["pipeline"] == [{"order": i + 1, "stage": stage, "status": status} for i, (stage, status) in enumerate(zip(CANONICAL_PIPELINE, ["pass", "pass", "pass", "pass", "not_run", "not_run", "not_run", "not_run", "not_run", "blocked"]))]
    assert report["overall_status"] == "blocked"


def test_pipeline_release_passes_only_when_native_acceptance_available_and_clean():
    report = run_pipeline(critical_findings=[], native_available=True)
    assert report["overall_status"] == "pass"
    assert all(item["status"] == "pass" for item in report["pipeline"])
