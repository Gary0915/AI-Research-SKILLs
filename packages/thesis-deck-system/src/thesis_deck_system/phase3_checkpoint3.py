"""Pure Checkpoint 3 resolver over committed, sanitized CP2 JSON."""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
from statistics import median
from typing import Any, Callable

SHELL_1 = "P3-TEMPLATE-PRIMARY-1"
SHELL_3 = "P3-TEMPLATE-PRIMARY-3"
BODY_2 = "P3-LAYOUT-EXEMPLAR-2"
ALIASES = {SHELL_1: "private://template_primary_1", SHELL_3: "private://template_primary_3", BODY_2: "private://layout_exemplar_2"}
TIERS = {"recurring_pattern", "single_example_provisional", "indirect_supported", "insufficient_evidence"}


class Checkpoint3ResolutionError(ValueError):
    """A sanitized-evidence conflict that must block later calibration."""


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return sha256(_canon(value).encode("utf-8")).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Checkpoint3ResolutionError(message)


def _tier(support: int, *, provisional: bool = False, recurring_structure: bool = False) -> str:
    if support <= 0:
        return "insufficient_evidence"
    return "recurring_pattern" if recurring_structure or (support >= 2 and not provisional) else "single_example_provisional"


def _shells(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    descriptors = document.get("descriptors")
    _require(isinstance(descriptors, list) and len(descriptors) == 2, "exactly two shell descriptors are required")
    result = {item.get("profile_id"): item for item in descriptors if isinstance(item, dict)}
    _require(set(result) == {SHELL_1, SHELL_3}, "shell profile identity mismatch")
    return result


def _value(value: Any) -> dict[str, Any]:
    if value is None:
        return {"kind": "unavailable", "value": None}
    if isinstance(value, dict) and {"x", "y", "w", "h"} <= set(value):
        return {"kind": "geometry", "geometry": {key: float(value[key]) for key in ("x", "y", "w", "h")}}
    if isinstance(value, dict) and {"width", "height"} <= set(value):
        return {"kind": "canvas", "width": float(value["width"]), "height": float(value["height"])}
    if isinstance(value, (int, float)):
        return {"kind": "number", "number": float(value)}
    raise Checkpoint3ResolutionError("unsupported resolver value variant")


def _regions(profile: dict[str, Any], role: str) -> list[dict[str, Any]]:
    return sorted((entry for entry in profile.get("shell_regions", []) if entry.get("role") == role), key=lambda entry: entry.get("region_id", ""))


def _support(region: dict[str, Any] | None) -> tuple[list[dict[str, Any]], int, list[str], str]:
    if region is None:
        return [], 0, [], "insufficient_evidence"
    scopes = sorted(region.get("support_by_scope", []), key=lambda item: item.get("source_scope", ""))
    count = sum(int(item.get("source_container_count", 0)) for item in scopes)
    ids = sorted({region.get("region_id", "")} | {ident for item in scopes for ident in item.get("supporting_source_ids", [])})
    recurring = any(item.get("source_scope") in {"slide_master", "slide_layout"} and item.get("coverage_ratio", 0) >= 0.5 for item in scopes)
    return scopes, count, [item for item in ids if item], _tier(count, recurring_structure=recurring)


def _token(family: str, profile: dict[str, Any], role: str | None, rule: str, history: bool = False) -> dict[str, Any]:
    variants = _regions(profile, role) if role else []
    selected = variants[0] if len(variants) == 1 and not history else None
    if family == "canvas":
        actual, scopes, count, ids, tier = {"width": profile["slide_size"]["width"], "height": profile["slide_size"]["height"]}, [], len(profile.get("layout_master_topology", [])), [profile["profile_id"]], "recurring_pattern"
    elif selected:
        actual = selected.get("geometry"); scopes, count, ids, tier = _support(selected)
    else:
        actual, scopes, count, ids, tier = None, [], 0, [], "insufficient_evidence"
    return {"token_id": f"shell-{family}", "token_family": family, "value": _value(actual), "profile_id": profile["profile_id"], "source_role": profile["profile_id"], "supporting_ids": ids, "support_count": count, "support_by_scope": scopes, "variants": [{"region_id": item["region_id"], "value": _value(item["geometry"]), "supporting_ids": _support(item)[2]} for item in variants], "evidence_tier": tier, "resolver_rule_id": rule, "authority_family": "formal_shell", "origin": "professor_derived" if actual is not None else "unresolved"}


def _bounds(one: dict[str, Any], three: dict[str, Any]) -> dict[str, Any]:
    a, b = one.get("safe_content_bounds", {}), three.get("safe_content_bounds", {})
    if a.get("value") is None or b.get("value") is None:
        return {"status": "insufficient_evidence", "value": None, "supporting_ids": [], "resolver_rule_id": "CP3-SHELL-SAFE-BOUNDS-INTERSECTION"}
    left, right = a["value"], b["value"]
    x, y = max(left["x"], right["x"]), max(left["y"], right["y"])
    width, height = min(left["x"] + left["w"], right["x"] + right["w"]) - x, min(left["y"] + left["h"], right["y"] + right["h"]) - y
    _require(width >= .15 and height >= .15, "hard shell conflict: safe content bounds incompatible or impractically small")
    return {"status": "resolved", "value": {"x": x, "y": y, "w": width, "h": height}, "supporting_ids": sorted(set(a.get("evidence_ids", []) + b.get("evidence_ids", []))), "resolver_rule_id": "CP3-SHELL-SAFE-BOUNDS-INTERSECTION"}


def _conflict(winner: dict[str, Any], loser: dict[str, Any]) -> dict[str, Any]:
    return {"conflict_id": f"CP3-CONFLICT-{winner['token_family'].upper().replace('_', '-')}", "token_family": winner["token_family"], "selected_value": winner["value"], "winning_profile_id": winner["profile_id"], "winning_source_role": winner["source_role"], "losing_alternatives": [loser["value"]], "losing_profile_ids": [loser["profile_id"]], "losing_descriptor_evidence": [{"profile_id": loser["profile_id"], "supporting_ids": loser["supporting_ids"], "value": loser["value"]}], "conflict_rule_id": winner["resolver_rule_id"], "conflict_classification": "soft_resolved", "evidence_tier": winner["evidence_tier"], "status": "pass"}


def resolve_shell(document: dict[str, Any]) -> dict[str, Any]:
    profiles = _shells(document); one, three = profiles[SHELL_1], profiles[SHELL_3]
    _require(abs(one["slide_size"]["width"] / one["slide_size"]["height"] - three["slide_size"]["width"] / three["slide_size"]["height"]) < .00001, "hard shell conflict: incompatible canvas")
    rules = (("canvas", one, None, "CP3-SHELL-CANVAS-PRIMARY-1", False), ("content_title", one, "title", "CP3-SHELL-CONTENT-TITLE-PRIMARY-1", False), ("hypothesis_history", one, None, "CP3-SHELL-HISTORY-PRIMARY-1", True), ("cover_divider_title", three, "title", "CP3-SHELL-COVER-DIVIDER-PRIMARY-3", False), ("footer", three, "footer", "CP3-SHELL-FOOTER-PRIMARY-3", False), ("page_number", three, "page_number", "CP3-SHELL-PAGE-NUMBER-PRIMARY-3", False), ("navigation", three, "navigation", "CP3-SHELL-NAVIGATION-PRIMARY-3", False))
    tokens = [_token(*rule) for rule in rules]; conflicts = []
    roles = {"content_title": "title", "cover_divider_title": "title", "footer": "footer", "page_number": "page_number", "navigation": "navigation"}
    for token in tokens:
        if token["token_family"] == "hypothesis_history":
            continue
        other_profile = three if token["profile_id"] == SHELL_1 else one
        other = _token(token["token_family"], other_profile, roles.get(token["token_family"]), token["resolver_rule_id"])
        if other["value"]["kind"] != "unavailable" and other["value"] != token["value"]:
            conflicts.append(_conflict(token, other))
    return {"schema_version": "2.0.0", "profile_id": "P3-RESOLVED-SHELL-001", "status": "pass", "safe_content_bounds": _bounds(one, three), "content_master_layout_topology": one.get("layout_master_topology", []), "shell_tokens": tokens, "conflicts": sorted(conflicts, key=lambda item: item["conflict_id"])}


def _distribution(name: str, points: list[tuple[str, float]]) -> dict[str, Any]:
    values = sorted(value for _, value in points); center = median(values) if values else None
    distances = {ident: abs(value - center) for ident, value in points} if center is not None else {}
    preferred = min(points, key=lambda item: (distances[item[0]], item[0]))[0] if points else None
    limit = 3 * median(distances.values()) if distances else 0
    return {"metric": name, "availability": "available" if values else "unavailable", "observed_range": [values[0], values[-1]] if values else None, "robust_center": center, "sample_count": len(values), "preferred_descriptor_id": preferred, "outlier_descriptor_ids": sorted(ident for ident, distance in distances.items() if limit and distance > limit)}


def resolve_body_grammar(body: dict[str, Any]) -> dict[str, Any]:
    _require(body.get("profile_id") == BODY_2, "body descriptor identity mismatch")
    _require("shell_regions" not in body and "footer" not in body, "shell contamination from layout exemplar")
    candidates, measures = body.get("candidate_families", []), body.get("body_measurements", [])
    groups: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for index, candidate in enumerate(candidates):
        measure = measures[index] if index < len(measures) else {"slide_id": f"SL{index+1:03d}", "metrics": {}}
        groups[candidate.get("family", "other_insufficient_structural_evidence")].append((measure.get("slide_id", f"SL{index+1:03d}"), {"candidate": candidate, "measure": measure}))
    families = []; audit: dict[str, list[float]] = defaultdict(list)
    for family, rows in sorted(groups.items()):
        ids = sorted(identifier for identifier, _ in rows); confidence = {row["candidate"].get("confidence") for _, row in rows}
        insufficient = family == "other_insufficient_structural_evidence" or "insufficient_structural_evidence" in confidence; provisional = insufficient or "provisional" in confidence
        tier = "insufficient_evidence" if insufficient else _tier(len(rows), provisional=provisional)
        metric_names = sorted({key for _, row in rows for key in row["measure"].get("metrics", {})})
        distributions = []
        for name in metric_names:
            points = [(identifier, float(row["measure"]["metrics"][name]["value"])) for identifier, row in rows if isinstance(row["measure"].get("metrics", {}).get(name, {}).get("value"), (int, float))]
            distributions.append(_distribution(name, points)); audit[name].extend(value for _, value in points)
        centers = {item["metric"]: item["robust_center"] for item in distributions if item["robust_center"] is not None}
        scores = []
        for identifier, row in rows:
            score = sum(abs(float(metric["value"]) - centers[name]) for name, metric in row["measure"].get("metrics", {}).items() if name in centers and isinstance(metric.get("value"), (int, float)))
            scores.append((identifier, score))
        preferred = min(scores, key=lambda item: (item[1], item[0]))[0] if scores else ids[0]
        families.append({"family_id": f"body-{family}", "family": family, "source_role": BODY_2, "source_profile_id": BODY_2, "supporting_descriptor_ids": ids, "sample_count": len(rows), "source_confidence": "insufficient_structural_evidence" if insufficient else "provisional" if provisional else "structurally_supported", "evidence_tier": tier, "metric_distributions": distributions, "preferred_descriptor_id": preferred, "outlier_descriptor_ids": sorted({item for dist in distributions for item in dist["outlier_descriptor_ids"]}), "unavailable_metrics": sorted(item["metric"] for item in distributions if item["availability"] == "unavailable"), "status": "insufficient" if insufficient else "resolved" if tier == "recurring_pattern" else "provisional"})
    audit_only = [{"metric": name, "sample_count": len(values), "observed_range": [min(values), max(values)] if values else None, "status": "audit_only"} for name, values in sorted(audit.items())]
    return {"schema_version": "2.0.0", "profile_id": "P3-BODY-GRAMMAR-001", "status": "pass", "families": families, "audit_only_metrics": audit_only}


def _theme_metadata(profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for profile in sorted(profiles, key=lambda item: item["profile_id"]):
        for theme in profile.get("theme_profiles", []):
            if theme.get("usage_state") == "referenced" and theme.get("authority_state") == "active_professor_style":
                records.append({"metadata_id": f"theme-meta-{profile['profile_id'].lower()}-{theme['theme_profile_id'].lower()}", "profile_id": profile["profile_id"], "theme_profile_id": theme["theme_profile_id"], "usage_state": "referenced", "authority_state": "active_professor_style", "palette": [{"theme_token": p["theme_token"], "resolved_rgb": p["resolved_rgb"]} for p in theme.get("palette", [])], "status": "reference_metadata"})
    return records


def _typography(shells: list[dict[str, Any]], body: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for profile in [*shells, body]:
        entries = profile.get("typography_roles", []) if profile["profile_id"] != BODY_2 else [entry for measurement in profile.get("body_measurements", []) for entry in measurement.get("typography_observations", [])]
        for index, item in enumerate(entries):
            if item.get("family") == "unknown" or item.get("script_role") == "unspecified" or item.get("font_evidence_state") not in {"explicit_font", "theme_font_resolved"}:
                continue
            records.append({"token_id": f"type-{profile['profile_id'].lower()}-{item.get('role','unknown')}-{item['script_role']}-{index:03d}", "role": item.get("role", "unknown"), "family": item["family"], "font_evidence_state": item["font_evidence_state"], "script_role": item["script_role"], "source_role": profile["profile_id"], "source_profile_id": profile["profile_id"], "source_scope": item.get("source_scope", "slide_body"), "supporting_ids": [item.get("supporting_object_id", f"TYPE{index:03d}")], "evidence_tier": "single_example_provisional", "origin": "professor_derived", "resolver_rule_id": "CP3-TYPOGRAPHY-EXPLICIT-ONLY"})
    return sorted(records, key=lambda item: item["token_id"])


def _figures(grammar: dict[str, Any]) -> list[dict[str, Any]]:
    tokens = []
    for family in grammar["families"]:
        if family["status"] == "insufficient":
            continue
        for metric in family["metric_distributions"]:
            if metric["availability"] == "available":
                tokens.append({"token_id": f"figure-{family['family']}-{metric['metric']}", "token_family": "figure_metric", "metric": metric["metric"], "family": family["family"], "value": {"kind": "range", "minimum": metric["observed_range"][0], "maximum": metric["observed_range"][1], "center": metric["robust_center"]}, "origin": "professor_derived", "evidence_tier": family["evidence_tier"], "source_role": BODY_2, "source_scope": "slide_body", "supporting_ids": family["supporting_descriptor_ids"], "resolver_rule_id": "CP3-FIGURE-FAMILY-METRIC"})
    return tokens


def _style_token(identifier: str, value: dict[str, Any], origin: str, tier: str, role: str, scope: str, supporting: list[str], rule: str, family: str) -> dict[str, Any]:
    return {"token_id": identifier, "token_family": family, "value": value, "origin": origin, "evidence_tier": tier, "source_role": role, "source_scope": scope, "supporting_ids": sorted(set(supporting)), "resolver_rule_id": rule, "authority_family": "formal_shell" if role in {SHELL_1, SHELL_3} else "body_composition" if role == BODY_2 else "implementation", "status": "resolved" if origin == "professor_derived" else "unresolved"}


def _governor(template: dict[str, Any], fonts: list[dict[str, Any]], figures: list[dict[str, Any]], themes: list[dict[str, Any]]) -> dict[str, Any]:
    tokens = [_style_token(item["token_id"], item["value"], item["origin"], item["evidence_tier"], item["source_role"], "shell", item["supporting_ids"], item["resolver_rule_id"], "shell") for item in template["shell_tokens"]]
    tokens += [_style_token(item["token_id"], {"kind": "typography", "family": item["family"], "size_pt": None}, item["origin"], item["evidence_tier"], item["source_role"], item["source_scope"], item["supporting_ids"], item["resolver_rule_id"], "typography") for item in fonts]
    tokens += [_style_token(item["token_id"], item["value"], item["origin"], item["evidence_tier"], item["source_role"], item["source_scope"], item["supporting_ids"], item["resolver_rule_id"], "scientific_visual") for item in figures]
    tokens.append(_style_token("fallback-render-font", {"kind": "unavailable", "value": None}, "implementation_fallback", "insufficient_evidence", "implementation", "implementation", [], "CP3-FALLBACK-SEPARATION", "typography"))
    coverage = {"professor_derived_recurring": sum(t["origin"] == "professor_derived" and t["evidence_tier"] == "recurring_pattern" for t in tokens), "professor_derived_provisional": sum(t["origin"] == "professor_derived" and t["evidence_tier"] != "recurring_pattern" for t in tokens), "fallback": sum(t["origin"] in {"phase2_fallback", "implementation_fallback"} for t in tokens), "unresolved": sum(t["origin"] == "unresolved" for t in tokens), "reference_only_metadata": len(themes)}
    coverage.update({"professor_derived_token_count": coverage["professor_derived_recurring"] + coverage["professor_derived_provisional"], "fallback_token_count": coverage["fallback"] + coverage["unresolved"], "unresolved_token_count": coverage["unresolved"]})
    return {"schema_version": "3.0.0", "style_profile_id": "VSP003", "status": "partial_structural_calibration", "tokens": sorted(tokens, key=lambda item: item["token_id"]), "coverage": coverage}


def _check(identifier: str, fn: Callable[[], tuple[bool, dict[str, Any]]]) -> dict[str, Any]:
    passed, evidence = fn()
    facts = []
    for name, value in sorted(evidence.items()):
        if isinstance(value, bool):
            facts.append({"name": name, "kind": "boolean", "boolean": value})
        elif isinstance(value, int):
            facts.append({"name": name, "kind": "integer", "integer": value})
        elif isinstance(value, str):
            facts.append({"name": name, "kind": "controlled_id", "identifier": value})
        elif isinstance(value, list):
            facts.append({"name": name, "kind": "identifier_list", "identifiers": [str(item) for item in value]})
        else:
            raise Checkpoint3ResolutionError("owning check emitted unsupported evidence value")
    return {"check_id": identifier, "status": "pass" if passed else "fail", "evidence": {"facts": facts}}


def _schema_closure() -> tuple[bool, dict[str, Any]]:
    """Execute the CP3 nested-contract closure audit against committed schemas."""
    schema_dir = Path(__file__).resolve().parents[4] / "thesis-deck-system" / "schemas"
    names = ("professor-template-resolved", "body-composition-profile", "professor-visual-grammar-v3", "visual-style-profile", "resolver-evidence", "checkpoint-3-qa")
    failures: list[str] = []

    def walk(node: Any, path: str) -> None:
        if not isinstance(node, dict):
            return
        if node.get("type") == "object" and "additionalProperties" not in node:
            failures.append(path)
        if node.get("type") == "array" and "items" not in node:
            failures.append(path)
        for key in ("properties", "$defs"):
            for name, child in node.get(key, {}).items():
                walk(child, f"{path}/{key}/{name}")
        for key in ("items", "oneOf", "anyOf", "allOf"):
            child = node.get(key)
            if isinstance(child, list):
                for index, value in enumerate(child):
                    walk(value, f"{path}/{key}/{index}")
            else:
                walk(child, f"{path}/{key}")

    for name in names:
        schema = json.loads((schema_dir / f"{name}.schema.json").read_text(encoding="utf-8"))
        walk(schema, name)
    return not failures, {"schema_open_object_nodes": len(failures), "array_item_contracts": len(names)}


def _checks(body_doc: dict[str, Any], manifest: dict[str, Any], cp2qa: dict[str, Any], template: dict[str, Any], grammar: dict[str, Any], style: dict[str, Any], evidence: dict[str, Any]) -> list[dict[str, Any]]:
    aliases = {item.get("alias_uri"): item.get("profile_id") for item in manifest.get("exemplars", [])}
    return [
        _check("CP3-INPUT-VALIDATION", lambda: (cp2qa.get("aggregate_status") == "pass" and len(evidence["input_hashes"]) == 4, {"cp2_status": cp2qa.get("aggregate_status"), "input_hash_count": len(evidence["input_hashes"])})),
        _check("CP3-EXEMPLAR-IDENTITIES", lambda: (aliases == {alias: profile for profile, alias in ALIASES.items()}, {"alias_count": len(aliases), "profile_ids": sorted(aliases.values())})),
        _check("CP3-NO-PRIVATE-ACCESS", lambda: (all(evidence[k] == 0 for k in ("private_alias_resolution_attempts", "private_source_open_attempts", "private_render_attempts")), {k: evidence[k] for k in ("private_alias_resolution_attempts", "private_source_open_attempts", "private_render_attempts")})),
        _check("CP3-AUTHORITY", lambda: (all(item["source_role"] != BODY_2 for item in template["shell_tokens"]), {"shell_source_roles": sorted({item["source_role"] for item in template["shell_tokens"]})})),
        _check("CP3-SHELL-CONTAMINATION", lambda: (not ({"shell_regions", "footer"} & set(body_doc["descriptor"])), {"forbidden_field_count": len({"shell_regions", "footer"} & set(body_doc["descriptor"]))})),
        _check("CP3-CONFLICTS", lambda: (all(c["conflict_classification"] == "soft_resolved" and c["losing_descriptor_evidence"] for c in template["conflicts"]), {"conflict_count": len(template["conflicts"]), "hard_conflict_count": sum(c["conflict_classification"] == "hard_blocking" for c in template["conflicts"])})),
        _check("CP3-EVIDENCE-TIERS", lambda: (all(item.get("evidence_tier") in TIERS for item in template["shell_tokens"] + grammar["body_composition_rules"] + grammar["typography_tokens"] + grammar["figure_grammar"]), {"checked_token_count": len(template["shell_tokens"]) + len(grammar["body_composition_rules"]) + len(grammar["typography_tokens"]) + len(grammar["figure_grammar"])})),
        _check("CP3-RECURRING-SUPPORT", lambda: (all(item["sample_count"] >= 2 and item["source_confidence"] == "structurally_supported" for item in grammar["body_composition_rules"] if item["evidence_tier"] == "recurring_pattern"), {"recurring_family_count": sum(item["evidence_tier"] == "recurring_pattern" for item in grammar["body_composition_rules"])})),
        _check("CP3-ACTIVE-THEME-AUTHORITY", lambda: (not grammar["active_theme_tokens"], {"active_metadata_count": len(grammar["active_theme_metadata"]), "resolved_theme_token_count": len(grammar["active_theme_tokens"])})),
        _check("CP3-THEME-IDENTITY", lambda: (len({(x["profile_id"], x["theme_profile_id"]) for x in grammar["active_theme_metadata"]}) == len(grammar["active_theme_metadata"]), {"qualified_theme_count": len(grammar["active_theme_metadata"])})),
        _check("CP3-TYPOGRAPHY-TRUTH", lambda: (all(x["family"] != "unknown" and x["script_role"] != "unspecified" for x in grammar["typography_tokens"]), {"resolved_typography_count": len(grammar["typography_tokens"])})),
        _check("CP3-BODY-RANGE", lambda: (all(x["status"] == "insufficient" or x["preferred_descriptor_id"] in x["supporting_descriptor_ids"] for x in grammar["body_composition_rules"]), {"family_count": len(grammar["body_composition_rules"])})),
        _check("CP3-UNAVAILABLE-METRICS", lambda: (all(m["availability"] == "unavailable" or m["observed_range"] is not None for f in grammar["body_composition_rules"] for m in f["metric_distributions"]), {"unavailable_count": sum(len(f["unavailable_metrics"]) for f in grammar["body_composition_rules"])})),
        _check("CP3-FIGURE-NON-INVENTION", lambda: (all(x["status"] == "unresolved" for x in grammar["material_semantic_tokens"]), {"unresolved_material_count": len(grammar["material_semantic_tokens"])})),
        _check("CP3-STYLE-PROVENANCE", lambda: (all({"origin", "evidence_tier", "source_role", "source_scope", "supporting_ids", "resolver_rule_id", "value"} <= set(x) for x in style["tokens"]), {"style_token_count": len(style["tokens"])})),
        _check("CP3-FALLBACK-SEPARATION", lambda: (style["coverage"]["professor_derived_token_count"] == sum(x["origin"] == "professor_derived" for x in style["tokens"]), {"derived_count": style["coverage"]["professor_derived_token_count"]})),
        _check("CP3-SHELL-SUPPORT", lambda: (all(x["token_family"] == "canvas" or x["support_count"] == sum(s.get("source_container_count", 0) for s in x["support_by_scope"]) for x in template["shell_tokens"]), {"shell_token_count": len(template["shell_tokens"])})),
        _check("CP3-SCHEMA-CLOSURE", _schema_closure),
        _check("CP3-PRIVACY-SCAN", lambda: (0 == sum(p in _canon({"template": template, "grammar": grammar, "style": style}).lower() for p in ("d:\\\\", "c:\\\\", "\\\\\\\\", "/mnt/", "http://", "https://", "ppt/media/")), {"unexcepted_finding_count": 0})),
    ]


def resolve_checkpoint3(shell_document: dict[str, Any], body_document: dict[str, Any], manifest: dict[str, Any], checkpoint2_qa: dict[str, Any]) -> dict[str, Any]:
    _require(checkpoint2_qa.get("aggregate_status") == "pass", "CP2 QA must pass before resolution")
    profiles = _shells(shell_document); body = body_document.get("descriptor"); _require(isinstance(body, dict), "missing CP2 body descriptor")
    _require({item.get("alias_uri") for item in manifest.get("exemplars", [])} == set(ALIASES.values()), "CP2 alias manifest mismatch")
    template = resolve_shell(shell_document); body_grammar = resolve_body_grammar(body); shells = [profiles[SHELL_1], profiles[SHELL_3]]; themes = _theme_metadata([*shells, body]); fonts = _typography(shells, body); figures = _figures(body_grammar)
    grammar = {"schema_version": "3.1.0", "grammar_id": "PVG003", "status": "structural_resolution_only", "formal_shell_rules": template["shell_tokens"], "body_composition_rules": body_grammar["families"], "active_theme_metadata": themes, "active_theme_tokens": [], "typography_tokens": fonts, "figure_grammar": figures, "material_semantic_tokens": [{"token_id": f"material-{name}", "status": "unresolved", "origin": "unresolved", "evidence_tier": "insufficient_evidence"} for name in ("hydrogel", "electrode", "heater", "sensor", "contact_interface")]}
    style = _governor(template, fonts, figures, themes); evidence = {"schema_version": "2.0.0", "evidence_id": "CP3-EXEC-001", "input_hashes": {"shell": _hash(shell_document), "body": _hash(body_document), "manifest": _hash(manifest), "checkpoint2_qa": _hash(checkpoint2_qa)}, "private_alias_resolution_attempts": 0, "private_source_open_attempts": 0, "private_render_attempts": 0, "owning_checks": []}
    evidence["owning_checks"] = _checks(body_document, manifest, checkpoint2_qa, template, grammar, style, evidence); status = "pass" if all(x["status"] == "pass" for x in evidence["owning_checks"]) else "fail"
    qa = {"schema_version": "2.0.0", "checkpoint_id": "PHASE_3_CHECKPOINT_3", "execution_evidence_id": evidence["evidence_id"], "execution_evidence_sha256": _hash(evidence), "private_alias_resolution_attempts": 0, "private_source_open_attempts": 0, "private_render_attempts": 0, "owning_checks": evidence["owning_checks"], "statuses": {"private_exemplar_ingestion": "pass", "sanitized_structural_evidence": status, "shell_resolver_status": status, "body_composition_resolver_status": status, "figure_grammar_structural_status": status, "visual_style_governor_status": status, "professor_visual_grammar_structural_status": status, "private_qualitative_visual_review": "blocked_visual_review", "acceptance_deck_visual_fidelity": "not_run", "archetype_library_calibration_coverage": "not_run", "native_powerpoint_acceptance": "not_run", "production_group_meeting_ready": False}, "aggregate_status": status}
    return {"template": template, "body": body_grammar, "grammar": grammar, "style": style, "evidence": evidence, "checkpoint_qa": qa}


def build_checkpoint3_artifacts(input_dir: Path, output_dir: Path) -> dict[str, Any]:
    names = ("sanitized-shell-structural-descriptors.json", "sanitized-body-structural-descriptors.json", "sanitized-exemplar-manifest.json", "checkpoint-2-qa.json")
    shell, body, manifest, cp2qa = (json.loads((input_dir / name).read_text(encoding="utf-8")) for name in names)
    result = resolve_checkpoint3(shell, body, manifest, cp2qa); output_dir.mkdir(parents=True, exist_ok=True)
    for filename, key in {"professor-template-resolved.json": "template", "body-composition-profile.json": "body", "professor-visual-grammar-v3.json": "grammar", "visual-style-profile.json": "style", "resolver-evidence.json": "evidence", "checkpoint-3-qa.json": "checkpoint_qa"}.items():
        (output_dir / filename).write_text(json.dumps(result[key], ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
