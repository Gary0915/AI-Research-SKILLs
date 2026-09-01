"""JSON Schema and cross-object semantic validation."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
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

PHASE2_SCHEMA_NAMES = (
    "hypothesis-layer",
    "problem",
    "fishbone-map",
    "fishbone-revision",
    "layer-discussion",
    "layer-summary",
    "hypothesis-transition",
    "layout-archetype",
    "layout-plan",
)

PHASE3_SCHEMA_NAMES = (
    "image-review-provider",
    "concept-image-provider",
    "figure-routing-request",
    "figure-production-plan",
    "scientific-figure-spec",
    "figure-output-manifest",
    "figure-critic-report",
    "visual-style-profile",
    "observation-visual-binding",
    "fabrication-process",
    "skill-routing",
    "checkpoint-qa",
    "sanitized-exemplar-manifest",
    "sanitized-shell-structural-descriptors",
    "sanitized-body-structural-descriptors",
    "checkpoint-2-qa",
    "professor-template-resolved",
    "body-composition-profile",
    "professor-visual-grammar-v3",
    "resolver-evidence",
    "checkpoint-3-qa",
    "archetype-figure-routing",
    "checkpoint-4-execution-evidence",
    "checkpoint-4-qa",
)

CP5A_SCHEMA_NAMES = (
    "scientific-svg-profile",
    "semantic-svg-role-registry",
    "static-svg-qa-report",
    "scientific-svg-identity",
    "checkpoint-5a-execution-evidence",
    "checkpoint-5a-qa",
    "scientific-svg-synthetic-corpus",
    "checkpoint-5a-report-facts",
)

CP5BCD_SCHEMA_NAMES = (
    "svg-native-capability-registry", "svg-native-test-vectors",
    "scientific-svg-figure-output-manifest", "static-figure-critic-report", "approved-figure",
    "checkpoint-5b-execution-evidence", "checkpoint-5b-qa",
    "checkpoint-5c-execution-evidence", "checkpoint-5c-qa",
    "structured-director-input", "checkpoint-5d-execution-evidence", "checkpoint-5d-qa",
    "vsp003-style-category-resolution-map",
    "checkpoint-5e-execution-evidence", "checkpoint-5e-qa", "checkpoint-5f-execution-evidence", "checkpoint-5f-qa", "checkpoint-5g-execution-evidence", "checkpoint-5g-qa",
    "archetype-calibration", "figure-family-calibration", "fishbone-style-profile", "reconstruction-benchmarks",
    "checkpoint-c1-g1-cross-gate-acceptance",
)

CP5HI_SCHEMA_NAMES = (
    "cp5-hi-backend-uniqueness-audit",
    "cp5-hi-execution-evidence",
    "native-figure-compilation-plan",
    "cp5-hi-release-gates",
    "cp5-hi-package-manifest",
    "generated-pptx-attestation",
    "native-materialization-parity",
    "final-closure-validation-run",
    "final-closure-reliability-qa",
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


_SCHEMA_CACHE: dict[tuple[str, str], tuple[dict[str, Any], Draft202012Validator]] = {}


class SchemaRegistry:
    def __init__(self, schema_dir: Path | str, *, include_phase2: bool = False, include_phase3: bool = False, include_cp5a: bool = False, include_cp5bcd: bool = False, include_cp5hi: bool = False, schema_names: tuple[str, ...] | None = None):
        self.schema_dir = Path(schema_dir)
        resolved_names = schema_names or (
            REQUIRED_SCHEMA_NAMES
            + (PHASE2_SCHEMA_NAMES if include_phase2 else ())
            + (PHASE3_SCHEMA_NAMES if include_phase3 else ())
            + (CP5A_SCHEMA_NAMES if include_cp5a else ())
            + (CP5BCD_SCHEMA_NAMES if include_cp5bcd else ())
            + (CP5HI_SCHEMA_NAMES if include_cp5hi else ())
        )
        self._schemas: dict[str, dict[str, Any]] = {}
        self._validators: dict[str, Draft202012Validator] = {}
        for name in resolved_names:
            path = (self.schema_dir / f"{name}.schema.json").resolve()
            contents = path.read_bytes()
            digest = sha256(contents).hexdigest()
            cache_key = (str(path), digest)
            cached = _SCHEMA_CACHE.get(cache_key)
            if cached is None:
                schema = json.loads(contents.decode("utf-8"))
                Draft202012Validator.check_schema(schema)
                cached = (schema, Draft202012Validator(schema, format_checker=FormatChecker()))
                _SCHEMA_CACHE[cache_key] = cached
            self._schemas[name], self._validators[name] = cached

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._schemas)

    def errors(self, name: str, value: Any) -> list[str]:
        validator = self._validators[name]
        errors = [
            f"{'/'.join(map(str, error.absolute_path)) or '$'}: {error.message}"
            for error in sorted(validator.iter_errors(value), key=lambda item: list(item.absolute_path))
        ]
        if name in {"figure-production-plan", "scientific-figure-spec"}:
            errors.extend(_figure_route_contract_errors(value, name))
        return errors

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


_FIGURE_ROUTES = {
    "quantitative_measured_result": ("scientific_plot", "scientific-plot-director", "reproducible_plot", "svg_vector", {"empirical"}, False, "canonical_data"),
    "real_experiment_photo": ("real_photo", "photo-annotation-director", "real_evidence_overlay", "source_evidence_asset", {"empirical"}, False, "real_evidence"),
    "literature_figure": ("literature_figure", "literature-figure-director", "source_extraction_overlay", "extracted_source_figure", {"literature_evidence"}, False, "literature_source"),
    "mechanism_explanation": ("mechanism_diagram", "mechanism-diagram-director", "deterministic_svg_vector", "svg_vector", {"empirical", "literature_evidence"}, False, "structured_spec"),
    "experiment_setup": ("experiment_schematic", "experiment-schematic-director", "deterministic_svg_vector", "svg_vector", {"empirical", "literature_evidence"}, False, "structured_spec"),
    "fabrication_process": ("fabrication_process_diagram", "fabrication-process-director", "deterministic_svg_vector", "svg_vector", {"empirical", "literature_evidence"}, False, "structured_spec"),
    "fishbone_history": ("fishbone_diagram", "fishbone-director", "deterministic_svg_vector", "svg_vector", {"empirical", "literature_evidence"}, False, "structured_spec"),
    "fair_comparison": ("comparison_diagram", "comparison-figure-director", "deterministic_svg_vector", "svg_vector", {"empirical", "literature_evidence"}, False, "structured_spec"),
    "image_matrix": ("image_matrix_figure", "image-matrix-director", "source_evidence_matrix", "source_evidence_asset", {"empirical"}, False, "real_evidence"),
    "organic_concept": ("concept_illustration", "concept-illustration-director", "generated_non_evidence", "generated_non_evidence_substrate", {"non_evidence"}, True, "non_evidence_only"),
}


def _figure_route_contract_errors(value: Any, name: str) -> list[str]:
    """Registered, fail-closed v4 route discriminator across plan/spec fields."""
    if not isinstance(value, dict) or value.get("schema_version") != "4.0.0":
        return []
    visual = value.get("visual_class")
    if name == "scientific-figure-spec":
        candidates = [route for route in _FIGURE_ROUTES.values() if route[0] == value.get("figure_type") and route[1] == value.get("director_skill")]
        if len(candidates) != 1:
            return ["$: ScientificFigureSpec route discriminator is invalid"]
        expected = candidates[0]
        actual = (value.get("figure_type"), value.get("director_skill"), value.get("renderer_class"), (value.get("output_targets") or [None])[0], value.get("evidence_status"))
    else:
        expected = _FIGURE_ROUTES.get(visual)
        if expected is None:
            return ["visual_class: unsupported FigureProductionPlan route"]
        actual = (value.get("figure_type"), value.get("selected_specialist_skill"), value.get("renderer_class"), value.get("canonical_output_kind"), value.get("evidence_status"))
    expected_values = expected[:4]
    labels = ("figure_type", "specialist", "renderer", "canonical_output")
    errors = [f"{label}: route discriminator mismatch" for label, got, want in zip(labels, actual[:4], expected_values) if got != want]
    if actual[4] not in expected[4]:
        errors.append("evidence_status: route discriminator mismatch")
    if visual is not None and value.get("ai_generation_allowed") != expected[5]:
        errors.append("ai_generation_allowed: route discriminator mismatch")
    if value.get("source_requirement") != expected[6]:
        errors.append("source_requirement: route discriminator mismatch")
    if name in {"figure-production-plan", "scientific-figure-spec"} and value.get("source_asset_required") != (expected[6] in {"real_evidence", "literature_source"}):
        errors.append("source_asset_required: source requirement mismatch")
    return errors

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
    for manifest in bundle.get("deck_manifests", []):
        ordinals = [slide.get("ordinal") for slide in manifest.get("slides", [])]
        if ordinals != list(range(1, len(ordinals) + 1)):
            findings.append(Finding("MANIFEST-ORDINAL-SEQUENCE", "schema_ledger_integrity", "Manifest ordinals must be unique and sequential", manifest.get("deck_id", "")))
    for profile in bundle.get("template_profiles", []):
        layouts = {layout.get("layout_index"): layout for layout in profile.get("layouts", [])}
        for role_name, role in profile.get("semantic_roles", {}).items():
            layout = layouts.get(role.get("layout_index"))
            if not layout or layout.get("layout_path") != role.get("layout_path") or layout.get("master_path") != role.get("master_path"):
                findings.append(Finding("TEMPLATE-ROLE-IDENTITY-MISMATCH", "schema_ledger_integrity", f"Semantic role {role_name} does not match its indexed layout", role_name))
    return findings


def validate_temporal_bindings(
    bundle: dict[str, Any],
    ledger: Any,
    specs: list[dict[str, Any]],
    manifests: list[dict[str, Any]],
    qa_reports: list[dict[str, Any]] | None = None,
) -> list[Finding]:
    """Validate immutable build bindings against the materialized state at each cursor.

    Research Block direct ref arrays are the graph boundary for that revision. Objects
    may originate in an earlier block revision, but never a later one, and every object
    used by a Slide Spec or Deck Manifest must be both materialized and reachable from
    the block revision active at that build cursor.
    """
    findings: list[Finding] = []
    qa_by_id = {report.get("qa_report_id"): report for report in qa_reports or []}
    assets_by_id = {asset.get("asset_id"): asset for asset in bundle.get("assets", [])}
    evidence_by_id = {card.get("evidence_id"): card for card in bundle.get("evidence_cards", [])}
    state_cache: dict[int, dict[str, Any]] = {}

    def add(rule_id: str, message: str, path: str) -> None:
        findings.append(Finding(rule_id, "schema_ledger_integrity", message, path))

    def state_at(cursor: Any, path: str) -> dict[str, Any] | None:
        if not isinstance(cursor, int) or cursor < 1 or cursor > len(ledger.replay()):
            add("TEMPORAL-CURSOR-INVALID", f"Cursor {cursor!r} is not present in the ledger", path)
            return None
        if cursor not in state_cache:
            state_cache[cursor] = ledger.materialize(cursor)
        return state_cache[cursor]

    def validate_binding(record: dict[str, Any], cursor: Any, block_ref: dict[str, Any], path: str) -> None:
        state = state_at(cursor, path)
        if state is None:
            return
        block_id = block_ref.get("block_id")
        block = state["blocks"].get(block_id)
        if block is None:
            add("TEMPORAL-BLOCK-MISSING", f"{block_id} is not materialized at cursor {cursor}", path)
            return
        block_revision = block.get("revision")
        if block_ref.get("revision") != block_revision:
            add("TEMPORAL-BLOCK-REVISION-MISMATCH", f"{block_id} revision {block_ref.get('revision')} does not equal materialized revision {block_revision} at cursor {cursor}", path)

        bindings = record.get("bindings", record)
        ref_contracts = (
            ("claim_refs", "claim_refs", "claims", "TEMPORAL-CLAIM-UNREACHABLE"),
            ("evidence_refs", "evidence_refs", "evidence", "TEMPORAL-EVIDENCE-UNREACHABLE"),
            ("asset_refs", "asset_refs", "assets", "TEMPORAL-ASSET-UNREACHABLE"),
            ("action_refs", "action_item_refs", "actions", "TEMPORAL-ACTION-UNREACHABLE"),
            ("decision_refs", "decision_refs", "decisions", "TEMPORAL-DECISION-UNREACHABLE"),
        )
        for binding_field, block_field, state_field, rule_id in ref_contracts:
            for ref in bindings.get(binding_field, []):
                # A meeting-delta slide may deliberately bind commitments from
                # more than one historical block.  Validate a reference against
                # its owning block below; do not wrongly require every binding
                # to be duplicated into every co-bound block graph.
                if ref not in block.get(block_field, []):
                    continue
                if ref not in state[state_field]:
                    add(rule_id, f"{ref} is not reachable from {block_id} revision {block_revision} at cursor {cursor}", f"{path}/{binding_field}/{ref}")

        for stage_name, stage_id in block.get("stage_refs", {}).items():
            if stage_name == "next_step":
                if stage_id not in state["actions"]:
                    add("TEMPORAL-STAGE-UNREACHABLE", f"Next Step {stage_id} is not materialized", path)
                continue
            stage = state["stages"].get(stage_id)
            if not stage:
                add("TEMPORAL-STAGE-UNREACHABLE", f"Stage {stage_id} is not materialized", path)
            elif stage.get("block_ref", {}).get("block_id") != block_id or stage.get("block_ref", {}).get("revision", 0) > block_revision:
                add("TEMPORAL-STAGE-BLOCK-REVISION", f"Stage {stage_id} has an impossible block revision", path)
        for stage_id in block.get("experiment_stage_refs", []) + block.get("result_stage_refs", []):
            stage = state["stages"].get(stage_id)
            if not stage:
                add("TEMPORAL-STAGE-UNREACHABLE", f"Stage {stage_id} is not materialized", path)
            elif stage.get("block_ref", {}).get("block_id") != block_id or stage.get("block_ref", {}).get("revision", 0) > block_revision:
                add("TEMPORAL-STAGE-BLOCK-REVISION", f"Stage {stage_id} has an impossible block revision", path)

        for ref in block.get("claim_refs", []):
            claim = state["claims"].get(ref)
            if not claim or claim.get("block_ref", {}).get("revision", 0) > block_revision:
                add("TEMPORAL-CLAIM-BLOCK-REVISION", f"Claim {ref} has an impossible block revision", path)
        for ref in block.get("action_item_refs", []):
            action = state["actions"].get(ref)
            linked = action.get("linked_block_refs", []) if action else []
            if not action or not any(item.get("block_id") == block_id and item.get("revision", 0) <= block_revision for item in linked):
                add("TEMPORAL-ACTION-BLOCK-REVISION", f"Action {ref} has an impossible block revision", path)
        for ref in block.get("decision_refs", []):
            decision = state["decisions"].get(ref)
            if not decision or decision.get("block_ref", {}).get("revision", 0) > block_revision:
                add("TEMPORAL-DECISION-BLOCK-REVISION", f"Decision {ref} has an impossible block revision", path)
        for ref in block.get("evidence_refs", []):
            card = evidence_by_id.get(ref)
            if ref not in state["evidence"] or not card or card.get("scope", {}).get("block_id") != block_id:
                add("TEMPORAL-EVIDENCE-BLOCK-SCOPE", f"Evidence {ref} is outside the materialized block graph", path)
        for ref in block.get("asset_refs", []):
            asset = assets_by_id.get(ref)
            if ref not in state["assets"] or not asset or not set(asset.get("source_evidence", [])) <= set(block.get("evidence_refs", [])):
                add("TEMPORAL-ASSET-BLOCK-SCOPE", f"Asset {ref} is outside the materialized block graph", path)

    def validate_record_block_union(record: dict[str, Any], cursor: Any, block_refs: list[dict[str, Any]], path: str) -> None:
        """Every bound ID must be owned by at least one declared block graph."""
        state = state_at(cursor, path)
        if state is None:
            return
        blocks = [state["blocks"].get(ref.get("block_id")) for ref in block_refs]
        bindings = record.get("bindings", record)
        for binding_field, block_field, state_field, rule_id in (
            ("claim_refs", "claim_refs", "claims", "TEMPORAL-CLAIM-UNREACHABLE"),
            ("evidence_refs", "evidence_refs", "evidence", "TEMPORAL-EVIDENCE-UNREACHABLE"),
            ("asset_refs", "asset_refs", "assets", "TEMPORAL-ASSET-UNREACHABLE"),
            ("action_refs", "action_item_refs", "actions", "TEMPORAL-ACTION-UNREACHABLE"),
            ("decision_refs", "decision_refs", "decisions", "TEMPORAL-DECISION-UNREACHABLE"),
        ):
            reachable = set().union(*(set(block.get(block_field, [])) for block in blocks if block))
            for ref in bindings.get(binding_field, []):
                if ref not in reachable or ref not in state[state_field]:
                    add(rule_id, f"{ref} is not reachable from any declared block at cursor {cursor}", f"{path}/{binding_field}/{ref}")

    for index, spec in enumerate(specs):
        block_refs = spec.get("block_refs", [])
        for block_ref in block_refs:
            validate_binding(spec, spec.get("source_cursor"), block_ref, f"slide_specs/{index}")
        validate_record_block_union(spec, spec.get("source_cursor"), block_refs, f"slide_specs/{index}")

    for manifest_index, manifest in enumerate(manifests):
        manifest_cursor = manifest.get("source_event_cursor")
        for slide_index, slide in enumerate(manifest.get("slides", [])):
            path = f"deck_manifests/{manifest_index}/slides/{slide_index}"
            # A cumulative master deck contains historical slides compiled at
            # earlier immutable cursors.  They must never point *after* the
            # manifest cursor, but equality is not required for every slide.
            if not isinstance(slide.get("source_event_cursor"), int) or slide.get("source_event_cursor") > manifest_cursor:
                add("TEMPORAL-MANIFEST-CURSOR-MISMATCH", "Slide cursor is after the manifest materialization cursor", path)
            block_refs = slide.get("block_refs", [slide.get("block_ref", {})])
            for block_ref in block_refs:
                validate_binding(slide, slide.get("source_event_cursor"), block_ref, path)
            validate_record_block_union(slide, slide.get("source_event_cursor"), block_refs, path)
            candidates = [spec for spec in specs if spec.get("slide_id") == slide.get("slide_id") and spec.get("source_cursor") == slide.get("source_event_cursor")]
            if not candidates:
                add("TEMPORAL-SLIDE-SPEC-MISSING", "Manifest slide has no matching Slide Spec at its cursor", path)
            else:
                spec = candidates[0]
                if spec.get("block_refs", [None])[0] != slide.get("block_ref") or spec.get("block_refs", []) != block_refs:
                    add("TEMPORAL-MANIFEST-SPEC-BLOCK-MISMATCH", "Manifest and Slide Spec block refs differ", path)
                for field in ("claim_refs", "evidence_refs", "asset_refs", "action_refs", "decision_refs"):
                    if set(spec.get("bindings", {}).get(field, [])) != set(slide.get(field, [])):
                        add("TEMPORAL-MANIFEST-SPEC-BINDING-MISMATCH", f"Manifest and Slide Spec {field} differ", path)
        for qa_ref in manifest.get("qa_report_refs", []):
            report = qa_by_id.get(qa_ref)
            if not report or report.get("deck_id") != manifest.get("deck_id") or report.get("build_id") != manifest.get("build_id"):
                add("QA-SCOPE-MISMATCH", f"QA report {qa_ref} does not match manifest deck/build scope", f"deck_manifests/{manifest_index}/qa_report_refs")
    return findings
