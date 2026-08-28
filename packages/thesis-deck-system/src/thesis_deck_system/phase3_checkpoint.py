"""Execution-derived, non-private evidence for Phase 3 Checkpoint 1."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
import subprocess
import sys
from typing import Callable


class Checkpoint1PolicyViolation(RuntimeError):
    """Raised after a forbidden Checkpoint 1 operation is recorded."""


_CHECK_IDS = (
    "CP1-PRIVACY-ROOT", "CP1-SANITIZER-SCANNER", "CP1-PROVIDER-AUTHORIZATION",
    "CP1-FIGURE-CONTRACTS", "CP1-OBSERVATION-EVIDENCE", "CP1-FABRICATION-CONTRACTS",
    "CP1-PHASE1-PHASE2-REGRESSION",
)
_STATUS_FIELDS = {
    "CP1-PRIVACY-ROOT": "privacy_root_status",
    "CP1-SANITIZER-SCANNER": "sanitizer_scanner_status",
    "CP1-PROVIDER-AUTHORIZATION": "provider_authorization_status",
    "CP1-FIGURE-CONTRACTS": "figure_contract_status",
    "CP1-OBSERVATION-EVIDENCE": "observation_evidence_status",
    "CP1-FABRICATION-CONTRACTS": "fabrication_contract_status",
    "CP1-PHASE1-PHASE2-REGRESSION": "phase1_phase2_regression_status",
}
_EXECUTOR_AUTHORITY = object()
_CANONICAL_BUILDER_AUTHORITY = object()


@dataclass
class Checkpoint1ExecutionEvidence:
    """The sole input from which the Checkpoint 1 QA summary is derived."""

    _owning_checks: dict[str, str] = field(default_factory=dict)
    _attempts: list[str] = field(default_factory=list)
    _sealed: bool = False
    _executor_authority: object | None = field(default=None, repr=False)
    _canonical_builder_authority: object | None = field(default=None, repr=False)

    @classmethod
    def start(cls) -> "Checkpoint1ExecutionEvidence":
        return cls()

    @staticmethod
    def required_check_ids() -> tuple[str, ...]:
        return _CHECK_IDS

    @property
    def private_source_open_attempts(self) -> int:
        return self._attempts.count("private_source_open")

    @property
    def real_private_alias_resolution_attempts(self) -> int:
        return self._attempts.count("private_alias_resolution")

    @property
    def owning_checks(self) -> dict[str, str]:
        return dict(self._owning_checks)

    def _record_check(self, check_id: str, result: str) -> None:
        if check_id not in _CHECK_IDS or result not in {"pass", "fail"}:
            raise ValueError("invalid Checkpoint 1 owning check")
        self._owning_checks[check_id] = result

    def _seal_after_execution(self, authority: object) -> None:
        if authority is not _EXECUTOR_AUTHORITY:
            raise ValueError("Checkpoint 1 evidence may only be sealed by the owning executor")
        self._sealed = True
        self._executor_authority = authority

    @property
    def is_executor_sealed(self) -> bool:
        return self._sealed and self._executor_authority is _EXECUTOR_AUTHORITY

    @property
    def is_canonical_builder_attested(self) -> bool:
        return self._canonical_builder_authority is _CANONICAL_BUILDER_AUTHORITY

    def _attest_canonical_builder(self, authority: object) -> None:
        if authority is not _CANONICAL_BUILDER_AUTHORITY or not self.is_executor_sealed:
            raise ValueError("Checkpoint 1 builder attestation is invalid")
        self._canonical_builder_authority = authority

    def reject_private_alias_resolution(self, _safe_request_id: str) -> None:
        self._attempts.append("private_alias_resolution")
        raise Checkpoint1PolicyViolation("Checkpoint 1 blocks private alias resolution")

    def reject_private_source_open(self, _safe_request_id: str) -> None:
        self._attempts.append("private_source_open")
        raise Checkpoint1PolicyViolation("Checkpoint 1 blocks private source open")

    def payload(self) -> dict:
        return {
            "schema_version": "3.1.0", "evidence_id": "CP1-EXEC-001",
            "policy_id": "checkpoint_1_private_source_free",
            "private_source_open_attempts": self.private_source_open_attempts,
            "real_private_alias_resolution_attempts": self.real_private_alias_resolution_attempts,
            "attempt_kinds": list(self._attempts),
            "owning_checks": [{"check_id": check_id, "result": self._owning_checks.get(check_id, "missing")} for check_id in _CHECK_IDS],
        }

    def sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.payload(), sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def checkpoint1_qa_record(execution_evidence: Checkpoint1ExecutionEvidence) -> dict:
    """Derive summary fields from persisted owning execution evidence only."""
    if not execution_evidence.is_executor_sealed or not execution_evidence.is_canonical_builder_attested:
        raise ValueError("Checkpoint 1 execution evidence is not sealed by the canonical owning builder")
    payload = execution_evidence.payload()
    checks = {item["check_id"]: item["result"] for item in payload["owning_checks"]}
    aggregate = "pass" if execution_evidence.private_source_open_attempts == 0 and execution_evidence.real_private_alias_resolution_attempts == 0 and all(checks[check_id] == "pass" for check_id in _CHECK_IDS) else "fail"
    record = {
        "schema_version": "3.1.0", "checkpoint_id": "PHASE_3_CHECKPOINT_1",
        "execution_evidence_id": payload["evidence_id"], "execution_evidence_sha256": execution_evidence.sha256(),
        "execution_evidence": payload,
        "private_source_open_attempts": execution_evidence.private_source_open_attempts,
        "real_private_alias_resolution_attempts": execution_evidence.real_private_alias_resolution_attempts,
        **{field: checks[check_id] for check_id, field in _STATUS_FIELDS.items()},
        "aggregate_status": aggregate,
    }
    errors = validate_checkpoint1_qa(record)
    if errors:
        raise ValueError("invalid execution-derived checkpoint QA: " + "; ".join(errors))
    return record


def execute_checkpoint1_owning_checks(checks: dict[str, object]) -> Checkpoint1ExecutionEvidence:
    """Execute each owning check and record its actual result before summarizing."""
    if set(checks) != set(_CHECK_IDS):
        raise ValueError("Checkpoint 1 requires every owning check")
    evidence = Checkpoint1ExecutionEvidence.start()
    for check_id in _CHECK_IDS:
        check = checks[check_id]
        if not callable(check):
            raise ValueError("Checkpoint 1 owning check must be callable")
        try:
            check()
        except Exception:
            evidence._record_check(check_id, "fail")
        else:
            evidence._record_check(check_id, "pass")
    evidence._seal_after_execution(_EXECUTOR_AUTHORITY)
    return evidence


def validate_checkpoint1_qa(record: dict) -> list[str]:
    """Verify hash-bound evidence and every derived final summary field."""
    evidence = record.get("execution_evidence")
    if not isinstance(evidence, dict):
        return ["CP1-QA-EXECUTION-EVIDENCE-MISSING"]
    errors: list[str] = []
    actual_hash = hashlib.sha256(json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    if record.get("execution_evidence_id") != evidence.get("evidence_id") or record.get("execution_evidence_sha256") != actual_hash:
        errors.append("CP1-QA-EXECUTION-EVIDENCE-HASH")
    checks = {item.get("check_id"): item.get("result") for item in evidence.get("owning_checks", []) if isinstance(item, dict)}
    if set(checks) != set(_CHECK_IDS) or any(checks.get(key) not in {"pass", "fail"} for key in _CHECK_IDS):
        return errors + ["CP1-QA-OWNING-CHECKS"]
    for check_id, field in _STATUS_FIELDS.items():
        if record.get(field) != checks[check_id]:
            errors.append("CP1-QA-STATUS-NONDERIVED")
    for field in ("private_source_open_attempts", "real_private_alias_resolution_attempts"):
        if record.get(field) != evidence.get(field) or not isinstance(record.get(field), int):
            errors.append("CP1-QA-ATTEMPTS-NONDERIVED")
    attempt_kinds = evidence.get("attempt_kinds", [])
    if (
        not isinstance(attempt_kinds, list)
        or evidence.get("private_source_open_attempts") != attempt_kinds.count("private_source_open")
        or evidence.get("real_private_alias_resolution_attempts") != attempt_kinds.count("private_alias_resolution")
    ):
        errors.append("CP1-QA-ATTEMPT-EVENT-COUNT")
    aggregate = "pass" if evidence.get("private_source_open_attempts") == 0 and evidence.get("real_private_alias_resolution_attempts") == 0 and all(checks[key] == "pass" for key in _CHECK_IDS) else "fail"
    if record.get("aggregate_status") != aggregate:
        errors.append("CP1-QA-AGGREGATE-NONDERIVED")
    return errors


def write_checkpoint1_qa(path: Path | str, *, execution_evidence: Checkpoint1ExecutionEvidence) -> dict:
    record = checkpoint1_qa_record(execution_evidence)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return record


def _run_phase1_phase2_regression(repository_root: Path) -> None:
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(repository_root / "packages" / "thesis-deck-system" / "src")
    subprocess.run([sys.executable, "-m", "pytest", "packages/thesis-deck-system/tests", "-q"], cwd=repository_root, env=environment, check=True)


def build_checkpoint1_qa(path: Path | str, *, repository_root: Path | str) -> dict:
    """Execute all non-private owning checks and persist their derived summary."""
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.image_review import preflight_image_review
    from thesis_deck_system.phase3_contracts import canonical_observation_catalogs, validate_fabrication_process, validate_observation_visual_binding
    from thesis_deck_system.phase3_privacy import PrivateProfileStore, RepositoryPrivacyScanner, sanitize_profile

    root = Path(repository_root)
    sha = "a" * 64
    registry = SchemaRegistry(root / "thesis-deck-system" / "schemas", include_phase3=True)
    provider = {"provider_id": "synthetic_image_reviewer", "image_capable": True, "hash_binding_supported": True, "private_content_allowed": True, "approved_for_private_exemplars": True, "egress_mode": "local_only", "retention_class": "ephemeral", "supported_input_forms": ["repository_relative_path", "local_private_handle"]}
    evidence_card = {"schema_version": "1.0.0", "evidence_id": "E001", "kind": "synthetic_measurement", "title": "Synthetic canonical evidence", "provenance": "synthetic_test_only", "source": {"source_id": "S001", "uri": "fixtures/synthetic.json", "sha256": sha}, "claim_support_refs": [], "claim_contradict_refs": [], "scope": {}, "verification": {"status": "synthetic_test_only"}}
    figure_output = {"schema_version": "3.0.0", "figure_output_id": "FOM001", "figure_id": "FIG001", "figure_type": "scientific_plot", "primary_artifact_kind": "svg_vector", "renderer": "synthetic_renderer", "source_spec_sha256": sha, "provenance_refs": ["E001"], "style_profile_ref": "VSP001", "evidence_status": "synthetic_test_evidence", "primary_artifact": {"path": "artifacts/cp1/plot.svg", "sha256": sha, "data_provenance_refs": ["E001"]}, "output_part_lineage": ["generated"]}
    binding = {"observation_id": "OBS001", "empirical_evidence_required": True, "observation_evidence_ref": "E001", "observation_output_ref": "FOM001", "evidence_refs": ["E001"], "auxiliary_visuals": []}
    fabrication = {"process_id": "FP001", "process_kind": "fabrication_process", "provenance_refs": ["E001"], "steps": [{"ordinal": 1, "operation": "mix", "material_refs": ["M001"], "state_before": "precursors", "state_after": "mixture", "conditions": {"temperature_c": "unknown", "duration_min": "unknown"}}]}

    def ensure(condition: bool, message: str) -> None:
        if not condition:
            raise RuntimeError(message)

    checks: dict[str, Callable[[], None]] = {
        "CP1-PRIVACY-ROOT": lambda: ensure(PrivateProfileStore(root / ".private" / "phase3" / "checkpoint-1-evidence", repository_root=root).prepare_for_future_open()["private_source_open_permitted"] is False, "privacy root probe"),
        "CP1-SANITIZER-SCANNER": lambda: (ensure(not RepositoryPrivacyScanner().scan_repository(root), "repository privacy scan"), sanitize_profile({"alias_uri": "private://template_primary_1", "resolved_status": "resolved", "source_sha256": sha, "sanitized_profile_id": "SP001", "slide_size": {"width": 13.333, "height": 7.5}})),
        "CP1-PROVIDER-AUTHORIZATION": lambda: ensure(preflight_image_review(provider, private_reference=True).status == "approved", "provider preflight"),
        "CP1-FIGURE-CONTRACTS": lambda: ensure(not registry.errors("figure-output-manifest", figure_output), "figure output schema"),
        "CP1-OBSERVATION-EVIDENCE": lambda: ensure(not validate_observation_visual_binding(binding, catalog=canonical_observation_catalogs(registry, [evidence_card], [figure_output])), "observation provenance"),
        "CP1-FABRICATION-CONTRACTS": lambda: ensure(not validate_fabrication_process(fabrication), "fabrication contract"),
        "CP1-PHASE1-PHASE2-REGRESSION": lambda: _run_phase1_phase2_regression(root),
    }
    evidence = execute_checkpoint1_owning_checks(checks)
    evidence._attest_canonical_builder(_CANONICAL_BUILDER_AUTHORITY)
    return write_checkpoint1_qa(path, execution_evidence=evidence)
