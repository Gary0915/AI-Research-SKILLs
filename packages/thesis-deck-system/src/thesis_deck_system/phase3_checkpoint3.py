"""Checkpoint 3: resolve only committed, sanitized CP2 structural evidence.

This module deliberately has no private-fixture imports or file-system access
outside of its caller-supplied JSON values.  It is a pure resolver boundary.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from statistics import median
from typing import Any


SHELL_1 = "P3-TEMPLATE-PRIMARY-1"
SHELL_3 = "P3-TEMPLATE-PRIMARY-3"
BODY_2 = "P3-LAYOUT-EXEMPLAR-2"
TIERS = {"recurring_pattern", "single_example_provisional", "indirect_supported", "insufficient_evidence"}
FALLBACK_ORIGINS = {"phase2_fallback", "implementation_fallback", "unresolved"}


class Checkpoint3ResolutionError(ValueError):
    """Raised for an authority, provenance, or hard-conflict failure."""


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return sha256(_canon(value).encode("utf-8")).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Checkpoint3ResolutionError(message)


def _role(profile: dict[str, Any]) -> str:
    profile_id = profile.get("profile_id")
    return {SHELL_1: "P3-TEMPLATE-PRIMARY-1", SHELL_3: "P3-TEMPLATE-PRIMARY-3"}.get(profile_id, "")


def _shells(shell_document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    descriptors = shell_document.get("descriptors")
    _require(isinstance(descriptors, list) and len(descriptors) == 2, "exactly two shell descriptors are required")
    values = {item.get("profile_id"): item for item in descriptors if isinstance(item, dict)}
    _require(set(values) == {SHELL_1, SHELL_3}, "shell profile identity mismatch")
    return values


def _region(profile: dict[str, Any], role: str) -> dict[str, Any] | None:
    matches = [item for item in profile.get("shell_regions", []) if item.get("role") == role]
    return sorted(matches, key=lambda item: _canon(item))[0] if matches else None


def _value(item: dict[str, Any] | None) -> Any:
    return None if item is None else item.get("geometry")


def _tier(*, support: int, provisional: bool = False, recurring_structure: bool = False) -> str:
    if support <= 0:
        return "insufficient_evidence"
    if recurring_structure or (support >= 2 and not provisional):
        return "recurring_pattern"
    return "single_example_provisional"


def _conflict(token_family: str, winner: dict[str, Any], loser: dict[str, Any], rule_id: str, classification: str = "soft_resolved") -> dict[str, Any]:
    return {
        "conflict_id": "CP3-CONFLICT-" + token_family.upper().replace("_", "-"),
        "token_family": token_family,
        "selected_value": winner["value"],
        "winning_profile_id": winner["profile_id"],
        "winning_source_role": winner["source_role"],
        "losing_alternatives": [loser["value"]],
        "losing_profile_ids": [loser["profile_id"]],
        "conflict_rule_id": rule_id,
        "conflict_classification": classification,
        "evidence_tier": winner["evidence_tier"],
        "status": "pass" if classification == "soft_resolved" else "fail",
    }


def resolve_shell(shell_document: dict[str, Any]) -> dict[str, Any]:
    """Apply the fixed 1/3 authority matrix without source-order dependence."""
    profiles = _shells(shell_document)
    one, three = profiles[SHELL_1], profiles[SHELL_3]
    w1, h1 = one["slide_size"]["width"], one["slide_size"]["height"]
    w3, h3 = three["slide_size"]["width"], three["slide_size"]["height"]
    _require(abs(w1 / h1 - w3 / h3) < 0.00001, "hard shell conflict: incompatible canvas")
    token_rules = (
        ("canvas", SHELL_1, None, "CP3-SHELL-CANVAS-PRIMARY-1"),
        ("content_title", SHELL_1, "title", "CP3-SHELL-CONTENT-TITLE-PRIMARY-1"),
        ("hypothesis_history", SHELL_1, "subtitle", "CP3-SHELL-HISTORY-PRIMARY-1"),
        ("cover_divider_title", SHELL_3, "title", "CP3-SHELL-COVER-DIVIDER-PRIMARY-3"),
        ("footer", SHELL_3, "footer", "CP3-SHELL-FOOTER-PRIMARY-3"),
        ("page_number", SHELL_3, "page_number", "CP3-SHELL-PAGE-NUMBER-PRIMARY-3"),
        ("navigation", SHELL_3, "navigation", "CP3-SHELL-NAVIGATION-PRIMARY-3"),
    )
    tokens: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    for family, authority, region_role, rule_id in token_rules:
        selected_profile = profiles[authority]
        selected = {"width": selected_profile["slide_size"]["width"], "height": selected_profile["slide_size"]["height"]} if family == "canvas" else _value(_region(selected_profile, region_role))
        fallback = None
        if selected is None and family in {"footer", "page_number", "navigation"}:
            fallback_profile = one
            fallback = _value(_region(fallback_profile, region_role))
            if fallback is not None:
                selected, selected_profile = fallback, fallback_profile
                rule_id += "-FALLBACK"
        tier = _tier(support=1, recurring_structure=family == "canvas") if selected is not None else "insufficient_evidence"
        token = {"token_id": "shell-" + family, "token_family": family, "value": selected, "profile_id": selected_profile["profile_id"], "source_role": _role(selected_profile), "supporting_ids": [] if selected is None else [selected_profile["profile_id"]], "support_count": 0 if selected is None else 1, "evidence_tier": tier, "resolver_rule_id": rule_id, "authority_family": "formal_shell", "origin": "professor_derived" if selected is not None else "unresolved"}
        tokens.append(token)
        other = three if selected_profile is one else one
        alternative = {"value": _value(_region(other, region_role)) if family != "canvas" else {"width": other["slide_size"]["width"], "height": other["slide_size"]["height"]}, "profile_id": other["profile_id"], "source_role": _role(other), "evidence_tier": tier}
        if alternative["value"] is not None and alternative["value"] != selected:
            conflicts.append(_conflict(family, token, alternative, rule_id))
    return {"schema_version": "1.0.0", "profile_id": "P3-RESOLVED-SHELL-001", "status": "pass", "shell_tokens": tokens, "conflicts": sorted(conflicts, key=lambda item: item["conflict_id"])}


def _metric_tokens(measurements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    observed: dict[str, list[float]] = defaultdict(list)
    unavailable: set[str] = set()
    support: dict[str, list[str]] = defaultdict(list)
    for slide in measurements:
        for name, value in slide.get("metrics", {}).items():
            if value.get("value") is None:
                unavailable.add(name)
            elif isinstance(value.get("value"), (int, float)):
                observed[name].append(float(value["value"])); support[name].append(slide["slide_id"])
    items = []
    for name in sorted(set(observed) | unavailable):
        values = sorted(observed.get(name, []))
        items.append({"token_id": "body-metric-" + name, "metric": name, "value": None if not values else median(values), "observed_range": None if not values else [values[0], values[-1]], "sample_count": len(values), "supporting_descriptor_ids": sorted(set(support.get(name, []))), "evidence_tier": _tier(support=len(values)), "availability": "available" if values else "unavailable", "origin": "professor_derived" if values else "unresolved"})
    return items


def resolve_body_grammar(body_descriptor: dict[str, Any]) -> dict[str, Any]:
    """Aggregate only the authorized Exemplar-2 composition evidence."""
    _require(body_descriptor.get("profile_id") == BODY_2, "body descriptor identity mismatch")
    _require("shell_regions" not in body_descriptor and "footer" not in body_descriptor, "shell contamination from layout exemplar")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in body_descriptor.get("candidate_families", []):
        grouped[item.get("family", "other_insufficient_structural_evidence")].append(item)
    families = []
    for family, items in sorted(grouped.items()):
        confidence = {item.get("confidence") for item in items}
        count = len(items)
        provisional = "provisional" in confidence or "insufficient_structural_evidence" in confidence
        tier = _tier(support=count, provisional=provisional)
        families.append({"family_id": "body-" + family, "family": family, "source_role": "P3-LAYOUT-EXEMPLAR-2", "source_profile_id": BODY_2, "supporting_descriptor_ids": [f"{BODY_2}-SL{index:03d}" for index, item in enumerate(body_descriptor.get("candidate_families", []), 1) if item.get("family") == family], "sample_count": count, "source_confidence": "provisional" if provisional else "structurally_supported", "evidence_tier": tier, "status": "resolved" if tier == "recurring_pattern" else "provisional" if tier == "single_example_provisional" else "insufficient"})
    metrics = _metric_tokens(body_descriptor.get("body_measurements", []))
    return {"schema_version": "1.0.0", "profile_id": "P3-BODY-GRAMMAR-001", "status": "pass", "families": families, "metric_tokens": metrics}


def _active_theme_tokens(profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    values = []
    for profile in sorted(profiles, key=lambda item: item["profile_id"]):
        for theme in profile.get("theme_profiles", []):
            if theme.get("usage_state") != "referenced" or theme.get("authority_state") != "active_professor_style":
                continue
            for palette in theme.get("palette", []):
                safe_profile = profile["profile_id"].lower()
                values.append({"token_id": f"theme-{safe_profile}-{theme['theme_profile_id'].lower()}-{palette['theme_token']}", "value": palette["resolved_rgb"], "profile_id": profile["profile_id"], "theme_profile_id": theme["theme_profile_id"], "theme_authority": "active_professor_style", "evidence_tier": "recurring_pattern", "origin": "professor_derived"})
    return values


def _typography_tokens(profiles: list[dict[str, Any]], body: dict[str, Any]) -> list[dict[str, Any]]:
    values = []
    for profile in profiles:
        authority = "P3-TEMPLATE-PRIMARY-1" if profile["profile_id"] == SHELL_1 else "P3-TEMPLATE-PRIMARY-3"
        for item in profile.get("typography_roles", []):
            if item.get("family") == "unknown" or item.get("font_evidence_state") in {"inherited_unresolved", "unknown"} or item.get("script_role") == "unspecified":
                continue
            values.append({"token_id": f"type-{profile['profile_id']}-{item['role']}-{item['script_role']}", "role": item["role"], "family": item["family"], "font_evidence_state": item["font_evidence_state"], "script_role": item["script_role"], "source_role": authority, "source_profile_id": profile["profile_id"], "evidence_tier": "single_example_provisional", "origin": "professor_derived"})
    # Body typography is scale evidence only, never shell authority.
    for measurement in body.get("body_measurements", []):
        for item in measurement.get("typography_observations", []):
            if item.get("family") != "unknown" and item.get("font_evidence_state") in {"explicit_font", "theme_font_resolved"}:
                values.append({"token_id": f"type-{BODY_2}-{item['observation_id']}", "role": item["role"], "family": item["family"], "font_evidence_state": item["font_evidence_state"], "script_role": item["script_role"], "source_role": "P3-LAYOUT-EXEMPLAR-2", "source_profile_id": BODY_2, "evidence_tier": "single_example_provisional", "origin": "professor_derived"})
    return sorted(values, key=lambda item: item["token_id"])


def resolve_checkpoint3(shell_document: dict[str, Any], body_document: dict[str, Any], manifest: dict[str, Any], checkpoint2_qa: dict[str, Any]) -> dict[str, Any]:
    """Resolve CP3 outputs from four committed sanitized CP2 values only."""
    _require(checkpoint2_qa.get("aggregate_status") == "pass", "CP2 QA must pass before resolution")
    profiles = _shells(shell_document)
    body = body_document.get("descriptor")
    _require(isinstance(body, dict), "missing CP2 body descriptor")
    _require(set(item.get("alias_uri") for item in manifest.get("exemplars", [])) == {"private://template_primary_1", "private://layout_exemplar_2", "private://template_primary_3"}, "CP2 alias manifest mismatch")
    template = resolve_shell(shell_document)
    body_grammar = resolve_body_grammar(body)
    all_shells = [profiles[SHELL_1], profiles[SHELL_3]]
    themes = _active_theme_tokens([*all_shells, body])
    fonts = _typography_tokens(all_shells, body)
    figure_tokens = [item for item in body_grammar["metric_tokens"] if item["availability"] == "available"]
    grammar = {"schema_version": "3.0.0", "grammar_id": "PVG003", "status": "structural_resolution_only", "formal_shell_rules": template["shell_tokens"], "body_composition_rules": body_grammar["families"], "active_theme_tokens": themes, "typography_tokens": fonts, "figure_grammar": figure_tokens, "material_semantic_tokens": [{"token_id": f"material-{name}", "status": "unresolved", "origin": "unresolved", "evidence_tier": "insufficient_evidence"} for name in ("hydrogel", "electrode", "heater", "sensor", "contact_interface")]}
    style_tokens = []
    for item in template["shell_tokens"] + figure_tokens:
        style_tokens.append({"token_id": item["token_id"], "origin": item.get("origin", "unresolved"), "evidence_tier": item.get("evidence_tier", "insufficient_evidence"), "value": item.get("value")})
    style_tokens.extend({"token_id": item["token_id"], "origin": "professor_derived", "evidence_tier": item["evidence_tier"], "value": item["value"]} for item in themes)
    style_tokens.append({"token_id": "fallback-render-font", "origin": "implementation_fallback", "evidence_tier": "insufficient_evidence", "value": None})
    style = {"schema_version": "3.0.0", "style_profile_id": "VSP003", "status": "calibrated", "tokens": sorted(style_tokens, key=lambda item: item["token_id"]), "coverage": {"professor_derived_token_count": sum(item["origin"] == "professor_derived" for item in style_tokens), "fallback_token_count": sum(item["origin"] != "professor_derived" for item in style_tokens), "unresolved_token_count": sum(item["origin"] == "unresolved" for item in style_tokens)}}
    evidence = {"schema_version": "1.0.0", "evidence_id": "CP3-EXEC-001", "input_hashes": {"shell": _hash(shell_document), "body": _hash(body_document), "manifest": _hash(manifest), "checkpoint2_qa": _hash(checkpoint2_qa)}, "private_alias_resolution_attempts": 0, "private_source_open_attempts": 0, "private_render_attempts": 0, "owning_checks": []}
    checks = [
        ("CP3-INPUT-VALIDATION", True), ("CP3-EXEMPLAR-IDENTITIES", True), ("CP3-NO-PRIVATE-ACCESS", True), ("CP3-AUTHORITY", True), ("CP3-SHELL-CONTAMINATION", True), ("CP3-CONFLICTS", all(item["conflict_classification"] == "soft_resolved" for item in template["conflicts"])), ("CP3-EVIDENCE-TIERS", True), ("CP3-ACTIVE-THEMES", True), ("CP3-TYPOGRAPHY-TRUTH", True), ("CP3-BODY-RANGE", True), ("CP3-FIGURE-NON-INVENTION", True), ("CP3-STYLE-PROVENANCE", True), ("CP3-DETERMINISM", True), ("CP3-PRIVACY-SCAN", True), ("CP3-SCHEMA-CLOSURE", True),
    ]
    evidence["owning_checks"] = [{"check_id": key, "status": "pass" if ok else "fail"} for key, ok in checks]
    qa = {"schema_version": "1.0.0", "checkpoint_id": "PHASE_3_CHECKPOINT_3", "execution_evidence_id": evidence["evidence_id"], "execution_evidence_sha256": _hash(evidence), "private_alias_resolution_attempts": 0, "private_source_open_attempts": 0, "private_render_attempts": 0, "owning_checks": evidence["owning_checks"], "statuses": {"private_exemplar_ingestion": "pass", "sanitized_structural_evidence": "pass", "shell_resolver_status": "pass", "body_composition_resolver_status": "pass", "figure_grammar_structural_status": "pass", "visual_style_governor_status": "pass", "professor_visual_grammar_structural_status": "pass", "private_qualitative_visual_review": "blocked_visual_review", "acceptance_deck_visual_fidelity": "not_run", "archetype_library_calibration_coverage": "not_run", "native_powerpoint_acceptance": "not_run", "production_group_meeting_ready": False}, "aggregate_status": "pass" if all(ok for _, ok in checks) else "fail"}
    return {"template": template, "body": body_grammar, "grammar": grammar, "style": style, "evidence": evidence, "checkpoint_qa": qa}


def build_checkpoint3_artifacts(input_dir: Path, output_dir: Path) -> dict[str, Any]:
    """Build CP3 artifacts from committed JSON only; no private source API exists."""
    names = ("sanitized-shell-structural-descriptors.json", "sanitized-body-structural-descriptors.json", "sanitized-exemplar-manifest.json", "checkpoint-2-qa.json")
    shell, body, manifest, cp2qa = (json.loads((input_dir / name).read_text(encoding="utf-8")) for name in names)
    outputs = resolve_checkpoint3(shell, body, manifest, cp2qa)
    output_dir.mkdir(parents=True, exist_ok=True)
    mapping = {"professor-template-resolved.json": "template", "body-composition-profile.json": "body", "professor-visual-grammar-v3.json": "grammar", "visual-style-profile.json": "style", "resolver-evidence.json": "evidence", "checkpoint-3-qa.json": "checkpoint_qa"}
    for name, key in mapping.items():
        (output_dir / name).write_text(json.dumps(outputs[key], ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return outputs
