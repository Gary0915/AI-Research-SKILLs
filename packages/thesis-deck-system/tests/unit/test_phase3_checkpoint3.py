"""Checkpoint 3 RED/GREEN tests: sanitized-domain visual grammar resolution."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess

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
    assert qa["aggregate_status"] == "fail"
    assert next(check for check in qa["owning_checks"] if check["check_id"] == "CP3-DISPOSABLE-REGRESSION")["status"] == "fail"


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
    from thesis_deck_system.phase3_checkpoint3 import _candidate_binding_fingerprint, resolve_checkpoint3

    shell, body, manifest, qa = _inputs()
    baseline = resolve_checkpoint3(shell, body, manifest, qa)
    mutated = copy.deepcopy(body)
    mutated["descriptor"]["body_measurements"][0]["metrics"]["annotation_density"] = {
        "value": 99.0, "basis": "derived", "evidence_state": "derived", "supporting_object_ids": ["O001"]
    }
    mutated["descriptor"]["candidate_families"][0]["binding_fingerprint"] = _candidate_binding_fingerprint(mutated["descriptor"]["candidate_families"][0], mutated["descriptor"]["body_measurements"][0])
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
    from thesis_deck_system.phase3_checkpoint3 import _candidate_binding_fingerprint, resolve_body_grammar

    _, body, _, _ = _inputs()
    body = copy.deepcopy(body["descriptor"])
    for index, family in enumerate(("result_single", "image_matrix")):
        body["candidate_families"][index]["family"] = family
        body["candidate_families"][index]["confidence"] = "structurally_supported"
        body["candidate_families"][index]["evidence_basis"] = ["test"]
        body["body_measurements"][index]["metrics"]["figure_text_ratio"] = {"value": float(index + 1), "basis": "derived", "evidence_state": "derived", "supporting_object_ids": [f"O{index}"]}
        body["candidate_families"][index]["binding_fingerprint"] = _candidate_binding_fingerprint(body["candidate_families"][index], body["body_measurements"][index])
    first = resolve_body_grammar(body)
    changed = copy.deepcopy(body)
    changed["body_measurements"][0]["metrics"]["figure_text_ratio"]["value"] = 9.0
    changed["candidate_families"][0]["binding_fingerprint"] = _candidate_binding_fingerprint(changed["candidate_families"][0], changed["body_measurements"][0])
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


def test_typography_authority_preserves_measured_hierarchy_and_rejects_cross_authority():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    outputs = resolve_checkpoint3(*_inputs())
    tokens = outputs["grammar"]["typography_tokens"]
    assert tokens
    assert all(token["size_pt"] is not None and token["weight"] and token["style"] for token in tokens)
    assert all(
        (token["source_role"] == "P3-TEMPLATE-PRIMARY-1" and token["role"] in {"title", "hypothesis_history", "content"})
        or (token["source_role"] == "P3-TEMPLATE-PRIMARY-3" and token["role"] in {"cover", "divider", "footer", "page_number", "navigation"})
        or (token["source_role"] == "P3-LAYOUT-EXEMPLAR-2" and token["role"] in {"body", "caption", "annotation", "panel_label"})
        for token in tokens
    )


def test_typography_duplicate_records_in_one_container_do_not_become_recurring():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    shell, body, manifest, qa = _inputs()
    shell = copy.deepcopy(shell)
    shell["descriptors"][0]["typography_roles"] *= 3
    tokens = resolve_checkpoint3(shell, body, manifest, qa)["grammar"]["typography_tokens"]
    assert all(token["evidence_tier"] != "recurring_pattern" for token in tokens)


def test_usage_backed_color_line_and_connector_grammar_excludes_unused_or_rotated_evidence():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    outputs = resolve_checkpoint3(*_inputs())
    figures = outputs["grammar"]["figure_grammar"]
    assert any(token["token_family"] == "style_color" and token["value"]["kind"] == "color" for token in figures)
    assert any(token["token_family"] == "connector" and token["value"]["kind"] == "connector" for token in figures)
    assert all(token.get("semantic_material") is None for token in figures)
    assert all(token["value"].get("rotation_eligible", True) for token in figures if token["token_family"] == "connector")


def test_body_candidate_measurement_binding_normalizes_measurement_reorder():
    from thesis_deck_system.phase3_checkpoint3 import resolve_body_grammar

    _, body, _, _ = _inputs()
    descriptor = copy.deepcopy(body["descriptor"])
    descriptor["body_measurements"].reverse()
    assert resolve_body_grammar(descriptor)["candidate_slide_bindings"] == resolve_body_grammar(body["descriptor"])["candidate_slide_bindings"]


def test_normalized_medoid_has_persisted_method_and_missingness_penalty():
    from thesis_deck_system.phase3_checkpoint3 import resolve_body_grammar

    _, body, _, _ = _inputs()
    grammar = resolve_body_grammar(body["descriptor"])
    reusable = [family for family in grammar["families"] if family["status"] != "insufficient"]
    assert reusable
    assert all(family["representative_method"]["method_id"] == "CP3-NORMALIZED-PAIRWISE-MEDOID-V1" for family in reusable)
    assert all(family["representative_method"]["comparable_metric_count"] >= 0 for family in reusable)
    assert all(family["representative_method"]["missing_data_penalty"] > 0 for family in reusable)


def test_execution_owned_qa_binds_schema_integrity_determinism_scanner_and_regression_evidence():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    checks = {item["check_id"]: item for item in resolve_checkpoint3(*_inputs())["evidence"]["owning_checks"]}
    required = {"CP3-CP2-SCHEMAS", "CP3-INPUT-HASHES", "CP3-DETERMINISM", "CP3-SUPPLEMENTAL-FONT-EXCLUSION", "CP3-REPOSITORY-STAGED-PRIVACY", "CP3-DISPOSABLE-REGRESSION"}
    assert required <= set(checks)
    assert all(checks[identifier]["evidence"]["facts"] for identifier in required)


def test_category_coverage_is_routing_useful_and_provisional_is_not_fully_calibrated():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    categories = resolve_checkpoint3(*_inputs())["style"]["coverage"]["categories"]
    required = {"shell_geometry", "typography_hierarchy", "body_composition", "scientific_figure_metrics", "connector_arrow_grammar", "line_style_grammar", "color_emphasis_grammar", "unresolved_fallback_reference"}
    assert required <= set(categories)
    assert all(categories[name]["reusable_coverage_status"] != "fully_calibrated" for name in required if categories[name]["professor_derived_recurring"] == 0)


def test_candidate_slide_bindings_are_persisted_and_reconcile_each_candidate_once():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    outputs = resolve_checkpoint3(*_inputs())
    bindings = outputs["body"]["candidate_slide_bindings"]
    assert len(bindings) == 13
    assert len({item["candidate_id"] for item in bindings}) == 13
    assert len({item["slide_id"] for item in bindings}) == 13
    assert all(item["binding_status"] == "resolved" for item in bindings)
    check = next(item for item in outputs["evidence"]["owning_checks"] if item["check_id"] == "CP3-BODY-BINDINGS")
    facts = {item["name"]: item for item in check["evidence"]["facts"]}
    assert facts["binding_count"]["integer"] == 13
    assert facts["ambiguous_binding_count"]["integer"] == 0
    assert facts["unresolved_binding_count"]["integer"] == 0


def test_explicit_body_binding_normalizes_reordered_arrays_and_rejects_ambiguous_duplicate_slide():
    from thesis_deck_system.phase3_checkpoint3 import Checkpoint3ResolutionError, resolve_body_grammar

    _, body, _, _ = _inputs()
    descriptor = copy.deepcopy(body["descriptor"])
    descriptor["candidate_families"].reverse()
    descriptor["body_measurements"].reverse()
    baseline = resolve_body_grammar(body["descriptor"])
    reordered = resolve_body_grammar(descriptor)
    assert baseline["candidate_slide_bindings"] == reordered["candidate_slide_bindings"]
    ambiguous = copy.deepcopy(body["descriptor"])
    ambiguous["candidate_families"][1]["bound_slide_id"] = ambiguous["candidate_families"][0]["bound_slide_id"]
    with pytest.raises(Checkpoint3ResolutionError, match="candidate.*binding"):
        resolve_body_grammar(ambiguous)


def test_privacy_owning_check_persists_actual_repository_and_staged_scanner_evidence():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    outputs = resolve_checkpoint3(*_inputs(), privacy_config={"config_id": "CP3-TEST-BOUNDARY", "private_root_signatures": ["__cp3_private_root_canary__"], "forbidden_basenames": ["__cp3_private_source__.pptx"]})
    check = next(item for item in outputs["evidence"]["owning_checks"] if item["check_id"] == "CP3-REPOSITORY-STAGED-PRIVACY")
    facts = {item["name"]: item for item in check["evidence"]["facts"]}
    required = {"scanner_id", "scanner_version", "configuration_hash", "repository_findings", "staged_findings", "approved_legacy_exceptions", "repository_scan_executed", "staged_scan_executed"}
    assert required <= set(facts)
    assert facts["repository_scan_executed"]["boolean"] is True
    assert facts["staged_scan_executed"]["boolean"] is True


def test_privacy_gate_rejects_empty_config_and_never_accepts_fabricated_staged_flag():
    from thesis_deck_system.phase3_checkpoint3 import _approved_privacy_scan

    passed, evidence = _approved_privacy_scan({"config_id": "EMPTY", "private_root_signatures": [], "forbidden_basenames": []})
    assert passed is False
    assert evidence["staged_scan_executed"] is False
    assert evidence["repository_scan_executed"] is False


def test_privacy_configuration_hash_changes_when_authoritative_boundary_changes():
    from thesis_deck_system.phase3_checkpoint3 import _approved_privacy_scan

    left = {"config_id": "CP3-A", "private_root_signatures": ["__cp3_root_a__"], "forbidden_basenames": ["__cp3_file_a__.pptx"]}
    right = {"config_id": "CP3-B", "private_root_signatures": ["__cp3_root_b__"], "forbidden_basenames": ["__cp3_file_b__.pptx"]}
    _, left_evidence = _approved_privacy_scan(left)
    _, right_evidence = _approved_privacy_scan(right)
    assert left_evidence["configuration_hash"] != right_evidence["configuration_hash"]


def test_repository_and_staged_scanners_detect_authoritative_basename_in_each_surface(tmp_path):
    from thesis_deck_system.phase3_privacy import RepositoryPrivacyScanner

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    tracked = tmp_path / "tracked.md"
    tracked.write_text("__cp3_authoritative_private_source__.pptx", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.md"], cwd=tmp_path, check=True)
    scanner = RepositoryPrivacyScanner(forbidden_basenames=["__cp3_authoritative_private_source__.pptx"])
    assert scanner.scan_tracked_repository(tmp_path)
    staged = tmp_path / "staged.md"
    staged.write_text("__cp3_authoritative_private_source__.pptx", encoding="utf-8")
    subprocess.run(["git", "add", "staged.md"], cwd=tmp_path, check=True)
    assert scanner.scan_staged(tmp_path)


def test_category_readiness_requires_all_subcapabilities_and_is_consistent_with_qa():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    outputs = resolve_checkpoint3(*_inputs())
    categories = outputs["style"]["coverage"]["categories"]
    assert categories["connector_arrow_grammar"]["reusable_coverage_status"] == "partial_recurring"
    assert categories["color_emphasis_grammar"]["reusable_coverage_status"] == "partial_recurring"
    check = next(item for item in outputs["evidence"]["owning_checks"] if item["check_id"] == "CP3-REPORT-ARTIFACT-CONSISTENCY")
    assert check["status"] == "pass"


def test_unknown_body_typography_is_audit_only_and_role_grammar_counts_independent_slides():
    from thesis_deck_system.phase3_checkpoint3 import resolve_checkpoint3

    shell, body, manifest, qa = _inputs()
    body = copy.deepcopy(body)
    observation = body["descriptor"]["body_measurements"][0]["typography_observations"][0]
    observation["role"] = "unknown"
    outputs = resolve_checkpoint3(shell, body, manifest, qa)
    assert all(item["role"] != "unknown" for item in outputs["grammar"]["typography_tokens"])
    assert all(item["role"] != "unknown" for item in outputs["grammar"]["typography_role_grammar"])
    assert all(item["independent_support_count"] <= len(item["supporting_container_ids"]) for item in outputs["grammar"]["typography_role_grammar"])


def test_candidate_state_components_bind_cp2_inputs_resolver_and_all_output_schemas():
    from thesis_deck_system.phase3_checkpoint3 import candidate_state_components, resolve_checkpoint3

    outputs = resolve_checkpoint3(*_inputs())
    components = candidate_state_components(outputs["evidence"]["input_hashes"])
    required = {"cp2:shell", "cp2:body", "cp2:manifest", "cp2:checkpoint2_qa", "resolver:phase3_checkpoint3.py", "schema:professor-template-resolved.schema.json", "schema:body-composition-profile.schema.json", "schema:professor-visual-grammar-v3.schema.json", "schema:visual-style-profile.schema.json", "schema:resolver-evidence.schema.json", "schema:checkpoint-3-qa.schema.json"}
    assert required <= set(components)
    assert outputs["evidence"]["candidate_state"]["component_hashes"] == components


def test_explicit_binding_rejects_swapped_overlapping_object_ids_and_insufficient_candidates():
    from thesis_deck_system.phase3_checkpoint3 import Checkpoint3ResolutionError, resolve_body_grammar

    _, body, _, _ = _inputs()
    swapped = copy.deepcopy(body["descriptor"])
    # Local object identifiers repeat by slide.  Swapping a binding must therefore
    # fail its composite structural fingerprint instead of silently relabelling.
    first, second = swapped["candidate_families"][0], swapped["candidate_families"][1]
    first["bound_slide_id"], second["bound_slide_id"] = second["bound_slide_id"], first["bound_slide_id"]
    with pytest.raises(Checkpoint3ResolutionError, match="fingerprint"):
        resolve_body_grammar(swapped)

    insufficient = copy.deepcopy(body["descriptor"])
    candidates = [item for item in insufficient["candidate_families"] if item["family"] == "other_insufficient_structural_evidence"]
    assert len(candidates) >= 2
    candidates[0]["bound_slide_id"], candidates[1]["bound_slide_id"] = candidates[1]["bound_slide_id"], candidates[0]["bound_slide_id"]
    with pytest.raises(Checkpoint3ResolutionError, match="fingerprint"):
        resolve_body_grammar(insufficient)


def test_explicit_binding_rejects_missing_slide_and_duplicate_evidence_fingerprint():
    from thesis_deck_system.phase3_checkpoint3 import Checkpoint3ResolutionError, resolve_body_grammar

    _, body, _, _ = _inputs()
    missing = copy.deepcopy(body["descriptor"])
    missing["candidate_families"][0]["bound_slide_id"] = "SL999"
    with pytest.raises(Checkpoint3ResolutionError, match="missing bound slide"):
        resolve_body_grammar(missing)

    duplicate = copy.deepcopy(body["descriptor"])
    duplicate["candidate_families"][1]["binding_fingerprint"] = duplicate["candidate_families"][0]["binding_fingerprint"]
    with pytest.raises(Checkpoint3ResolutionError, match="fingerprint"):
        resolve_body_grammar(duplicate)


def test_role_level_typography_requires_independent_slides_for_recurrence():
    from thesis_deck_system.phase3_checkpoint3 import _typography

    body = {
        "profile_id": "P3-LAYOUT-EXEMPLAR-2",
        "body_measurements": [
            {"slide_id": "SL001", "typography_observations": [{"role": "body", "role_confidence": "structurally_supported", "script_role": "latin", "family": "Arial", "font_evidence_state": "explicit_font", "size_pt": 18, "weight": "regular", "style": "normal", "source_scope": "slide_body", "supporting_object_id": "O001"}]},
            {"slide_id": "SL002", "typography_observations": [{"role": "body", "role_confidence": "structurally_supported", "script_role": "latin", "family": "Arial", "font_evidence_state": "explicit_font", "size_pt": 18, "weight": "regular", "style": "normal", "source_scope": "slide_body", "supporting_object_id": "O001"}]},
        ],
    }
    grammar = _typography([], body)
    assert len(grammar) == 1
    assert grammar[0]["independent_support_count"] == 2
    assert grammar[0]["evidence_tier"] == "recurring_pattern"


def test_candidate_state_hash_changes_for_cp2_and_source_or_schema_component_mutation(monkeypatch):
    import thesis_deck_system.phase3_checkpoint3 as cp3

    outputs = cp3.resolve_checkpoint3(*_inputs())
    hashes = outputs["evidence"]["input_hashes"]
    baseline = cp3._candidate_state_hash(hashes)
    changed_cp2 = {**hashes, "body": "0" * 64}
    assert cp3._candidate_state_hash(changed_cp2) != baseline

    original = Path.read_bytes
    def altered(self):
        if self.name in {"phase3_checkpoint3.py", "resolver-evidence.schema.json"}:
            return b"CP3 controlled mutation"
        return original(self)
    monkeypatch.setattr(Path, "read_bytes", altered)
    assert cp3._candidate_state_hash(hashes) != baseline
