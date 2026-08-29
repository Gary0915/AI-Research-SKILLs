"""Checkpoint 3 RED/GREEN tests: sanitized-domain visual grammar resolution."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]
ARTIFACTS = ROOT / "thesis-deck-system" / "artifacts" / "phase3"


def _inputs() -> tuple[dict, dict, dict, dict]:
    return tuple(
        json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))
        for name in (
            "sanitized-shell-structural-descriptors.json",
            "sanitized-body-structural-descriptors.json",
            "sanitized-exemplar-manifest.json",
            "checkpoint-2-qa.json",
        )
    )


def test_cp3_resolver_consumes_only_sanitized_inputs_and_records_zero_private_access():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    outputs = resolve_checkpoint3(*_inputs())
    qa = outputs["checkpoint_qa"]
    assert qa["private_alias_resolution_attempts"] == 0
    assert qa["private_source_open_attempts"] == 0
    assert qa["private_render_attempts"] == 0
    assert qa["aggregate_status"] == "pass"


def test_layout_exemplar_cannot_contaminate_shell_authority():
    from thesis_deck_system.phase3_checkpoint3 import Checkpoint3ResolutionError, resolve_checkpoint3

    shell, body, manifest, qa = _inputs()
    body = copy.deepcopy(body)
    body["descriptor"]["shell_regions"] = [{"role": "footer"}]
    with pytest.raises(Checkpoint3ResolutionError, match="shell contamination"):
        resolve_checkpoint3(shell, body, manifest, qa)


def test_shell_winners_and_losers_are_deterministic_and_role_bound():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    shell, body, manifest, qa = _inputs()
    first = resolve_checkpoint3(shell, body, manifest, qa)
    shell["descriptors"].reverse()
    second = resolve_checkpoint3(shell, body, manifest, qa)
    assert first["template"]["shell_tokens"] == second["template"]["shell_tokens"]
    assert first["template"]["conflicts"] == second["template"]["conflicts"]
    winners = {token["token_family"]: token["source_role"] for token in first["template"]["shell_tokens"]}
    assert winners["content_title"] == "P3-TEMPLATE-PRIMARY-1"
    assert winners["footer"] == "P3-TEMPLATE-PRIMARY-3"


def test_unmapped_hard_shell_conflict_blocks_resolution():
    from thesis_deck_system.phase3_checkpoint3 import Checkpoint3ResolutionError, resolve_checkpoint3

    shell, body, manifest, qa = _inputs()
    shell = copy.deepcopy(shell)
    shell["descriptors"][0]["slide_size"]["width"] += 3
    with pytest.raises(Checkpoint3ResolutionError, match="hard shell conflict"):
        resolve_checkpoint3(shell, body, manifest, qa)


def test_single_or_provisional_body_descriptor_never_upgrades_to_recurring():
    from thesis_deck_system.phase3_checkpoint3 import resolve_body_grammar

    _, body, _, _ = _inputs()
    grammar = resolve_body_grammar(body["descriptor"])
    assert all(
        item["evidence_tier"] != "recurring_pattern"
        for item in grammar["families"]
        if item["sample_count"] == 1 or item["source_confidence"] == "provisional"
    )


def test_active_theme_and_explicit_font_only_can_be_professor_derived():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    outputs = resolve_checkpoint3(*_inputs())
    assert all(item["theme_authority"] == "active_professor_style" for item in outputs["grammar"]["active_theme_tokens"])
    assert all(item["family"] != "unknown" for item in outputs["grammar"]["typography_tokens"])
    assert all(item["font_evidence_state"] not in {"inherited_unresolved", "unknown"} for item in outputs["grammar"]["typography_tokens"])


def test_missing_metric_stays_unavailable_and_body_mutation_changes_only_body_grammar():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    shell, body, manifest, qa = _inputs()
    baseline = resolve_checkpoint3(shell, body, manifest, qa)
    mutated = copy.deepcopy(body)
    mutated["descriptor"]["body_measurements"][0]["metrics"]["annotation_density"] = {
        "value": 99.0, "basis": "derived", "evidence_state": "derived", "supporting_object_ids": ["O001"]
    }
    changed = resolve_checkpoint3(shell, mutated, manifest, qa)
    assert baseline["template"]["shell_tokens"] == changed["template"]["shell_tokens"]
    assert any(
        metric["availability"] == "unavailable"
        for family in baseline["body"]["families"]
        for metric in family["metric_distributions"]
    )
    assert baseline["body"]["families"] != changed["body"]["families"]


def test_conflicting_colors_remain_distinct_and_material_colors_remain_unresolved():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    grammar = resolve_checkpoint3(*_inputs())["grammar"]
    assert all("blended" not in item["value"] for item in grammar["active_theme_tokens"])
    assert all(item["status"] == "unresolved" for item in grammar["material_semantic_tokens"])


def test_fallback_tokens_do_not_count_as_professor_derived_coverage():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    style = resolve_checkpoint3(*_inputs())["style"]
    derived = sum(item["origin"] == "professor_derived" for item in style["tokens"])
    assert style["coverage"]["professor_derived_token_count"] == derived
    assert style["coverage"]["fallback_token_count"] == sum(item["origin"] != "professor_derived" for item in style["tokens"])


def test_owning_qa_checks_have_executed_evidence_and_fail_honestly():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    outputs = resolve_checkpoint3(*_inputs())
    checks = outputs["evidence"]["owning_checks"]
    assert len(checks) >= 19
    assert all(check["evidence"] for check in checks)
    assert all(check["status"] in {"pass", "fail"} for check in checks)


def test_failed_owning_check_makes_checkpoint_qa_fail_without_literal_pass():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    shell, body, manifest, qa = _inputs()
    qa = copy.deepcopy(qa)
    qa["aggregate_status"] = "fail"
    with pytest.raises(ValueError, match="CP2 QA must pass"):
        resolve_checkpoint3(shell, body, manifest, qa)


def test_shell_tokens_preserve_scope_support_variants_and_content_topology():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    template = resolve_checkpoint3(*_inputs())["template"]
    assert template["content_master_layout_topology"]
    title = next(token for token in template["shell_tokens"] if token["token_family"] == "content_title")
    assert title["support_by_scope"]
    assert title["support_count"] == sum(item["source_container_count"] for item in title["support_by_scope"])
    assert title["variants"]


def test_missing_safe_bounds_remain_insufficient_instead_of_invented():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    safe_bounds = resolve_checkpoint3(*_inputs())["template"]["safe_content_bounds"]
    assert safe_bounds["status"] == "insufficient_evidence"
    assert safe_bounds["value"] is None


def test_shell_safe_bound_intersection_is_explicit_and_incompatible_bounds_block():
    from thesis_deck_system.phase3_checkpoint3 import Checkpoint3ResolutionError, resolve_checkpoint3

    shell, body, manifest, qa = _inputs()
    shell = copy.deepcopy(shell)
    for descriptor, bounds in zip(shell["descriptors"], ({"x": 0.1, "y": 0.1, "w": 0.7, "h": 0.7}, {"x": 0.2, "y": 0.2, "w": 0.6, "h": 0.6})):
        descriptor["safe_content_bounds"] = {"value": bounds, "basis": "derived", "source_scope": "slide_layout", "evidence_ids": ["L001"]}
    assert resolve_checkpoint3(shell, body, manifest, qa)["template"]["safe_content_bounds"]["status"] == "resolved"
    shell["descriptors"][1]["safe_content_bounds"]["value"] = {"x": 0.95, "y": 0.95, "w": 0.04, "h": 0.04}
    with pytest.raises(Checkpoint3ResolutionError, match="safe content bounds"):
        resolve_checkpoint3(shell, body, manifest, qa)


def test_family_metrics_are_separate_and_mutation_is_family_local():
    from thesis_deck_system.phase3_checkpoint3 import resolve_body_grammar

    _, body, _, _ = _inputs()
    body = copy.deepcopy(body["descriptor"])
    for index, family in enumerate(("result_single", "image_matrix")):
        body["candidate_families"][index] = {"family": family, "confidence": "structurally_supported", "evidence_basis": "test"}
        body["body_measurements"][index]["metrics"]["figure_text_ratio"] = {"value": float(index + 1), "basis": "derived", "evidence_state": "derived", "supporting_object_ids": [f"O{index}"]}
    first = resolve_body_grammar(body)
    changed = copy.deepcopy(body)
    changed["body_measurements"][0]["metrics"]["figure_text_ratio"]["value"] = 9.0
    second = resolve_body_grammar(changed)
    first_by_family = {item["family"]: item for item in first["families"]}
    second_by_family = {item["family"]: item for item in second["families"]}
    assert first_by_family["result_single"]["metric_distributions"] != second_by_family["result_single"]["metric_distributions"]
    assert first_by_family["image_matrix"]["metric_distributions"] == second_by_family["image_matrix"]["metric_distributions"]


def test_family_medoid_and_outliers_are_deterministic():
    from thesis_deck_system.phase3_checkpoint3 import resolve_body_grammar

    _, body, _, _ = _inputs()
    grammar = resolve_body_grammar(body["descriptor"])
    for family in grammar["families"]:
        if family["status"] != "insufficient":
            assert family["preferred_descriptor_id"] in family["supporting_descriptor_ids"]
            assert set(family["outlier_descriptor_ids"]).issubset(family["supporting_descriptor_ids"])


def test_other_insufficient_family_never_becomes_reusable_grammar():
    from thesis_deck_system.phase3_checkpoint3 import resolve_body_grammar

    _, body, _, _ = _inputs()
    family = next(item for item in resolve_body_grammar(body["descriptor"])["families"] if item["family"] == "other_insufficient_structural_evidence")
    assert family["status"] == "insufficient"
    assert family["evidence_tier"] == "insufficient_evidence"


def test_active_theme_metadata_is_not_automatically_professor_style():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    outputs = resolve_checkpoint3(*_inputs())
    grammar = outputs["grammar"]
    assert grammar["active_theme_metadata"]
    assert not grammar["active_theme_tokens"]


def test_body_theme_cannot_create_formal_shell_palette_token():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    style = resolve_checkpoint3(*_inputs())["style"]
    assert all(not (token["source_role"] == "P3-LAYOUT-EXEMPLAR-2" and token["authority_family"] == "formal_shell") for token in style["tokens"])


def test_visual_style_governor_has_partial_calibration_and_typography_tokens():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    style = resolve_checkpoint3(*_inputs())["style"]
    assert style["status"] == "partial_structural_calibration"
    assert any(token["token_family"] == "typography" for token in style["tokens"])
    assert {"professor_derived_recurring", "professor_derived_provisional", "fallback", "unresolved", "reference_only_metadata"} <= set(style["coverage"])


def test_governor_tokens_have_complete_provenance():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    for token in resolve_checkpoint3(*_inputs())["style"]["tokens"]:
        assert {"origin", "evidence_tier", "source_role", "source_scope", "supporting_ids", "resolver_rule_id", "value"} <= set(token)


def test_schema_rejects_unexpected_nested_shell_and_conflict_fields():
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    template = resolve_checkpoint3(*_inputs())["template"]
    template["shell_tokens"][0]["unexpected"] = "nope"
    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", include_phase3=True)
    assert registry.errors("professor-template-resolved", template)
    template = resolve_checkpoint3(*_inputs())["template"]
    template["conflicts"].append({"conflict_id": "bad"})
    assert registry.errors("professor-template-resolved", template)


def test_schema_rejects_malformed_style_value_variant_and_owning_check():
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    outputs = resolve_checkpoint3(*_inputs())
    outputs["style"]["tokens"][0]["value"] = {"surprise": True}
    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", include_phase3=True)
    assert registry.errors("visual-style-profile", outputs["style"])
    outputs["evidence"]["owning_checks"][0]["evidence"] = {"untyped": True}
    assert registry.errors("resolver-evidence", outputs["evidence"])


def test_shell_variants_are_not_selected_by_input_order_and_preserve_loser_evidence():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    shell, body, manifest, qa = _inputs()
    shell = copy.deepcopy(shell)
    original = copy.deepcopy(shell["descriptors"][0]["shell_regions"][0])
    original["region_id"] = "R999"
    original["role"] = "title"
    shell["descriptors"][0]["shell_regions"].append(original)
    first = resolve_checkpoint3(shell, body, manifest, qa)["template"]
    shell["descriptors"][0]["shell_regions"].reverse()
    second = resolve_checkpoint3(shell, body, manifest, qa)["template"]
    assert first["shell_tokens"] == second["shell_tokens"]
    assert all("losing_descriptor_evidence" in conflict for conflict in first["conflicts"])


def test_hypothesis_history_remains_insufficient_without_direct_motif_evidence():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    token = next(token for token in resolve_checkpoint3(*_inputs())["template"]["shell_tokens"] if token["token_family"] == "hypothesis_history")
    assert token["evidence_tier"] == "insufficient_evidence"
