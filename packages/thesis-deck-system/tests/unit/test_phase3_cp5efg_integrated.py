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
    assert result["qa"]["structural_geometry_calibration"] == "provisional"
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


def test_g1_rebuilt_measured_calibration_artifacts_match_closed_schemas(tmp_path: Path):
    """G1 evidence must not outgrow the registered machine contracts."""
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.phase3_cp5efg_integrated import build_calibration_artifacts
    import json

    build_calibration_artifacts(ROOT, tmp_path)
    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5a=True, include_cp5bcd=True)
    for artifact, schema_name in (
        ("archetype-calibration.json", "archetype-calibration"),
        ("figure-family-calibration.json", "figure-family-calibration"),
        ("fishbone-style-profile.json", "fishbone-style-profile"),
        ("reconstruction-benchmarks.json", "reconstruction-benchmarks"),
        ("checkpoint-5g-qa.json", "checkpoint-5g-qa"),
    ):
        assert registry.errors(schema_name, json.loads((tmp_path / artifact).read_text(encoding="utf-8"))) == []


def test_e1_plot_hash_and_svg_are_deterministically_derived_from_numeric_input():
    from thesis_deck_system.phase3_cp5efg_integrated import canonical_plot_input, build_scientific_plot

    payload = {"series": [{"series_id": "S-A", "points": [[0, 1], [2, 3]]}], "x_axis_label": "time", "x_axis_unit": "s", "y_axis_label": "response", "y_axis_unit": "a.u.", "provenance_refs": ["E101"], "evidence_status": "synthetic_test_evidence"}
    first = build_scientific_plot(ROOT, payload)
    assert first["data_sha256"] == canonical_plot_input(payload)["data_sha256"]
    assert "time / s" in first["svg"] and "response / a.u." in first["svg"]
    changed = deepcopy(payload); changed["series"][0]["points"][1][1] = 4
    assert build_scientific_plot(ROOT, changed)["canonical_sha256"] != first["canonical_sha256"]
    stale = deepcopy(payload); stale["data_sha256"] = "a" * 64
    with pytest.raises(Exception):
        canonical_plot_input(stale)


def test_e1_image_matrix_binds_each_synthetic_panel_hash_provenance_order_and_scale():
    from thesis_deck_system.phase3_cp5efg_integrated import build_image_matrix

    fixtures = ROOT / "thesis-deck-system" / "assets" / "cp5e-synthetic-panels"
    panels = [{"panel_id": f"P{index:03}", "source_asset_ref": f"assets/cp5e-synthetic-panels/p{index:03}.svg", "source_bytes": (fixtures / f"p{index:03}.svg").read_bytes(), "provenance_ref": "E101", "order": index, "scale_policy": "shared", "label": f"panel {index}"} for index in range(1, 5)]
    result = build_image_matrix(ROOT, panels)
    assert len(result["panel_lineage"]) == 4
    assert all(item["source_sha256"] for item in result["panel_lineage"])
    reordered = [*reversed(panels)]
    for index, panel in enumerate(reordered, 1): panel["order"] = index
    assert build_image_matrix(ROOT, reordered)["canonical_sha256"] != result["canonical_sha256"]
    stale = deepcopy(panels); stale[0]["source_sha256"] = "0" * 64
    with pytest.raises(Exception):
        build_image_matrix(ROOT, stale)


def test_e1_default_matrix_uses_committed_synthetic_panel_fixtures():
    """Default E1 provenance must name auditable committed synthetic sources."""
    from thesis_deck_system.phase3_cp5efg_integrated import build_evidence_bound_outputs

    matrix = build_evidence_bound_outputs(ROOT)["image_matrix"]
    for panel in matrix["panel_lineage"]:
        assert panel["source_asset_ref"].startswith("assets/cp5e-synthetic-panels/")
        assert (ROOT / "thesis-deck-system" / panel["source_asset_ref"]).is_file()


def test_e1_synthetic_panel_bundle_uses_canonical_lowercase_resource_names():
    """Bundle-relative SVG hrefs must resolve on case-sensitive consumers."""
    fixtures = ROOT / "thesis-deck-system" / "assets" / "cp5e-synthetic-panels"
    assert sorted(path.name for path in fixtures.glob("*.svg")) == [
        "p001.svg",
        "p002.svg",
        "p003.svg",
        "p004.svg",
    ]


def test_c1_e1_approved_routes_carry_real_cp1_foms():
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.phase3_cp5efg_integrated import build_evidence_bound_outputs

    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5a=True, include_cp5bcd=True)
    outputs = build_evidence_bound_outputs(ROOT)
    for name in ("scientific_plot", "image_matrix"):
        assert registry.errors("figure-output-manifest", outputs[name]["cp1_fom"]) == []


def test_f1_deterministic_renderer_adapter_proves_positive_render_manifest_path():
    from thesis_deck_system.phase3_cp5efg_integrated import DeterministicTestRendererAdapter, render_with_adapter

    result = render_with_adapter(DeterministicTestRendererAdapter(), '<svg xmlns="http://www.w3.org/2000/svg"/>', {"width": 16, "height": 9})
    assert result["render_manifest"]["renderer_version"] == "test-1"
    assert result["render_manifest"]["png_sha256"] == result["render_critic"]["png_sha256"]
    assert result["render_critic"]["status"] == "pass"


def test_f1_deterministic_adapter_returns_a_structurally_valid_png_with_requested_dimensions():
    from thesis_deck_system.phase3_cp5efg_integrated import DeterministicTestRendererAdapter, render_with_adapter

    result = render_with_adapter(DeterministicTestRendererAdapter(), '<svg xmlns="http://www.w3.org/2000/svg"/>', {"width": 16, "height": 9})
    png = result["rendered_fixture_bytes"]
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert png[12:16] == b"IHDR"
    assert int.from_bytes(png[16:20], "big") == 16
    assert int.from_bytes(png[20:24], "big") == 9


def test_f1_review_action_is_deeply_immutable_after_caller_and_view_mutation():
    from thesis_deck_system.phase3_cp5efg_integrated import CurrentSlideContext, ReviewAction

    payload = {"nested": {"values": ["original"]}}
    context = CurrentSlideContext("CTX-D1", "A03", "FIG002", "hash", ("obj-1",))
    action = ReviewAction.create(context, "flag_overlap", payload)
    payload["nested"]["values"].append("mutated")
    assert action.payload["nested"]["values"] == ("original",)
    with pytest.raises(TypeError):
        action.payload["nested"] = "mutated"


def test_g1_calibration_records_measured_provenance_and_real_benchmark_fixtures(tmp_path: Path):
    from thesis_deck_system.phase3_cp5efg_integrated import build_calibration_artifacts

    result = build_calibration_artifacts(ROOT, tmp_path)
    assert all(item["measured_metrics"] and item["archetype_source_hash"] for item in result["archetypes"])
    assert all(item["representative_fixture"] and item["stress_fixture"] for item in result["families"]["families"])
    first = (tmp_path / "cp5g" / "archetype-calibration-montage.svg").read_text(encoding="utf-8")
    second = (tmp_path / "cp5g" / "figure-family-calibration-montage.svg").read_text(encoding="utf-8")
    assert first != second
