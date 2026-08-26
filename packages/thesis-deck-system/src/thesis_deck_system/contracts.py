"""JSON Schema and cross-object semantic validation."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


REQUIRED_SCHEMA_NAMES = (
    "research-block",
    "scientific-stage",
    "claim",
    "evidence-card",
    "asset-manifest",
    "next-step",
    "slide-spec",
    "deck-manifest",
    "qa-report",
    "decision-event",
    "professor-profile",
    "template-profile",
)

SCHEMA_BY_COLLECTION = {
    "research_blocks": "research-block",
    "stages": "scientific-stage",
    "claims": "claim",
    "evidence_cards": "evidence-card",
    "assets": "asset-manifest",
    "actions": "next-step",
    "decisions": "decision-event",
    "slide_specs": "slide-spec",
    "deck_manifests": "deck-manifest",
    "qa_reports": "qa-report",
    "professor_profiles": "professor-profile",
    "template_profiles": "template-profile",
}


@dataclass(frozen=True)
class Finding:
    rule_id: str
    stage: str
    message: str
    path: str = ""
    severity: str = "critical"


class SchemaRegistry:
    def __init__(self, schema_dir: Path | str):
        self.schema_dir = Path(schema_dir)
        self._schemas = {
            name: json.loads((self.schema_dir / f"{name}.schema.json").read_text(encoding="utf-8"))
            for name in REQUIRED_SCHEMA_NAMES
        }
        for schema in self._schemas.values():
            Draft202012Validator.check_schema(schema)

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._schemas)

    def errors(self, name: str, value: Any) -> list[str]:
        validator = Draft202012Validator(self._schemas[name], format_checker=FormatChecker())
        return [
            f"{'/'.join(map(str, error.absolute_path)) or '$'}: {error.message}"
            for error in sorted(validator.iter_errors(value), key=lambda item: list(item.absolute_path))
        ]

    def validate(self, name: str, value: Any) -> None:
        errors = self.errors(name, value)
        if errors:
            raise ValueError(f"{name} validation failed: {'; '.join(errors)}")

    def validate_bundle(self, bundle: dict[str, Any]) -> list[Finding]:
        findings: list[Finding] = []
        for collection, schema_name in SCHEMA_BY_COLLECTION.items():
            for index, value in enumerate(bundle.get(collection, [])):
                for message in self.errors(schema_name, value):
                    findings.append(Finding("SCHEMA-INVALID", "schema_ledger_integrity", message, f"{collection}/{index}"))
        findings.extend(semantic_findings(bundle))
        return findings


def _refs(items: Iterable[dict[str, Any]], field: str) -> set[str]:
    refs: set[str] = set()
    for item in items:
        refs.update(item.get(field, []))
    return refs


def semantic_findings(bundle: dict[str, Any]) -> list[Finding]:
    """Return stable, gate-addressed findings for cross-object rules."""
    findings: list[Finding] = []
    blocks = bundle.get("research_blocks", [])
    claims = bundle.get("claims", [])
    stages = bundle.get("stages", [])
    evidence = bundle.get("evidence_cards", [])
    assets = bundle.get("assets", [])
    actions = bundle.get("actions", [])
    claim_ids = {claim.get("claim_id") for claim in claims}
    action_ids = {action.get("action_item_id") for action in actions}

    referenced_claims = _refs(blocks, "claim_refs") | _refs(blocks, "hypothesis_claim_refs") | _refs(blocks, "mechanism_claim_refs") | _refs(blocks, "prediction_claim_refs")
    referenced_claims |= _refs(stages, "claim_refs") | _refs(stages, "hypothesis_claim_refs") | _refs(stages, "prediction_claim_refs")
    referenced_claims |= _refs(evidence, "claim_support_refs") | _refs(evidence, "claim_contradict_refs")
    referenced_claims |= _refs(actions, "linked_claim_refs")
    for ref in sorted(ref for ref in referenced_claims if ref and ref not in claim_ids):
        findings.append(Finding("REF-DANGLING-CLAIM", "schema_ledger_integrity", f"Claim reference {ref} does not resolve", ref))

    for block in blocks:
        block_id = block.get("block_id", "unknown")
        if not block.get("research_question") or not block.get("problem_statement"):
            findings.append(Finding("SCI-BLOCK-MISSING-RESEARCH-QUESTION", "scientific_reasoning", f"{block_id} lacks a research question/problem statement", block_id))
        if block.get("research_status") == "archived_from_main_story":
            findings.append(Finding("LEDGER-STATUS-VISIBILITY-CONFLATED", "schema_ledger_integrity", f"{block_id} uses a visibility value as research status", block_id))
        next_ref = block.get("stage_refs", {}).get("next_step")
        if next_ref and next_ref not in action_ids:
            findings.append(Finding("REF-DANGLING-ACTION", "schema_ledger_integrity", f"Next Step {next_ref} does not resolve", block_id))

    for claim in claims:
        if claim.get("claim_type") in {"hypothesis", "mechanism"}:
            if not claim.get("falsifiable_predictions") or not claim.get("discriminating_evidence_requirements"):
                findings.append(Finding("SCI-HYPOTHESIS-NOT-FALSIFIABLE", "scientific_reasoning", f"{claim.get('claim_id')} lacks falsification or discriminating evidence", claim.get("claim_id", "")))

    literature_fields = {
        "consensus", "disagreements_or_alternatives", "known_mechanisms", "research_gap",
        "relevance_to_observation", "implication_for_hypothesis_or_strategy",
    }
    experiment_fields = {
        "independent_variables", "controlled_variables", "controls_baselines", "sample_plan",
        "measured_outputs", "instrumentation_method_refs", "predicted_outcomes", "decision_rules",
    }
    for stage in stages:
        data = stage.get("data", {})
        if stage.get("stage_type") == "literature" and any(not data.get(field) for field in literature_fields):
            findings.append(Finding("SCI-LITERATURE-NOT-SYNTHESIZED", "scientific_reasoning", "Literature must contain structured synthesis", stage.get("stage_id", "")))
        if stage.get("stage_type") == "experiment" and any(not data.get(field) for field in experiment_fields):
            findings.append(Finding("SCI-EXPERIMENT-INCOMPLETE", "scientific_reasoning", "Experiment metadata is incomplete", stage.get("stage_id", "")))

    required_action_fields = {"owner", "target_window", "source_decision_ref", "success_failure_criteria", "dependency_refs", "parallelizable", "workstream", "status"}
    for action in actions:
        if any(field not in action or action.get(field) in (None, "") for field in required_action_fields):
            findings.append(Finding("SCI-NEXT-STEP-INCOMPLETE", "scientific_reasoning", "Next Step lacks owner/timing/decision/progress data", action.get("action_item_id", "")))

    for card in evidence:
        if card.get("kind") == "generated_context" and (card.get("claim_support_refs") or card.get("claim_contradict_refs")):
            findings.append(Finding("PROV-GENERATED-AS-EVIDENCE", "citation_evidence_provenance", "Generated context cannot support or contradict Claims", card.get("evidence_id", "")))
    for asset in assets:
        if asset.get("asset_type") == "generated_context" and asset.get("evidence_role") != "decorative_only":
            findings.append(Finding("PROV-GENERATED-AS-EVIDENCE", "citation_evidence_provenance", "Generated context must be decorative only", asset.get("asset_id", "")))

    projection = bundle.get("meeting_projection")
    if projection:
        prior = set(projection.get("prior_commitment_ids", []))
        included = set(projection.get("included_action_ids", []))
        if prior - included:
            findings.append(Finding("PROF-MEETING-LOST-COMMITMENT", "professor_style_logic", f"Meeting projection lost commitments: {sorted(prior - included)}"))

    reachable = set(bundle.get("history_reachable_block_ids", []))
    for block in blocks:
        if block.get("research_status") == "failed_but_informative" and block.get("block_id") not in reachable:
            findings.append(Finding("LEDGER-FAILED-HISTORY-UNREACHABLE", "schema_ledger_integrity", f"Failed block {block.get('block_id')} is unreachable"))

    for report in bundle.get("qa_reports", []):
        open_critical = any(finding.get("severity") == "critical" and finding.get("status") == "open" for finding in report.get("findings", []))
        release_stage = next((item for item in report.get("pipeline", []) if item.get("stage") == "release"), {})
        if open_critical and release_stage.get("status") == "pass":
            findings.append(Finding("RELEASE-CRITICAL-FINDING-OPEN", "release", "Release cannot pass with an open critical finding"))
    return findings
