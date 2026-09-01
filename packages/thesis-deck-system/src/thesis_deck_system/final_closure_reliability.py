"""Bounded final-closure reliability primitives.

The raw repository privacy scanner deliberately remains conservative.  This
module provides a separate, sealed adjudication layer for *generated* PPTX
artifacts and durable local validation execution.  Neither component resolves
or opens a private source.
"""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from typing import Any, Callable, Iterable
import zipfile


class GeneratedArtifactAdjudicationError(ValueError):
    """A generated binary cannot be proven safe for privacy adjudication."""


def _canonical_hash(value: dict[str, Any]) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


class GeneratedArtifactAdjudicator:
    """Execution-owned generated-PPTX attestation over raw scanner findings."""

    _ARTIFACT_CLASSES = {
        "phase2_acceptance_deck", "n_layer_acceptance_deck", "sanitized_native_template", "final_acceptance_deck",
    }
    _SAFE_PART_PREFIXES = ("[Content_Types].xml", "_rels/", "docProps/", "ppt/")

    def __init__(self, *, root: Path, candidate_state_hash: str, approved_producers: dict[str, str | Path], generated_contracts: dict[str, tuple[str, str]], privacy_scanner: Any) -> None:
        if len(candidate_state_hash) != 64 or any(char not in "0123456789abcdef" for char in candidate_state_hash):
            raise GeneratedArtifactAdjudicationError("candidate hash must be SHA-256")
        self.root = Path(root).resolve()
        self.candidate_state_hash = candidate_state_hash
        self.privacy_scanner = privacy_scanner
        self.approved_producers = {
            producer_id: sha256(Path(source).read_bytes()).hexdigest()
            for producer_id, source in approved_producers.items()
        }
        self.generated_contracts = dict(generated_contracts)
        self._records: dict[str, dict[str, Any]] = {}

    def _relative_path(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except ValueError as error:
            raise GeneratedArtifactAdjudicationError("generated artifact is outside repository root") from error

    def _package_facts(self, package: Path) -> dict[str, Any]:
        try:
            with zipfile.ZipFile(package) as archive:
                names = sorted(info.filename for info in archive.infolist())
                if not names or any(not name.startswith(self._SAFE_PART_PREFIXES) for name in names):
                    raise GeneratedArtifactAdjudicationError("unknown package part")
                xml_parts = [name for name in names if name.endswith((".xml", ".rels"))]
                text_findings = []
                external_relationships = 0
                for name in xml_parts:
                    text = archive.read(name).decode("utf-8", errors="strict")
                    text_findings.extend(self.privacy_scanner._scan_private_repository_text(text, location="package-part", generic_absolute_paths=False))
                    external_relationships += text.count('TargetMode="External"') + text.count("TargetMode='External'")
        except (OSError, zipfile.BadZipFile, UnicodeDecodeError) as error:
            raise GeneratedArtifactAdjudicationError("generated artifact package is unreadable") from error
        lowered = [name.casefold() for name in names]
        return {
            "package_part_count": len(names),
            "package_inventory_sha256": sha256("\n".join(names).encode("utf-8")).hexdigest(),
            "external_relationship_count": external_relationships,
            "macro_part_count": sum("vbaproject" in name for name in lowered),
            "embedded_package_or_ole_count": sum("embeddings/" in name or "oleobject" in name for name in lowered),
            "package_privacy_finding_count": len(text_findings),
            "unknown_package_part_count": 0,
            "media_part_count": sum(name.startswith("ppt/media/") for name in lowered),
        }

    def attest_generated_pptx(self, package: Path, *, artifact_class: str, producer_id: str, declared_input_paths: Iterable[str | Path], execution_id: str) -> dict[str, Any]:
        package = Path(package)
        if artifact_class not in self._ARTIFACT_CLASSES or producer_id not in self.approved_producers or not execution_id:
            raise GeneratedArtifactAdjudicationError("unapproved generated artifact contract")
        if package.suffix.casefold() != ".pptx" or not package.is_file():
            raise GeneratedArtifactAdjudicationError("generated artifact is not a regular PPTX")
        path = self._relative_path(package)
        if self.generated_contracts.get(path) != (artifact_class, producer_id):
            raise GeneratedArtifactAdjudicationError("generated artifact path does not match its closed producer contract")
        declared_inputs = list(declared_input_paths)
        raw_input_findings = self.privacy_scanner.scan_paths(declared_inputs, location_root=self.root)
        # A declared dependency can itself be an already sealed generated
        # artifact.  That is not a private input, but an un-attested PPTX is.
        trusted_generated_inputs = {
            self._relative_path(Path(value))
            for value in declared_inputs
            if Path(value).suffix.casefold() == ".pptx"
            and Path(value).exists()
            and self._relative_path(Path(value)) in self._records
        }
        input_findings = [
            finding for finding in raw_input_findings
            if not (finding.classification == "private_pptx_candidate" and finding.location in trusted_generated_inputs)
        ]
        package_facts = self._package_facts(package)
        record = {
            "attestation_id": f"GPA-{sha256((self.candidate_state_hash + path).encode()).hexdigest()[:16]}",
            "status": "attested_generated_artifact",
            "repository_relative_path": path,
            "artifact_sha256": sha256(package.read_bytes()).hexdigest(),
            "candidate_state_hash": self.candidate_state_hash,
            "artifact_class": artifact_class,
            "producer_id": producer_id,
            "producer_source_sha256": self.approved_producers[producer_id],
            "declared_input_count": len(declared_inputs),
            "private_input_count": len(input_findings),
            "execution_id": execution_id,
            "raw_scanner_finding": "private_pptx_candidate",
            **package_facts,
        }
        record["evidence_sha256"] = _canonical_hash(record)
        self._records[path] = record
        return dict(record)

    def adjudicate_record(self, record: dict[str, Any]) -> dict[str, Any]:
        unsigned = {key: value for key, value in record.items() if key != "evidence_sha256"}
        if record.get("evidence_sha256") != _canonical_hash(unsigned):
            raise GeneratedArtifactAdjudicationError("attestation evidence is not sealed")
        expected = {
            "status": "attested_generated_artifact", "candidate_state_hash": self.candidate_state_hash,
            "raw_scanner_finding": "private_pptx_candidate",
        }
        if any(record.get(key) != value for key, value in expected.items()):
            raise GeneratedArtifactAdjudicationError("attestation binding is invalid")
        if record.get("artifact_class") not in self._ARTIFACT_CLASSES or record.get("producer_source_sha256") != self.approved_producers.get(record.get("producer_id")):
            raise GeneratedArtifactAdjudicationError("attestation producer is invalid")
        forbidden_counts = ("private_input_count", "external_relationship_count", "macro_part_count", "embedded_package_or_ole_count", "package_privacy_finding_count", "unknown_package_part_count")
        if any(record.get(key) != 0 for key in forbidden_counts):
            raise GeneratedArtifactAdjudicationError("generated package failed privacy closure")
        return {**record, "status": "adjudicated_safe_generated_artifact"}

    def adjudicate(self, package: Path, *, artifact_class: str, producer_id: str) -> dict[str, Any]:
        path = self._relative_path(Path(package))
        record = self._records.get(path)
        if record is None or record.get("artifact_class") != artifact_class or record.get("producer_id") != producer_id:
            raise GeneratedArtifactAdjudicationError("no execution-owned attestation for generated artifact")
        if sha256(Path(package).read_bytes()).hexdigest() != record.get("artifact_sha256"):
            raise GeneratedArtifactAdjudicationError("generated artifact hash is stale")
        return self.adjudicate_record(record)


def authoritative_privacy_adjudication(*, raw_findings: Iterable[Any], adjudicator: GeneratedArtifactAdjudicator, attestations: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Keep raw findings observable; clear only exact sealed generated records."""
    records = {record.get("repository_relative_path"): record for record in attestations}
    unexcepted: list[str] = []
    attested = 0
    raw_pptx = 0
    for finding in raw_findings:
        classification, location = finding.classification, finding.location
        if classification != "private_pptx_candidate":
            unexcepted.append(classification)
            continue
        raw_pptx += 1
        record = records.get(location)
        if record is None:
            unexcepted.append(classification)
            continue
        try:
            package = adjudicator.root / location
            adjudicator.adjudicate(package, artifact_class=record["artifact_class"], producer_id=record["producer_id"])
        except GeneratedArtifactAdjudicationError:
            unexcepted.append(classification)
        else:
            attested += 1
    return {
        "raw_pptx_candidate_count": raw_pptx,
        "attested_generated_pptx_count": attested,
        "unattested_pptx_count": raw_pptx - attested,
        "unexcepted_final_finding_count": len(unexcepted),
        "unexcepted_finding_categories": sorted(unexcepted),
    }


_FINAL_GENERATED_PPTX_CONTRACTS: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "thesis-deck-system/artifacts/phase2/acceptance-deck.pptx": ("phase2_acceptance_deck", "phase2-acceptance-builder", ("thesis-deck-system/artifacts/phase2/slide-specs.json", "thesis-deck-system/artifacts/phase2/materialized-h02.json")),
    "thesis-deck-system/artifacts/phase2/n-layer-acceptance-deck.pptx": ("n_layer_acceptance_deck", "phase2-acceptance-builder", ("thesis-deck-system/artifacts/phase2/n-layer-slide-specs.json", "thesis-deck-system/artifacts/phase2/materialized-h02.json")),
    "thesis-deck-system/artifacts/phase2/synthetic-template.pptx": ("sanitized_native_template", "sanitized-template-builder", ("packages/thesis-deck-system/src/thesis_deck_system/template.py",)),
    "thesis-deck-system/artifacts/phase3/final-sanitized-native-template.pptx": ("sanitized_native_template", "final-composition-builder", ("packages/thesis-deck-system/src/thesis_deck_system/template.py", "packages/thesis-deck-system/src/thesis_deck_system/phase3_final_visual_composition.py")),
    "thesis-deck-system/artifacts/phase3/cp5-final-visual-composition-acceptance-deck.pptx": ("final_acceptance_deck", "final-composition-builder", ("thesis-deck-system/artifacts/phase3/final-sanitized-native-template.pptx", "thesis-deck-system/artifacts/phase3/final-acceptance-slide-composition-plan.json")),
}


def attest_final_generated_pptx_set(root: Path, *, candidate_state_hash: str, privacy_scanner: Any, execution_id: str) -> list[dict[str, Any]]:
    """Attest the fixed generated outputs through declared producer contracts.

    This is intentionally not a generic PPTX allowlist: each path must be
    produced by its registered builder, hash-bound to the frozen candidate and
    pass independent package/privacy inspection.
    """
    root = Path(root).resolve()
    producers = {
        "phase2-acceptance-builder": root / "packages/thesis-deck-system/src/thesis_deck_system/phase2_build.py",
        "sanitized-template-builder": root / "packages/thesis-deck-system/src/thesis_deck_system/template.py",
        "final-composition-builder": root / "packages/thesis-deck-system/src/thesis_deck_system/phase3_final_visual_composition.py",
    }
    contracts = {path: (artifact_class, producer) for path, (artifact_class, producer, _) in _FINAL_GENERATED_PPTX_CONTRACTS.items()}
    adjudicator = GeneratedArtifactAdjudicator(root=root, candidate_state_hash=candidate_state_hash, approved_producers=producers, generated_contracts=contracts, privacy_scanner=privacy_scanner)
    records: list[dict[str, Any]] = []
    for relative_path, (artifact_class, producer, inputs) in _FINAL_GENERATED_PPTX_CONTRACTS.items():
        records.append(adjudicator.attest_generated_pptx(root / relative_path, artifact_class=artifact_class, producer_id=producer, declared_input_paths=[root / path for path in inputs], execution_id=execution_id))
    return records


class DurableValidationRunner:
    """Persist complete subprocess evidence before returning control to Codex."""

    def __init__(self, *, root: Path, evidence_root: Path, candidate_hash: Callable[[], str]) -> None:
        self.root = Path(root).resolve()
        self.evidence_root = Path(evidence_root).resolve()
        self.evidence_root.mkdir(parents=True, exist_ok=True)
        self.candidate_hash = candidate_hash

    def run(self, tier: str, command: list[str]) -> dict[str, Any]:
        run_id = sha256((tier + "\0" + "\0".join(command) + "\0" + datetime.now(timezone.utc).isoformat()).encode()).hexdigest()[:16]
        stdout_path = self.evidence_root / f"{run_id}.stdout.log"
        stderr_path = self.evidence_root / f"{run_id}.stderr.log"
        record_path = self.evidence_root / f"{run_id}.json"
        record = {"run_id": run_id, "tier": tier, "command": command, "head": self._git("rev-parse", "HEAD"), "candidate_hash_pre": self.candidate_hash(), "started_at": datetime.now(timezone.utc).isoformat(), "stdout_path": str(stdout_path), "stderr_path": str(stderr_path), "completion_status": "running"}
        record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
            completed = subprocess.run(command, cwd=self.root, stdout=stdout, stderr=stderr, check=False, text=True)
        record.update({"exit_code": completed.returncode, "candidate_hash_post": self.candidate_hash(), "ended_at": datetime.now(timezone.utc).isoformat(), "completion_status": "completed"})
        record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return record

    def build_manifest(self, node_ids: Iterable[str], *, shard_count: int) -> dict[str, Any]:
        """Create a deterministic, coverage-auditable shard manifest.

        The caller supplies the authoritative `pytest --collect-only` node
        list.  Shards are intentionally sequential by default: shared build
        artifacts have not been proven safe for parallel execution.
        """
        nodes = list(node_ids)
        if shard_count <= 0 or len(nodes) != len(set(nodes)):
            raise ValueError("validation collection must be unique and shard count positive")
        shards = [{"shard_id": f"shard-{index + 1}", "node_ids": nodes[index::shard_count]} for index in range(shard_count)]
        executed = [node for shard in shards for node in shard["node_ids"]]
        return {
            "manifest_id": "FC-VALIDATION-MANIFEST-001", "execution_model": "sequential_durable_shards",
            "full_collection_count": len(nodes), "executed_unique_count": len(set(executed)),
            "missing_count": len(set(nodes) - set(executed)), "duplicate_count": len(executed) - len(set(executed)),
            "shards": shards,
        }

    def _git(self, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=self.root, check=False, capture_output=True, text=True, encoding="utf-8").stdout.strip()


def native_materialization_parity(materializations: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Derive plan→assembler parity facts; never infer an emitted object."""
    records = list(materializations)
    style_fields = ("geometry", "fill", "stroke", "stroke_width", "font_family", "font_size", "font_weight", "dash", "marker", "transform")
    coverage = {
        field: {
            "supported": sum(record["style_coverage"].get(field) == "supported" for item in records for record in item.get("materialization_records", [])),
            "fallback": 0,
            "unresolved": sum(record["style_coverage"].get(field) == "unresolved" for item in records for record in item.get("materialization_records", [])),
        }
        for field in style_fields
    }
    planned = sum(item.get("planned_native_object_count", -1) for item in records)
    emitted = sum(item.get("native_object_count", 0) for item in records)
    fallback = sum(item.get("fallback_object_count", 0) for item in records)
    mismatches = sum(item.get("native_mismatch_count", 1) for item in records)
    return {
        "parity_id": "FC-NATIVE-PARITY-001", "aggregate_status": "pass" if records and mismatches == 0 else "fail",
        "planned_native_object_count": planned, "emitted_native_object_count": emitted,
        "explicit_fallback_object_count": fallback, "blocked_object_count": 0,
        "native_mismatch_count": mismatches, "style_field_coverage": coverage,
        "materialization_record_count": len(records),
    }


def build_final_closure_qa(*, candidate_state_hash: str, parity: dict[str, Any], privacy: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    """Project final closure status from executed evidence, never literals."""
    checks = [
        ("FC-P0-01-NATIVE-PARITY", parity.get("aggregate_status") == "pass" and parity.get("native_mismatch_count") == 0, {"native_mismatch_count": parity.get("native_mismatch_count")}),
        ("FC-P0-06-GENERATED-PPTX-PRIVACY", privacy.get("unexcepted_final_finding_count") == 0 and privacy.get("attested_generated_pptx_count") == privacy.get("raw_pptx_candidate_count"), {"raw_pptx_candidate_count": privacy.get("raw_pptx_candidate_count"), "attested_generated_pptx_count": privacy.get("attested_generated_pptx_count"), "unexcepted_final_finding_count": privacy.get("unexcepted_final_finding_count")}),
        ("FC-P1-07-DURABLE-VALIDATION", validation.get("completion_status") == "completed" and validation.get("exit_code") == 0 and validation.get("candidate_hash_pre") == candidate_state_hash and validation.get("candidate_hash_post") == candidate_state_hash, {"exit_code": validation.get("exit_code"), "candidate_hash_pre": validation.get("candidate_hash_pre"), "candidate_hash_post": validation.get("candidate_hash_post")}),
    ]
    owning_checks = [{"check_id": check_id, "status": "pass" if passed else "fail", "facts": facts, "facts_sha256": _canonical_hash(facts)} for check_id, passed, facts in checks]
    return {"qa_id": "FC-RELIABILITY-QA-001", "candidate_state_hash": candidate_state_hash, "aggregate_status": "pass" if all(item["status"] == "pass" for item in owning_checks) else "fail", "owning_checks": owning_checks}
