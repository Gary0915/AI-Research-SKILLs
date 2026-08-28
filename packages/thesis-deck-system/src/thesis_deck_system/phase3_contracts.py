"""Cross-contract guards for Phase 3 visual control-plane inputs."""

from __future__ import annotations


_EMPIRICAL_ORIGINS = {"experimental_photo", "microscopy", "instrument_output", "measurement", "source_derived_scientific_visual"}


def validate_observation_visual_binding(binding: dict) -> list[str]:
    findings: list[str] = []
    if binding.get("empirical_evidence_required"):
        evidence_ref = binding.get("observation_evidence_ref")
        catalog = binding.get("evidence_catalog", {})
        evidence = catalog.get(evidence_ref) if evidence_ref else None
        if not evidence_ref or evidence_ref not in binding.get("evidence_refs", []) or not evidence:
            findings.append("P3-OBSERVATION-EMPIRICAL-EVIDENCE-MISSING")
        elif evidence.get("origin") not in _EMPIRICAL_ORIGINS:
            findings.append("P3-OBSERVATION-GENERATED-AS-EVIDENCE")
    for visual in binding.get("auxiliary_visuals", []):
        if visual.get("figure_type") == "concept_illustration" and visual.get("evidence_status") != "non_evidence":
            findings.append("P3-OBSERVATION-AUXILIARY-CONCEPT-STATUS")
    return findings


def validate_fabrication_process(process: dict) -> list[str]:
    findings: list[str] = []
    if process.get("process_kind") != "fabrication_process":
        findings.append("P3-FABRICATION-KIND")
        return findings
    if not process.get("provenance_refs"):
        findings.append("P3-FABRICATION-PROVENANCE-MISSING")
    steps = process.get("steps", [])
    ordinals = [step.get("ordinal") for step in steps]
    if not steps or ordinals != list(range(1, len(steps) + 1)):
        findings.append("P3-FABRICATION-ORDER")
    for step in steps:
        if not step.get("material_refs") or not step.get("state_before") or not step.get("state_after"):
            findings.append("P3-FABRICATION-STATE-OR-MATERIAL-MISSING")
        conditions = step.get("conditions")
        if not isinstance(conditions, dict) or set(conditions) != {"temperature_c", "duration_min"}:
            findings.append("P3-FABRICATION-CONDITION-CONTRACT")
    return findings


def validate_skill_routing(routing: dict) -> list[str]:
    findings: list[str] = []
    skills = {item.get("skill_id"): item for item in routing.get("skills", [])}
    fabrication = skills.get("fabrication-process-director")
    if not fabrication or fabrication.get("output_contract") != "fabrication-process":
        findings.append("P3-SKILL-ROUTING-FABRICATION")
    for route in routing.get("routes", []):
        if route.get("request_kind") == "fabrication_process" and route.get("skill_id") != "fabrication-process-director":
            findings.append("P3-SKILL-ROUTING-FABRICATION")
    return findings
