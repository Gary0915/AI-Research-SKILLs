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
    assert any(item["value"] is None for item in baseline["body"]["metric_tokens"])
    assert baseline["body"]["metric_tokens"] != changed["body"]["metric_tokens"]


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
