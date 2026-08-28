"""Cross-contract guards for Phase 3 visual control-plane inputs."""

from __future__ import annotations

from typing import Any


_EMPIRICAL_EVIDENCE_KINDS = {
    "experimental_measurement", "synthetic_measurement", "observation_photo", "synthetic_observation",
    "microscopy_image", "simulation_output",
}
_EMPIRICAL_OUTPUT_TYPES = {"scientific_plot", "real_photo"}
_PRODUCTION_EMPIRICAL_EVIDENCE_KINDS = {
    "experimental_measurement", "observation_photo", "microscopy_image",
}


def canonical_observation_catalogs(registry: Any, evidence_cards: list[dict], output_manifests: list[dict]) -> dict:
    """Build the Observation catalog only from schema-valid canonical identities."""
    evidence_by_id: dict[str, dict] = {}
    for card in evidence_cards:
        if registry.errors("evidence-card", card):
            raise ValueError("canonical Evidence card is invalid")
        evidence_by_id[card["evidence_id"]] = card
    outputs: dict[str, dict] = {}
    for output in output_manifests:
        if registry.errors("figure-output-manifest", output):
            raise ValueError("canonical FigureOutput manifest is invalid")
        outputs[output["figure_output_id"]] = output
    return {"evidence": evidence_by_id, "outputs": outputs}


def validate_observation_visual_binding(binding: dict, *, catalog: dict | None = None, evidence_policy: str = "fixture") -> list[str]:
    """Require canonical empirical Evidence + FigureOutput provenance for Observation."""
    findings: list[str] = []
    if binding.get("empirical_evidence_required"):
        evidence_ref = binding.get("observation_evidence_ref")
        output_ref = binding.get("observation_output_ref")
        evidence = catalog.get("evidence", {}).get(evidence_ref) if catalog and evidence_ref else None
        output = catalog.get("outputs", {}).get(output_ref) if catalog and output_ref else None
        if not evidence_ref or evidence_ref not in binding.get("evidence_refs", []) or not evidence or not output:
            findings.append("P3-OBSERVATION-EMPIRICAL-EVIDENCE-MISSING")
        elif evidence.get("kind") not in _EMPIRICAL_EVIDENCE_KINDS or output.get("figure_type") not in _EMPIRICAL_OUTPUT_TYPES:
            findings.append("P3-OBSERVATION-GENERATED-AS-EVIDENCE")
        elif evidence_policy == "production" and (evidence.get("kind") not in _PRODUCTION_EMPIRICAL_EVIDENCE_KINDS or evidence.get("verification", {}).get("status") != "verified"):
            findings.append("P3-OBSERVATION-PRODUCTION-EMPIRICAL-POLICY")
        elif evidence_policy not in {"fixture", "production"}:
            findings.append("P3-OBSERVATION-EVIDENCE-POLICY")
        elif evidence_ref not in output.get("provenance_refs", []) or output.get("evidence_status") == "non_evidence":
            findings.append("P3-OBSERVATION-PROVENANCE-MISMATCH")
        elif output.get("figure_type") == "scientific_plot" and evidence_ref not in output.get("primary_artifact", {}).get("data_provenance_refs", []):
            findings.append("P3-OBSERVATION-PROVENANCE-MISMATCH")
        elif output.get("figure_type") == "real_photo" and evidence_ref != output.get("primary_artifact", {}).get("evidence_card_ref"):
            findings.append("P3-OBSERVATION-PROVENANCE-MISMATCH")
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
