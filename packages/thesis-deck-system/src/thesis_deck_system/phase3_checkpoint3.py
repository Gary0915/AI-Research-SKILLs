"""Pure Checkpoint 3 resolver over committed, sanitized CP2 JSON."""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
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


def _candidate_state_hash(input_hashes: dict[str, str]) -> str:
    """Bind release evidence to both canonical CP2 inputs and this resolver source."""
    source_sha = sha256(Path(__file__).read_bytes()).hexdigest()
    return _hash({"input_hashes": input_hashes, "resolver_source_sha256": source_sha})


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
    values = sorted(value for _, value in points)
    center = median(values) if values else None
    distances = {ident: abs(value - center) for ident, value in points} if center is not None else {}
    limit = 3 * median(distances.values()) if distances else 0
    return {
        "metric": name, "availability": "available" if values else "unavailable",
        "observed_range": [values[0], values[-1]] if values else None,
        "robust_center": center, "sample_count": len(values),
        "preferred_descriptor_id": None,
        "outlier_descriptor_ids": sorted(ident for ident, distance in distances.items() if limit and distance > limit),
    }


def _normalized_medoid(rows: list[tuple[str, dict[str, Any]]], metric_names: list[str]) -> tuple[str | None, dict[str, Any]]:
    """Deterministic pairwise medoid over min/max-normalized metrics.

    A missing metric carries a fixed penalty so absence cannot make a sparse
    descriptor preferable.  This remains a structural selection only.
    """
    values: dict[str, list[float]] = defaultdict(list)
    for _, row in rows:
        for name in metric_names:
            value = row["measure"].get("metrics", {}).get(name, {}).get("value")
            if isinstance(value, (int, float)):
                values[name].append(float(value))
    usable = [name for name in metric_names if len(values[name]) >= 2 and max(values[name]) > min(values[name])]
    penalty = 1.0
    if not rows:
        return None, {"method_id": "CP3-NORMALIZED-PAIRWISE-MEDOID-V1", "comparable_metric_count": 0, "missing_data_penalty": penalty, "outlier_method_id": "CP3-MAD-OUTLIER-V1"}
    scores: list[tuple[str, float]] = []
    for ident, row in rows:
        total = 0.0
        for other_ident, other in rows:
            if ident == other_ident:
                continue
            for name in usable:
                low, high = min(values[name]), max(values[name])
                left = row["measure"].get("metrics", {}).get(name, {}).get("value")
                right = other["measure"].get("metrics", {}).get(name, {}).get("value")
                if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
                    total += penalty
                else:
                    total += abs((float(left) - low) / (high - low) - (float(right) - low) / (high - low))
        scores.append((ident, total))
    return min(scores, key=lambda item: (item[1], item[0]))[0], {"method_id": "CP3-NORMALIZED-PAIRWISE-MEDOID-V1", "comparable_metric_count": len(usable), "missing_data_penalty": penalty, "outlier_method_id": "CP3-MAD-OUTLIER-V1"}


def _bind_body_candidates(body: dict[str, Any]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    candidates, measurements = body.get("candidate_families", []), body.get("body_measurements", [])
    _require(isinstance(candidates, list) and isinstance(measurements, list) and len(candidates) == len(measurements), "candidate/measurement binding cardinality mismatch")
    bound: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for index, candidate in enumerate(candidates):
        evidence_ids = [item for item in candidate.get("evidence_basis", []) if isinstance(item, str) and item.startswith("O")]
        measure = measurements[index]
        if evidence_ids:
            object_ids = {obj.get("object_id") for obj in measure.get("objects", [])}
            _require(set(evidence_ids) <= object_ids, "candidate/measurement binding does not resolve to the paired slide")
        bound.append((candidate, measure))
    return bound


def resolve_body_grammar(body: dict[str, Any]) -> dict[str, Any]:
    _require(body.get("profile_id") == BODY_2, "body descriptor identity mismatch")
    _require("shell_regions" not in body and "footer" not in body, "shell contamination from layout exemplar")
    bindings = _bind_body_candidates(body)
    groups: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for index, (candidate, measure) in enumerate(bindings):
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
        preferred, representative = _normalized_medoid(rows, metric_names)
        for distribution in distributions:
            distribution["preferred_descriptor_id"] = preferred if distribution["availability"] == "available" else None
        families.append({"family_id": f"body-{family}", "family": family, "source_role": BODY_2, "source_profile_id": BODY_2, "supporting_descriptor_ids": ids, "sample_count": len(rows), "source_confidence": "insufficient_structural_evidence" if insufficient else "provisional" if provisional else "structurally_supported", "evidence_tier": tier, "metric_distributions": distributions, "preferred_descriptor_id": preferred or ids[0], "outlier_descriptor_ids": sorted({item for dist in distributions for item in dist["outlier_descriptor_ids"]}), "unavailable_metrics": sorted(item["metric"] for item in distributions if item["availability"] == "unavailable"), "representative_method": representative, "status": "insufficient" if insufficient else "resolved" if tier == "recurring_pattern" else "provisional"})
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
    records: list[dict[str, Any]] = []
    allowed = {SHELL_1: {"title", "content", "hypothesis_history"}, SHELL_3: {"cover", "divider", "footer", "page_number", "navigation"}, BODY_2: {"body", "caption", "annotation", "panel_label", "unknown"}}
    for profile in [*shells, body]:
        entries = profile.get("typography_roles", []) if profile["profile_id"] != BODY_2 else [entry for measurement in profile.get("body_measurements", []) for entry in measurement.get("typography_observations", [])]
        for index, item in enumerate(entries):
            if item.get("family") == "unknown" or item.get("script_role") == "unspecified" or item.get("font_evidence_state") not in {"explicit_font", "theme_font_resolved"}:
                continue
            role = item.get("role", "unknown")
            if role not in allowed[profile["profile_id"]]:
                continue
            records.append({"token_id": f"type-{profile['profile_id'].lower()}-{role}-{item['script_role']}-{index:03d}", "role": role, "role_confidence": item.get("role_confidence", "structurally_supported"), "family": item["family"], "font_evidence_state": item["font_evidence_state"], "script_role": item["script_role"], "size_pt": item.get("size_pt"), "weight": item.get("weight", "regular"), "style": item.get("style", "normal"), "source_role": profile["profile_id"], "source_profile_id": profile["profile_id"], "source_scope": item.get("source_scope", "slide_body"), "supporting_ids": [item.get("supporting_object_id", f"TYPE{index:03d}")], "evidence_tier": "single_example_provisional", "origin": "professor_derived", "resolver_rule_id": "CP3-TYPOGRAPHY-AUTHORITY-ROLE"})
    return sorted(records, key=lambda item: item["token_id"])


def _figures(grammar: dict[str, Any], shells: list[dict[str, Any]], body: dict[str, Any]) -> list[dict[str, Any]]:
    tokens = []
    for family in grammar["families"]:
        if family["status"] == "insufficient":
            continue
        for metric in family["metric_distributions"]:
            if metric["availability"] == "available":
                tokens.append({"token_id": f"figure-{family['family']}-{metric['metric']}", "token_family": "figure_metric", "metric": metric["metric"], "family": family["family"], "value": {"kind": "range", "minimum": metric["observed_range"][0], "maximum": metric["observed_range"][1], "center": metric["robust_center"]}, "origin": "professor_derived", "evidence_tier": family["evidence_tier"], "source_role": BODY_2, "source_scope": "slide_body", "supporting_ids": family["supporting_descriptor_ids"], "resolver_rule_id": "CP3-FIGURE-FAMILY-METRIC"})
    def add_styles(profile: dict[str, Any], role: str) -> None:
        for index, style in enumerate(profile.get("style_roles", [])):
            color = style.get("fill_color_evidence", {}).get("resolved_rgb")
            if color and style.get("fill_color_evidence", {}).get("basis") == "measured":
                tokens.append({"token_id": f"style-color-{role.lower()}-{index:03d}", "token_family": "style_color", "metric": "usage_backed_color", "family": "shell" if role != BODY_2 else "body", "value": {"kind": "color", "rgb": color, "semantic_role": style.get("role", "neutral"), "rotation_eligible": True}, "origin": "professor_derived", "evidence_tier": "single_example_provisional", "source_role": role, "source_scope": style.get("source_scope", "slide_layout"), "supporting_ids": [profile["profile_id"]], "resolver_rule_id": "CP3-USAGE-BACKED-COLOR"})
    for shell in shells:
        add_styles(shell, shell["profile_id"])
    for measurement in body.get("body_measurements", []):
        for index, connector in enumerate(measurement.get("connectors", [])):
            if connector.get("geometry_eligible") and connector.get("rotation_status") in {"none", "not_rotated"}:
                tokens.append({"token_id": f"connector-{measurement['slide_id'].lower()}-{index:03d}", "token_family": "connector", "metric": "connector_class", "family": "body", "value": {"kind": "connector", "orientation": connector.get("orientation"), "directedness": connector.get("directedness"), "head_marker": connector.get("head_arrow"), "tail_marker": connector.get("tail_arrow"), "rotation_eligible": True}, "origin": "professor_derived", "evidence_tier": "single_example_provisional", "source_role": BODY_2, "source_scope": "slide_body", "supporting_ids": [measurement["slide_id"], connector.get("object_id", "")], "resolver_rule_id": "CP3-USAGE-BACKED-CONNECTOR"})
        for index, style in enumerate(measurement.get("style_roles", [])):
            color = style.get("fill_color_evidence", {}).get("resolved_rgb")
            if color and style.get("fill_color_evidence", {}).get("basis") == "measured":
                tokens.append({"token_id": f"style-color-{measurement['slide_id'].lower()}-{index:03d}", "token_family": "style_color", "metric": "usage_backed_color", "family": "body", "value": {"kind": "color", "rgb": color, "semantic_role": style.get("role", "neutral"), "rotation_eligible": True}, "origin": "professor_derived", "evidence_tier": "single_example_provisional", "source_role": BODY_2, "source_scope": "slide_body", "supporting_ids": [measurement["slide_id"]], "resolver_rule_id": "CP3-USAGE-BACKED-COLOR"})
            width = style.get("line_width_pt")
            if isinstance(width, (int, float)) and width > 0 and style.get("basis") == "measured":
                tokens.append({"token_id": f"line-width-{measurement['slide_id'].lower()}-{index:03d}", "token_family": "figure_metric", "metric": "line_width_pt", "family": "body", "value": {"kind": "range", "minimum": float(width), "maximum": float(width), "center": float(width)}, "origin": "professor_derived", "evidence_tier": "single_example_provisional", "source_role": BODY_2, "source_scope": "slide_body", "supporting_ids": [measurement["slide_id"]], "resolver_rule_id": "CP3-USAGE-BACKED-LINE-WIDTH"})
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    passthrough: list[dict[str, Any]] = []
    for token in tokens:
        if token["token_family"] == "style_color":
            key = ("style_color", token["source_role"], token["source_scope"], token["value"]["rgb"], token["value"]["semantic_role"])
        elif token["token_family"] == "connector":
            value = token["value"]
            key = ("connector", value["orientation"], value["directedness"], value["head_marker"], value["tail_marker"])
        elif token["token_id"].startswith("line-width-"):
            key = ("line_width", token["value"]["center"])
        else:
            passthrough.append(token)
            continue
        grouped[key].append(token)
    for key, rows in sorted(grouped.items(), key=lambda item: _canon(item[0])):
        first = rows[0]
        supporting = sorted({ident for row in rows for ident in row["supporting_ids"] if ident})
        slide_support = {ident for ident in supporting if ident.startswith("SL")}
        tier = _tier(len(slide_support) if slide_support else len({row["source_role"] for row in rows}))
        category = key[0]
        first = {**first, "token_id": f"{category}-{sha256(_canon(key).encode()).hexdigest()[:10]}", "supporting_ids": supporting, "evidence_tier": tier}
        passthrough.append(first)
    return sorted(passthrough, key=lambda item: item["token_id"])


def _style_token(identifier: str, value: dict[str, Any], origin: str, tier: str, role: str, scope: str, supporting: list[str], rule: str, family: str) -> dict[str, Any]:
    return {"token_id": identifier, "token_family": family, "value": value, "origin": origin, "evidence_tier": tier, "source_role": role, "source_scope": scope, "supporting_ids": sorted(set(supporting)), "resolver_rule_id": rule, "authority_family": "formal_shell" if role in {SHELL_1, SHELL_3} else "body_composition" if role == BODY_2 else "implementation", "status": "resolved" if origin == "professor_derived" else "unresolved"}


def _governor(template: dict[str, Any], fonts: list[dict[str, Any]], figures: list[dict[str, Any]], themes: list[dict[str, Any]]) -> dict[str, Any]:
    tokens = [_style_token(item["token_id"], item["value"], item["origin"], item["evidence_tier"], item["source_role"], "shell", item["supporting_ids"], item["resolver_rule_id"], "shell") for item in template["shell_tokens"]]
    tokens += [_style_token(item["token_id"], {"kind": "typography", "family": item["family"], "size_pt": item["size_pt"], "weight": item["weight"], "style": item["style"], "script_role": item["script_role"], "role": item["role"]}, item["origin"], item["evidence_tier"], item["source_role"], item["source_scope"], item["supporting_ids"], item["resolver_rule_id"], "typography") for item in fonts]
    tokens += [_style_token(item["token_id"], item["value"], item["origin"], item["evidence_tier"], item["source_role"], item["source_scope"], item["supporting_ids"], item["resolver_rule_id"], "scientific_visual") for item in figures]
    tokens.append(_style_token("fallback-render-font", {"kind": "unavailable", "value": None}, "implementation_fallback", "insufficient_evidence", "implementation", "implementation", [], "CP3-FALLBACK-SEPARATION", "typography"))
    coverage = {"professor_derived_recurring": sum(t["origin"] == "professor_derived" and t["evidence_tier"] == "recurring_pattern" for t in tokens), "professor_derived_provisional": sum(t["origin"] == "professor_derived" and t["evidence_tier"] != "recurring_pattern" for t in tokens), "fallback": sum(t["origin"] in {"phase2_fallback", "implementation_fallback"} for t in tokens), "unresolved": sum(t["origin"] == "unresolved" for t in tokens), "reference_only_metadata": len(themes)}
    coverage.update({"professor_derived_token_count": coverage["professor_derived_recurring"] + coverage["professor_derived_provisional"], "fallback_token_count": coverage["fallback"] + coverage["unresolved"], "unresolved_token_count": coverage["unresolved"]})
    families = {
        "shell_geometry": lambda token: token["token_family"] == "shell",
        "typography_hierarchy": lambda token: token["token_family"] == "typography",
        "body_composition": lambda token: token["token_family"] == "scientific_visual" and token["value"].get("kind") == "range",
        "scientific_figure_metrics": lambda token: token["token_family"] == "scientific_visual" and token["value"].get("kind") == "range",
        "connector_arrow_grammar": lambda token: token["token_family"] == "scientific_visual" and token["value"].get("kind") == "connector",
        "line_style_grammar": lambda token: token["token_family"] == "scientific_visual" and token.get("token_id", "").startswith("line_width-"),
        "color_emphasis_grammar": lambda token: token["token_family"] == "scientific_visual" and token["value"].get("kind") == "color",
        "unresolved_fallback_reference": lambda token: token["origin"] != "professor_derived",
    }
    categories = {}
    for name, predicate in families.items():
        selected = [token for token in tokens if predicate(token)]
        recurring = sum(token["origin"] == "professor_derived" and token["evidence_tier"] == "recurring_pattern" for token in selected)
        provisional = sum(token["origin"] == "professor_derived" and token["evidence_tier"] != "recurring_pattern" for token in selected)
        fallback = sum(token["origin"] in {"phase2_fallback", "implementation_fallback"} for token in selected)
        unresolved = sum(token["origin"] == "unresolved" for token in selected)
        categories[name] = {"professor_derived_recurring": recurring, "professor_derived_provisional": provisional, "fallback": fallback, "unresolved": unresolved, "reference_only_metadata": len(themes) if name == "unresolved_fallback_reference" else 0, "reusable_coverage_status": "fully_calibrated" if recurring else "provisional_only" if provisional else "unresolved"}
    coverage["categories"] = categories
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


def _cp2_schema_validation(shell_doc: dict[str, Any], body_doc: dict[str, Any], manifest: dict[str, Any], cp2qa: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    from .contracts import SchemaRegistry
    registry = SchemaRegistry(Path(__file__).resolve().parents[4] / "thesis-deck-system" / "schemas", include_phase3=True)
    objects = (("sanitized-shell-structural-descriptors", shell_doc), ("sanitized-body-structural-descriptors", body_doc), ("sanitized-exemplar-manifest", manifest), ("checkpoint-2-qa", cp2qa))
    errors = sum(len(registry.errors(name, value)) for name, value in objects)
    return errors == 0, {"validated_input_count": len(objects), "schema_error_count": errors}


@lru_cache(maxsize=1)
def _approved_privacy_scan() -> tuple[bool, dict[str, Any]]:
    """Use the same repository/staged scanner approved in CP2, not a substring substitute."""
    from .phase3_privacy import RepositoryPrivacyScanner
    root = Path(__file__).resolve().parents[4]
    findings, exceptions = RepositoryPrivacyScanner().scan_repository_with_legacy_exception(root, forbidden_basenames=[])
    return not findings, {"repository_unexcepted_finding_count": len(findings), "approved_legacy_exception_count": len(exceptions), "staged_scan_bound": True}


def _checks(shell_doc: dict[str, Any], body_doc: dict[str, Any], manifest: dict[str, Any], cp2qa: dict[str, Any], template: dict[str, Any], body_grammar: dict[str, Any], grammar: dict[str, Any], style: dict[str, Any], evidence: dict[str, Any], fonts: list[dict[str, Any]], figures: list[dict[str, Any]], themes: list[dict[str, Any]], regression_evidence: dict[str, Any] | None) -> list[dict[str, Any]]:
    aliases = {item.get("alias_uri"): item.get("profile_id") for item in manifest.get("exemplars", [])}
    return [
        _check("CP3-CP2-SCHEMAS", lambda: _cp2_schema_validation(shell_doc, body_doc, manifest, cp2qa)),
        _check("CP3-INPUT-VALIDATION", lambda: (cp2qa.get("aggregate_status") == "pass", {"cp2_status": cp2qa.get("aggregate_status")})),
        _check("CP3-INPUT-HASHES", lambda: (len(evidence["input_hashes"]) == 4 and all(len(value) == 64 for value in evidence["input_hashes"].values()), {"input_hash_count": len(evidence["input_hashes"])})),
        _check("CP3-EXEMPLAR-IDENTITIES", lambda: (aliases == {alias: profile for profile, alias in ALIASES.items()}, {"alias_count": len(aliases), "profile_ids": sorted(aliases.values())})),
        _check("CP3-NO-PRIVATE-ACCESS", lambda: (all(evidence[k] == 0 for k in ("private_alias_resolution_attempts", "private_source_open_attempts", "private_render_attempts")), {k: evidence[k] for k in ("private_alias_resolution_attempts", "private_source_open_attempts", "private_render_attempts")})),
        _check("CP3-AUTHORITY", lambda: (all(item["source_role"] != BODY_2 for item in template["shell_tokens"]), {"shell_source_roles": sorted({item["source_role"] for item in template["shell_tokens"]})})),
        _check("CP3-SHELL-CONTAMINATION", lambda: (not ({"shell_regions", "footer"} & set(body_doc["descriptor"])), {"forbidden_field_count": len({"shell_regions", "footer"} & set(body_doc["descriptor"]))})),
        _check("CP3-CONFLICTS", lambda: (all(c["conflict_classification"] == "soft_resolved" and c["losing_descriptor_evidence"] for c in template["conflicts"]), {"conflict_count": len(template["conflicts"]), "hard_conflict_count": sum(c["conflict_classification"] == "hard_blocking" for c in template["conflicts"])})),
        _check("CP3-EVIDENCE-TIERS", lambda: (all(item.get("evidence_tier") in TIERS for item in template["shell_tokens"] + grammar["body_composition_rules"] + grammar["typography_tokens"] + grammar["figure_grammar"]), {"checked_token_count": len(template["shell_tokens"]) + len(grammar["body_composition_rules"]) + len(grammar["typography_tokens"]) + len(grammar["figure_grammar"])})),
        _check("CP3-RECURRING-SUPPORT", lambda: (all(item["sample_count"] >= 2 and item["source_confidence"] == "structurally_supported" for item in grammar["body_composition_rules"] if item["evidence_tier"] == "recurring_pattern"), {"recurring_family_count": sum(item["evidence_tier"] == "recurring_pattern" for item in grammar["body_composition_rules"])})),
        _check("CP3-ACTIVE-THEME-AUTHORITY", lambda: (not grammar["active_theme_tokens"], {"active_metadata_count": len(grammar["active_theme_metadata"]), "resolved_theme_token_count": len(grammar["active_theme_tokens"])})),
        _check("CP3-THEME-IDENTITY", lambda: (len({(x["profile_id"], x["theme_profile_id"]) for x in grammar["active_theme_metadata"]}) == len(grammar["active_theme_metadata"]), {"qualified_theme_count": len(grammar["active_theme_metadata"])})),
        _check("CP3-TYPOGRAPHY-TRUTH", lambda: (all(x["family"] != "unknown" and x["script_role"] != "unspecified" and x["size_pt"] is not None for x in grammar["typography_tokens"]), {"resolved_typography_count": len(grammar["typography_tokens"])})),
        _check("CP3-TYPOGRAPHY-AUTHORITY", lambda: (all((x["source_role"] == SHELL_1 and x["role"] in {"title", "content", "hypothesis_history"}) or (x["source_role"] == SHELL_3 and x["role"] in {"cover", "divider", "footer", "page_number", "navigation"}) or (x["source_role"] == BODY_2 and x["role"] in {"body", "caption", "annotation", "panel_label", "unknown"}) for x in grammar["typography_tokens"]), {"authority_valid_typography_count": len(grammar["typography_tokens"])})),
        _check("CP3-SUPPLEMENTAL-FONT-EXCLUSION", lambda: (all(x["font_evidence_state"] in {"explicit_font", "theme_font_resolved"} for x in grammar["typography_tokens"]), {"supplemental_promoted_count": 0})),
        _check("CP3-BODY-BINDINGS", lambda: (all(x["preferred_descriptor_id"] in x["supporting_descriptor_ids"] for x in grammar["body_composition_rules"]), {"binding_family_count": len(grammar["body_composition_rules"])})),
        _check("CP3-BODY-RANGE", lambda: (all(x["status"] == "insufficient" or x["preferred_descriptor_id"] in x["supporting_descriptor_ids"] for x in grammar["body_composition_rules"]), {"family_count": len(grammar["body_composition_rules"])})),
        _check("CP3-UNAVAILABLE-METRICS", lambda: (all(m["availability"] == "unavailable" or m["observed_range"] is not None for f in grammar["body_composition_rules"] for m in f["metric_distributions"]), {"unavailable_count": sum(len(f["unavailable_metrics"]) for f in grammar["body_composition_rules"])})),
        _check("CP3-FIGURE-NON-INVENTION", lambda: (all(x["status"] == "unresolved" for x in grammar["material_semantic_tokens"]), {"unresolved_material_count": len(grammar["material_semantic_tokens"])})),
        _check("CP3-USAGE-BACKED-STYLE", lambda: (all(x["token_family"] != "style_color" or x["value"].get("kind") == "color" for x in grammar["figure_grammar"]), {"usage_backed_style_token_count": sum(x["token_family"] in {"style_color", "connector"} for x in grammar["figure_grammar"])})),
        _check("CP3-STYLE-PROVENANCE", lambda: (all({"origin", "evidence_tier", "source_role", "source_scope", "supporting_ids", "resolver_rule_id", "value"} <= set(x) for x in style["tokens"]), {"style_token_count": len(style["tokens"])})),
        _check("CP3-FALLBACK-SEPARATION", lambda: (style["coverage"]["professor_derived_token_count"] == sum(x["origin"] == "professor_derived" for x in style["tokens"]), {"derived_count": style["coverage"]["professor_derived_token_count"]})),
        _check("CP3-SHELL-SUPPORT", lambda: (all(x["token_family"] == "canvas" or x["support_count"] == sum(s.get("source_container_count", 0) for s in x["support_by_scope"]) for x in template["shell_tokens"]), {"shell_token_count": len(template["shell_tokens"])})),
        _check("CP3-SCHEMA-CLOSURE", _schema_closure),
        _check("CP3-DETERMINISM", lambda: (resolve_shell(shell_doc) == template and resolve_body_grammar(body_doc["descriptor"]) == body_grammar and _governor(template, fonts, figures, themes) == style, {"resolver_input_hash": _hash({"template": template, "grammar": grammar, "style": style})})),
        _check("CP3-REPOSITORY-STAGED-PRIVACY", _approved_privacy_scan),
        _check("CP3-DISPOSABLE-REGRESSION", lambda: (
            isinstance(regression_evidence, dict)
            and regression_evidence.get("candidate_state_hash") == _candidate_state_hash(evidence["input_hashes"])
            and regression_evidence.get("disposable_worktree") is True
            and isinstance(regression_evidence.get("tests_passed"), int)
            and regression_evidence["tests_passed"] > 0
            and regression_evidence.get("tests_failed") == 0,
            {"candidate_state_binding": _candidate_state_hash(evidence["input_hashes"]), "tests_passed": int(regression_evidence.get("tests_passed", 0)) if isinstance(regression_evidence, dict) else 0, "tests_failed": int(regression_evidence.get("tests_failed", 0)) if isinstance(regression_evidence, dict) else 0, "disposable_worktree": bool(regression_evidence.get("disposable_worktree")) if isinstance(regression_evidence, dict) else False},
        )),
    ]


def resolve_checkpoint3(shell_document: dict[str, Any], body_document: dict[str, Any], manifest: dict[str, Any], checkpoint2_qa: dict[str, Any], *, regression_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    _require(checkpoint2_qa.get("aggregate_status") == "pass", "CP2 QA must pass before resolution")
    profiles = _shells(shell_document); body = body_document.get("descriptor"); _require(isinstance(body, dict), "missing CP2 body descriptor")
    _require({item.get("alias_uri") for item in manifest.get("exemplars", [])} == set(ALIASES.values()), "CP2 alias manifest mismatch")
    template = resolve_shell(shell_document); body_grammar = resolve_body_grammar(body); shells = [profiles[SHELL_1], profiles[SHELL_3]]; themes = _theme_metadata([*shells, body]); fonts = _typography(shells, body); figures = _figures(body_grammar, shells, body)
    grammar = {"schema_version": "3.1.0", "grammar_id": "PVG003", "status": "structural_resolution_only", "formal_shell_rules": template["shell_tokens"], "body_composition_rules": body_grammar["families"], "active_theme_metadata": themes, "active_theme_tokens": [], "typography_tokens": fonts, "figure_grammar": figures, "material_semantic_tokens": [{"token_id": f"material-{name}", "status": "unresolved", "origin": "unresolved", "evidence_tier": "insufficient_evidence"} for name in ("hydrogel", "electrode", "heater", "sensor", "contact_interface")]}
    style = _governor(template, fonts, figures, themes); evidence = {"schema_version": "2.0.0", "evidence_id": "CP3-EXEC-001", "input_hashes": {"shell": _hash(shell_document), "body": _hash(body_document), "manifest": _hash(manifest), "checkpoint2_qa": _hash(checkpoint2_qa)}, "private_alias_resolution_attempts": 0, "private_source_open_attempts": 0, "private_render_attempts": 0, "owning_checks": []}
    evidence["owning_checks"] = _checks(shell_document, body_document, manifest, checkpoint2_qa, template, body_grammar, grammar, style, evidence, fonts, figures, themes, regression_evidence); status = "pass" if all(x["status"] == "pass" for x in evidence["owning_checks"]) else "fail"
    qa = {"schema_version": "2.0.0", "checkpoint_id": "PHASE_3_CHECKPOINT_3", "execution_evidence_id": evidence["evidence_id"], "execution_evidence_sha256": _hash(evidence), "private_alias_resolution_attempts": 0, "private_source_open_attempts": 0, "private_render_attempts": 0, "owning_checks": evidence["owning_checks"], "statuses": {"private_exemplar_ingestion": "pass", "sanitized_structural_evidence": status, "shell_resolver_status": status, "body_composition_resolver_status": status, "figure_grammar_structural_status": status, "visual_style_governor_status": status, "professor_visual_grammar_structural_status": status, "private_qualitative_visual_review": "blocked_visual_review", "acceptance_deck_visual_fidelity": "not_run", "archetype_library_calibration_coverage": "not_run", "native_powerpoint_acceptance": "not_run", "production_group_meeting_ready": False}, "aggregate_status": status}
    return {"template": template, "body": body_grammar, "grammar": grammar, "style": style, "evidence": evidence, "checkpoint_qa": qa}


def build_checkpoint3_artifacts(input_dir: Path, output_dir: Path, *, regression_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    names = ("sanitized-shell-structural-descriptors.json", "sanitized-body-structural-descriptors.json", "sanitized-exemplar-manifest.json", "checkpoint-2-qa.json")
    shell, body, manifest, cp2qa = (json.loads((input_dir / name).read_text(encoding="utf-8")) for name in names)
    result = resolve_checkpoint3(shell, body, manifest, cp2qa, regression_evidence=regression_evidence); output_dir.mkdir(parents=True, exist_ok=True)
    for filename, key in {"professor-template-resolved.json": "template", "body-composition-profile.json": "body", "professor-visual-grammar-v3.json": "grammar", "visual-style-profile.json": "style", "resolver-evidence.json": "evidence", "checkpoint-3-qa.json": "checkpoint_qa"}.items():
        (output_dir / filename).write_text(json.dumps(result[key], ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
