"""Focused CP5-B/C/D integrated-sprint contract tests."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]


def test_cp5b_registry_is_feature_level_and_native_unknown_does_not_invalidate_legal_svg():
    from thesis_deck_system.phase3_cp5bcd_integrated import CapabilityRegistry, CapabilityError, default_registry

    registry = default_registry()
    assert registry.record_count >= 30
    assert registry.svg_static_eligible(["svg-root-viewbox", "path-commands", "text-editable-cjk" ]) is True
    with pytest.raises(CapabilityError):
        registry.require_coverage(["missing-feature"])
    duplicate = deepcopy(registry.payload)
    duplicate["records"].append(deepcopy(duplicate["records"][0]))
    with pytest.raises(CapabilityError):
        CapabilityRegistry(duplicate)


def test_cp5b_rejects_native_overclaim_and_silent_raster_fallback():
    from thesis_deck_system.phase3_cp5bcd_integrated import CapabilityRegistry, CapabilityError, default_registry

    overclaim = deepcopy(default_registry().payload)
    overclaim["records"][0]["capability_state"] = "NATIVE_EXACT"
    overclaim["records"][0]["evidence_level"] = "source_inspected"
    with pytest.raises(CapabilityError):
        CapabilityRegistry(overclaim)
    silent = deepcopy(default_registry().payload)
    silent["records"][0]["capability_state"] = "RASTER_FALLBACK"
    silent["records"][0]["fallback_declared"] = False
    with pytest.raises(CapabilityError):
        CapabilityRegistry(silent)


def test_cp5c_static_critic_requires_real_manifest_hashes_and_approval_cannot_be_fabricated():
    from thesis_deck_system.phase3_cp5bcd_integrated import StaticFigureCritic, FigureGateError, make_synthetic_manifest

    manifest = make_synthetic_manifest(ROOT, "FIG002")
    result = StaticFigureCritic(ROOT).execute(manifest)
    assert result["status"] == "APPROVED_FIGURE"
    assert result["approval"]["approval_status"] == "APPROVED_FIGURE"
    bad = deepcopy(manifest)
    bad["canonical_output"]["canonical_sha256"] = "0" * 64
    assert StaticFigureCritic(ROOT).execute(bad)["status"] == "FAIL"
    with pytest.raises(FigureGateError):
        StaticFigureCritic(ROOT).approve_unexecuted({"approved": True})


def test_cp5c_uses_a_distinct_svg_manifest_contract_without_replacing_cp1_contract():
    """CP5-C must not overwrite the established CP1 FigureOutputManifest."""
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.phase3_cp5bcd_integrated import make_synthetic_manifest

    registry = SchemaRegistry(
        ROOT / "thesis-deck-system" / "schemas",
        include_phase3=True,
        include_cp5a=True,
        include_cp5bcd=True,
    )
    manifest = make_synthetic_manifest(ROOT, "FIG002")
    assert registry.errors("scientific-svg-figure-output-manifest", manifest) == []


@pytest.mark.parametrize("section", ["style_resolution", "output_lineage", "static_critic"])
def test_cp5c_svg_manifest_rejects_untyped_nested_contract_fields(section: str):
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.phase3_cp5bcd_integrated import make_synthetic_manifest

    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5a=True, include_cp5bcd=True)
    manifest = make_synthetic_manifest(ROOT, "FIG002")
    manifest[section]["unexpected"] = "must-fail-closed"
    assert registry.errors("scientific-svg-figure-output-manifest", manifest)


def test_cp5c_layout_handoff_allows_only_executed_approved_figure():
    from thesis_deck_system.phase3_cp5bcd_integrated import StaticFigureCritic, FigureGateError, make_synthetic_manifest, reverify_approved_figure

    critic = StaticFigureCritic(ROOT)
    with pytest.raises(FigureGateError):
        critic.layout_eligible({"kind": "raw_svg"})
    manifest = make_synthetic_manifest(ROOT, "FIG002")
    result = critic.execute(manifest)
    handle = reverify_approved_figure(manifest, result["report"], result["approval"], ROOT)
    assert critic.layout_eligible(handle) is True


def test_cp5c_layout_requires_runtime_handle_and_reverification_rejects_forged_approval():
    """Persisted approval-shaped JSON is evidence, never runtime authority."""
    from thesis_deck_system.phase3_cp5bcd_integrated import (
        FigureGateError,
        StaticFigureCritic,
        make_synthetic_manifest,
        reverify_approved_figure,
    )

    critic = StaticFigureCritic(ROOT)
    manifest = make_synthetic_manifest(ROOT, "FIG002")
    result = critic.execute(manifest)
    with pytest.raises(FigureGateError):
        critic.layout_eligible(result["approval"])
    handle = reverify_approved_figure(manifest, result["report"], result["approval"], ROOT)
    assert critic.layout_eligible(handle) is True
    forged = deepcopy(result["approval"])
    forged["manifest_hash"] = "a" * 64
    with pytest.raises(FigureGateError):
        reverify_approved_figure(manifest, result["report"], forged, ROOT)


def test_cp5c_style_resolution_consumes_actual_vsp003_fields_not_fake_category_ids():
    from thesis_deck_system.phase3_cp5bcd_integrated import resolve_style, _spec

    style = resolve_style(ROOT, _spec(ROOT, "FIG002"))
    assert style["token_provenance"], "usable VSP003 tokens must be traceable"
    assert all("token_id" in item and "authority_family" in item for item in style["token_provenance"])
    assert style["application_trace"], "visual attributes must bind token/fallback provenance"


def test_cp5c_static_critic_persists_the_full_owning_check_set_with_facts():
    from thesis_deck_system.phase3_cp5bcd_integrated import StaticFigureCritic, make_synthetic_manifest

    report = StaticFigureCritic(ROOT).execute(make_synthetic_manifest(ROOT, "FIG002"))["report"]
    check_ids = {item["check_id"] for item in report["checks"]}
    assert {f"C0-{index:02d}" for index in range(1, 22)} <= check_ids
    assert all("facts" in item and item["status"] in {"pass", "fail", "blocked"} for item in report["checks"])


def test_c1_constructs_and_schema_validates_canonical_cp1_fom_with_hash_bound_svg_envelope():
    """The CP1 FigureOutputManifest must be a real critic input, not a label."""
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.phase3_cp5bcd_integrated import (
        StaticFigureCritic,
        make_cp1_figure_output_manifest,
        make_synthetic_manifest,
    )

    envelope = make_synthetic_manifest(ROOT, "FIG002")
    cp1_fom = make_cp1_figure_output_manifest(ROOT, envelope)
    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5a=True, include_cp5bcd=True)
    assert registry.errors("figure-output-manifest", cp1_fom) == []
    result = StaticFigureCritic(ROOT).execute_bundle({"cp1_fom": cp1_fom, "svg_envelope": envelope})
    assert result["status"] == "APPROVED_FIGURE"
    assert result["report"]["checks"][0]["facts"]["cp1_fom_hash"] == result["bundle"]["cp1_fom_hash"]


def test_c1_rejects_cp1_fom_hash_mutation_and_svg_style_trace_disagreement():
    from thesis_deck_system.phase3_cp5bcd_integrated import (
        StaticFigureCritic,
        make_cp1_figure_output_manifest,
        make_synthetic_manifest,
    )

    envelope = make_synthetic_manifest(ROOT, "FIG002")
    cp1_fom = make_cp1_figure_output_manifest(ROOT, envelope)
    cp1_fom["primary_artifact"]["sha256"] = "0" * 64
    assert StaticFigureCritic(ROOT).execute_bundle({"cp1_fom": cp1_fom, "svg_envelope": envelope})["status"] == "FAIL"
    envelope = make_synthetic_manifest(ROOT, "FIG002")
    envelope["style_resolution"]["application_trace"][0]["serialized_applied_value"] = "unrelated-value"
    cp1_fom = make_cp1_figure_output_manifest(ROOT, envelope)
    assert StaticFigureCritic(ROOT).execute_bundle({"cp1_fom": cp1_fom, "svg_envelope": envelope})["status"] == "FAIL"


def test_vsp003_category_resolution_map_is_a_registered_closed_contract():
    from thesis_deck_system.contracts import SchemaRegistry
    import json

    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5a=True, include_cp5bcd=True)
    payload = json.loads((ROOT / "thesis-deck-system" / "artifacts" / "phase3" / "vsp003-style-category-resolution-map.json").read_text(encoding="utf-8"))
    assert registry.errors("vsp003-style-category-resolution-map", payload) == []


def test_cp5c_execution_artifacts_are_derived_from_executed_critic(tmp_path: Path):
    from thesis_deck_system.phase3_cp5bcd_integrated import write_gate_c_artifacts

    result = write_gate_c_artifacts(ROOT, tmp_path)
    assert result["qa"]["aggregate_status"] == "pass"
    assert result["execution"]["owning_check_count"] >= 21
    assert (tmp_path / "checkpoint-5c-qa.json").exists()


@pytest.mark.parametrize("family", ["fishbone", "mechanism", "experiment", "fabrication", "comparison"])
def test_cp5d_specialist_directors_validate_inputs_and_traverse_static_approval(family: str):
    from thesis_deck_system.phase3_cp5bcd_integrated import build_representative_director_output

    result = build_representative_director_output(ROOT, family)
    assert result["director_family"] == family
    assert result["svg_qa"]["aggregate_status"] == "pass"
    assert result["critic"]["status"] == "APPROVED_FIGURE"
    assert result["style_resolution"]["material_semantic_colors_not_consumed"] is True


def test_cp5d_directors_emit_distinct_family_semantic_geometry():
    from thesis_deck_system.phase3_cp5bcd_integrated import build_representative_director_output

    outputs = {family: build_representative_director_output(ROOT, family)["svg"] for family in ("fishbone", "mechanism", "experiment", "fabrication", "comparison")}
    assert len(set(outputs.values())) == 5
    assert outputs["fishbone"].count('data-semantic-role="branch"') >= 3
    assert 'data-semantic-role="sample"' in outputs["experiment"]
    assert 'id="obj-control"' in outputs["experiment"]
    assert 'data-semantic-role="process_step"' in outputs["fabrication"]
    assert outputs["comparison"].count('data-semantic-role="panel"') >= 2
    assert 'stroke-dasharray=' in outputs["mechanism"]


def test_cp5d_artifacts_include_svg_montage_and_structural_distinctness(tmp_path: Path):
    from thesis_deck_system.phase3_cp5bcd_integrated import write_gate_c_and_d_artifacts

    result = write_gate_c_and_d_artifacts(ROOT, tmp_path)
    assert result["d_qa"]["aggregate_status"] == "pass"
    assert (tmp_path / "cp5d-structured-directors" / "structured-director-montage.svg").exists()
    facts = json.loads((tmp_path / "cp5d-structured-directors" / "structural-distinctness.json").read_text(encoding="utf-8"))
    assert facts["all_canonical_hashes_distinct"] is True


@pytest.mark.parametrize("family, mutate", [
    ("fishbone", lambda value: value["branches"].append(deepcopy(value["branches"][0]))),
    ("fishbone", lambda value: value["branches"].__setitem__(0, value["branches"][0] | {"parent_ref": "BR002"})),
    ("mechanism", lambda value: value["edges"].__setitem__(0, {"from": "N001", "to": "MISSING", "state": "certain"})),
    ("experiment", lambda value: value.__setitem__("controls", [])),
    ("fabrication", lambda value: value["steps"].__setitem__(0, value["steps"][0] | {"temperature": "25"})),
    ("comparison", lambda value: value["sides"].__setitem__(1, value["sides"][1] | {"area": 0.7})),
])
def test_cp5d_director_negative_contracts_fail_closed(family: str, mutate):
    from thesis_deck_system.phase3_cp5bcd_integrated import DirectorInputError, _representative_input, validate_director_input

    payload = _representative_input(family)
    mutate(payload)
    with pytest.raises(DirectorInputError):
        validate_director_input(family, payload)
