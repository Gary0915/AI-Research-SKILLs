"""Focused CP5-B/C/D integrated-sprint contract tests."""
from __future__ import annotations

from copy import deepcopy
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


def test_cp5c_layout_handoff_allows_only_executed_approved_figure():
    from thesis_deck_system.phase3_cp5bcd_integrated import StaticFigureCritic, FigureGateError, make_synthetic_manifest

    critic = StaticFigureCritic(ROOT)
    with pytest.raises(FigureGateError):
        critic.layout_eligible({"kind": "raw_svg"})
    approval = critic.execute(make_synthetic_manifest(ROOT, "FIG002"))["approval"]
    assert critic.layout_eligible(approval) is True


@pytest.mark.parametrize("family", ["fishbone", "mechanism", "experiment", "fabrication", "comparison"])
def test_cp5d_specialist_directors_validate_inputs_and_traverse_static_approval(family: str):
    from thesis_deck_system.phase3_cp5bcd_integrated import build_representative_director_output

    result = build_representative_director_output(ROOT, family)
    assert result["director_family"] == family
    assert result["svg_qa"]["aggregate_status"] == "pass"
    assert result["critic"]["status"] == "APPROVED_FIGURE"
    assert result["style_resolution"]["material_semantic_colors_not_consumed"] is True


@pytest.mark.parametrize("family, mutation", [
    ("fishbone", "duplicate_branch"), ("fishbone", "cycle"), ("mechanism", "unknown_promoted"),
    ("experiment", "missing_control"), ("fabrication", "invented_unknown"), ("comparison", "unequal_scale"),
])
def test_cp5d_director_negative_contracts_fail_closed(family: str, mutation: str):
    from thesis_deck_system.phase3_cp5bcd_integrated import DirectorInputError, validate_director_input

    with pytest.raises(DirectorInputError):
        validate_director_input(family, {"mutation": mutation})
