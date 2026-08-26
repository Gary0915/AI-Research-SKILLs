from thesis_deck_system.contracts import semantic_findings


def has_rule(bundle, rule):
    return any(f.rule_id == rule for f in semantic_findings(bundle))


def test_block_without_research_question():
    assert has_rule({"research_blocks": [{"block_id": "B001", "research_status": "active"}]}, "SCI-BLOCK-MISSING-RESEARCH-QUESTION")


def test_non_falsifiable_mechanism():
    assert has_rule({"claims": [{"claim_id": "C001", "claim_type": "mechanism"}]}, "SCI-HYPOTHESIS-NOT-FALSIFIABLE")


def test_literature_source_list_without_synthesis():
    assert has_rule({"stages": [{"stage_id": "ST-LIT", "stage_type": "literature", "data": {}}]}, "SCI-LITERATURE-NOT-SYNTHESIZED")


def test_next_step_missing_owner_timing_decision_binding():
    assert has_rule({"actions": [{"action_item_id": "NS001"}]}, "SCI-NEXT-STEP-INCOMPLETE")


def test_experiment_missing_controls_variables_metrics_decision_rule():
    assert has_rule({"stages": [{"stage_id": "ST-EXP", "stage_type": "experiment", "data": {}}]}, "SCI-EXPERIMENT-INCOMPLETE")


def test_research_status_cannot_encode_story_visibility():
    assert has_rule({"research_blocks": [{"block_id": "B001", "research_status": "archived_from_main_story"}]}, "LEDGER-STATUS-VISIBILITY-CONFLATED")


def test_meeting_projection_cannot_drop_prior_commitment():
    assert has_rule({"meeting_projection": {"prior_commitment_ids": ["NS001"], "included_action_ids": []}}, "PROF-MEETING-LOST-COMMITMENT")


def test_generated_evidence_cannot_support_claim():
    assert has_rule({"evidence_cards": [{"evidence_id": "E001", "kind": "generated_context", "claim_support_refs": ["C001"]}]}, "PROV-GENERATED-AS-EVIDENCE")


def test_failed_experiment_must_remain_reachable():
    assert has_rule({"research_blocks": [{"block_id": "B001", "research_status": "failed_but_informative"}], "history_reachable_block_ids": []}, "LEDGER-FAILED-HISTORY-UNREACHABLE")


def test_open_critical_finding_blocks_release():
    assert has_rule({"qa_reports": [{"findings": [{"severity": "critical", "status": "open"}], "pipeline": [{"stage": "release", "status": "pass"}]}]}, "RELEASE-CRITICAL-FINDING-OPEN")

