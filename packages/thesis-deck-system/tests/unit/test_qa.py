from thesis_deck_system.qa import CANONICAL_PIPELINE, run_pipeline


def test_pipeline_has_exact_canonical_order_and_blocks_release_on_critical():
    report = run_pipeline(critical_findings=[{"finding_id": "QF-1", "severity": "critical", "status": "open"}], native_available=False)
    assert [(item["order"], item["stage"], item["status"]) for item in report["pipeline"]] == [
        (i + 1, stage, status)
        for i, (stage, status) in enumerate(zip(CANONICAL_PIPELINE, ["not_run"] * 9 + ["blocked"]))
    ]
    assert report["overall_status"] == "blocked"
    assert report["tool_versions"]["gate_execution"] == "not_executed"


def test_compatibility_input_cannot_replace_executed_owning_checks():
    report = run_pipeline(critical_findings=[], native_available=True)
    assert report["overall_status"] == "blocked"
    assert all(item["status"] != "pass" for item in report["pipeline"])
