"""Hypothesis-layer story compilation and hard professor-rule validation."""

from __future__ import annotations

from .contracts import Finding


def _spec(layer: dict, role: str, ordinal: int, source_cursor: int, *, object_ref: str | None = None) -> dict:
    layer_id = layer["hypothesis_layer_id"]
    return {
        "slide_id": f"S-{layer_id}-{role.upper().replace('_', '-')}-{ordinal:02d}",
        "hypothesis_layer_ref": layer_id,
        "hypothesis_layer_revision": layer["revision"],
        "semantic_role": role,
        "combined_roles": [role],
        "source_cursor": source_cursor,
        "object_ref": object_ref,
        "fishbone_snapshot_ref": layer.get("fishbone_snapshot_ref") if role == "fishbone_locator" else None,
        "fishbone_focus_refs": layer.get("fishbone_focus_refs", []) if role == "fishbone_locator" else [],
    }


def compile_hypothesis_layer(layer: dict, *, source_cursor: int) -> list[dict]:
    sequence: list[tuple[str, str | None]] = [
        ("hypothesis_title", layer.get("hypothesis_claim_ref")),
        ("problem_definition", layer.get("problem_ref")),
        ("fishbone_locator", None),
        ("observation_problem", layer.get("research_block_refs", [None])[0]),
        ("literature_mechanism", layer.get("research_block_refs", [None])[0]),
    ]
    sequence.extend(("experiment_design", ref) for ref in layer.get("experiment_order", layer.get("experiment_refs", [])))
    result_refs = layer.get("result_order", layer.get("result_refs", []))
    sequence.extend((("result_comparison" if len(result_refs) > 1 else "result_single"), ref) for ref in result_refs)
    sequence.extend([
        ("layer_integrated_discussion", layer.get("layer_discussion_ref")),
        ("layer_summary_decision", layer.get("layer_summary_ref")),
        ("hypothesis_transition", layer.get("transition_ref")),
    ])
    specs = [_spec(layer, role, index, source_cursor, object_ref=ref) for index, (role, ref) in enumerate(sequence, 1)]
    findings = validate_story_order(layer, specs)
    if findings:
        raise ValueError("invalid hypothesis story: " + ",".join(finding.rule_id for finding in findings))
    return specs


def validate_story_order(layer: dict, specs: list[dict]) -> list[Finding]:
    findings: list[Finding] = []
    roles = [spec.get("semantic_role") for spec in specs]
    for spec in specs:
        combined = set(spec.get("combined_roles", []))
        if {"hypothesis_title", "problem_definition"} <= combined:
            findings.append(Finding("P-HARD-01", "professor_style_logic", "Hypothesis and Problem were merged", spec.get("slide_id", "")))
    for required in ("hypothesis_title", "problem_definition", "fishbone_locator", "layer_integrated_discussion", "layer_summary_decision"):
        if required not in roles:
            findings.append(Finding("P-HARD-02" if required == "fishbone_locator" else "P2-STORY-MISSING-ROLE", "professor_style_logic", f"Missing required role {required}"))
    if "layer_integrated_discussion" in roles:
        discussion_index = roles.index("layer_integrated_discussion")
        result_indices = [index for index, role in enumerate(roles) if role in {"result_single", "result_comparison"}]
        if len(result_indices) != len(layer.get("result_refs", [])) or any(index > discussion_index for index in result_indices):
            findings.append(Finding("P-HARD-05", "scientific_reasoning", "Integrated Discussion appears before the complete result set"))
    return findings
