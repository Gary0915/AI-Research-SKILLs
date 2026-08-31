"""Focused C0–G sprint tests for evidence routes, review infrastructure, and calibration."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]


def test_cp5e_routes_keep_evidence_statuses_and_block_missing_sources():
    from thesis_deck_system.phase3_cp5efg_integrated import build_evidence_bound_outputs

    outputs = build_evidence_bound_outputs(ROOT)
    assert outputs["scientific_plot"]["status"] == "APPROVED_FIGURE"
    assert outputs["image_matrix"]["status"] == "APPROVED_FIGURE"
    assert outputs["concept_illustration"]["status"] == "APPROVED_FIGURE"
    assert outputs["photo_annotation"]["status"] == "BLOCKED_SOURCE"
    assert outputs["literature_figure"]["status"] == "BLOCKED_SOURCE"
    assert outputs["concept_illustration"]["scientific_claim_support"] == "forbidden"


def test_cp5e_rejects_semantic_mutations_not_marker_flags():
    from thesis_deck_system.phase3_cp5efg_integrated import EvidenceRouteError, validate_plot_input

    valid = {"series":[{"series_id":"S001","points":[[0,1],[1,2]]}],"axes":{"x_unit":"s","y_unit":"a.u."},"data_sha256":"a" * 64,"provenance_refs":["E101"],"evidence_status":"synthetic_test_evidence"}
    invalid = deepcopy(valid)
    invalid["provenance_refs"] = []
    with pytest.raises(EvidenceRouteError):
        validate_plot_input(invalid)


def test_cp5f_status_dimensions_are_independent_and_deictic_review_is_immutable():
    from thesis_deck_system.phase3_cp5efg_integrated import CurrentSlideContext, ReviewAction, probe_render_capability

    status = probe_render_capability()
    assert status["render_critic_status"] in {"available", "blocked_environment"}
    assert status["image_capable_qualitative_review_status"] == "blocked_visual_review"
    context = CurrentSlideContext("CTX001", "A03", "FIG002", "hash", ("obj-br002",))
    action = ReviewAction.create(context, "flag_overlap", {"severity":"minor"})
    assert action.context_id == "CTX001"
    with pytest.raises(Exception):
        action.action_type = "rewrite_ledger"


def test_cp5g_calibration_is_sanitized_only_and_cannot_claim_qualitative_pass():
    from thesis_deck_system.phase3_cp5efg_integrated import build_calibration_artifacts

    result = build_calibration_artifacts(ROOT, None)
    assert result["qa"]["structural_geometry_calibration"] == "pass"
    assert result["qa"]["professor_visual_acceptance"] == "blocked"
    assert result["qa"]["private_alias_resolution_attempts"] == 0


def test_cp5efg_execution_artifacts_are_registered_schema_contracts(tmp_path: Path):
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.phase3_cp5efg_integrated import write_gate_e_artifacts, write_gate_f_artifacts, build_calibration_artifacts
    import json

    write_gate_e_artifacts(ROOT, tmp_path); write_gate_f_artifacts(ROOT, tmp_path); build_calibration_artifacts(ROOT, tmp_path)
    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5a=True, include_cp5bcd=True)
    for name, path in (("checkpoint-5e-execution-evidence", "checkpoint-5e-execution-evidence.json"), ("checkpoint-5e-qa", "checkpoint-5e-qa.json"), ("checkpoint-5f-qa", "checkpoint-5f-qa.json"), ("checkpoint-5g-qa", "checkpoint-5g-qa.json")):
        assert registry.errors(name, json.loads((tmp_path / path).read_text(encoding="utf-8"))) == []
