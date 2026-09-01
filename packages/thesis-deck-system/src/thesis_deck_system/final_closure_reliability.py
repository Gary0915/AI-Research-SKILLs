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
import re
import subprocess
from typing import Any, Callable, Iterable
import zipfile


class GeneratedArtifactAdjudicationError(ValueError):
    """A generated binary cannot be proven safe for privacy adjudication."""


def _canonical_hash(value: dict[str, Any]) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def build_generated_source_closure(root: Path, declared_inputs: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Close every direct generated-PPTX input to a safe repository identity."""
    root = Path(root).resolve()
    required = {"input_id", "repository_relative_path", "input_class", "producer_id", "input_role", "source_kind", "privacy_status"}
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in declared_inputs:
        if set(item) != required or not isinstance(item.get("input_id"), str) or item["input_id"] in seen:
            raise GeneratedArtifactAdjudicationError("generated source closure input contract is invalid")
        relative = item.get("repository_relative_path")
        if not isinstance(relative, str) or relative.startswith(("/", "\\")) or ".." in Path(relative).parts:
            raise GeneratedArtifactAdjudicationError("generated source closure path is unsafe")
        path = (root / relative).resolve()
        try:
            path.relative_to(root)
        except ValueError as error:
            raise GeneratedArtifactAdjudicationError("generated source closure path escapes repository") from error
        if not path.is_file() or item.get("privacy_status") != "sanitized":
            raise GeneratedArtifactAdjudicationError("generated source closure input is unresolved or private")
        seen.add(item["input_id"])
        records.append({**item, "input_sha256": sha256(path.read_bytes()).hexdigest()})
    records.sort(key=lambda value: value["input_id"])
    closure_sha256 = _canonical_hash({"input_records": records})
    return {
        "source_closure_id": f"FEC-SOURCE-CLOSURE-{closure_sha256[:12].upper()}",
        "input_records": records,
        "input_record_count": len(records),
        "unresolved_input_count": 0,
        "private_input_count": 0,
        "source_closure_sha256": closure_sha256,
    }


def build_package_media_lineage(package: Path, source_records: Iterable[dict[str, Any]], media_sources: dict[str, str]) -> dict[str, Any]:
    """Map every PPTX media part to one closed source record, fail closed."""
    by_id = {item.get("input_id"): item for item in source_records}
    try:
        with zipfile.ZipFile(package) as archive:
            media_names = sorted(name for name in archive.namelist() if name.startswith("ppt/media/"))
            records: list[dict[str, Any]] = []
            for name in media_names:
                source_id = media_sources.get(name)
                source = by_id.get(source_id)
                if source is None:
                    raise GeneratedArtifactAdjudicationError("package media part has no declared source lineage")
                media_sha = sha256(archive.read(name)).hexdigest()
                source_sha = source.get("input_sha256")
                if media_sha != source_sha:
                    raise GeneratedArtifactAdjudicationError("package media bytes do not match declared source")
                records.append({
                    "package_part_name": name,
                    "media_sha256": media_sha,
                    "media_type": Path(name).suffix.casefold().lstrip(".") or "unknown",
                    "source_kind": source["source_kind"],
                    "source_ref": source_id,
                    "source_sha256": source_sha,
                    "producer_id": source["producer_id"],
                    "lineage_status": "exact_source_bytes",
                })
    except (OSError, zipfile.BadZipFile) as error:
        raise GeneratedArtifactAdjudicationError("package media inventory is unreadable") from error
    declared_extra = set(media_sources) - set(media_names)
    if declared_extra:
        raise GeneratedArtifactAdjudicationError("media lineage declares absent package parts")
    lineage_sha256 = _canonical_hash({"media_lineage_records": records})
    return {
        "media_lineage_id": f"FEC-MEDIA-LINEAGE-{lineage_sha256[:12].upper()}",
        "package_media_part_count": len(media_names),
        "media_lineage_records": records,
        "unresolved_media_part_count": 0,
        "undeclared_media_part_count": 0,
        "duplicate_media_lineage_count": len(records) - len({item["package_part_name"] for item in records}),
        "media_lineage_sha256": lineage_sha256,
    }


class GeneratedArtifactAdjudicator:
    """Execution-owned generated-PPTX attestation over raw scanner findings."""

    _ARTIFACT_CLASSES = {
        "phase2_acceptance_deck", "n_layer_acceptance_deck", "sanitized_native_template", "final_acceptance_deck",
        "planner_composition_review_deck",
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

    def _staged_identity(self, relative_path: str) -> tuple[str, bytes]:
        """Read one stage-0 Git-index blob without trusting checkout bytes."""
        listed = subprocess.run(
            ["git", "ls-files", "--stage", "--", relative_path],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        entries = [line.split(maxsplit=3) for line in listed.stdout.splitlines() if line.strip()]
        if listed.returncode != 0 or len(entries) != 1 or len(entries[0]) != 4:
            raise GeneratedArtifactAdjudicationError("staged generated artifact has no exact index entry")
        _mode, blob_sha, stage, staged_path = entries[0]
        if stage != "0" or staged_path != relative_path:
            raise GeneratedArtifactAdjudicationError("staged generated artifact index identity is ambiguous")
        blob = subprocess.run(
            ["git", "cat-file", "blob", blob_sha],
            cwd=self.root,
            check=False,
            capture_output=True,
        )
        if blob.returncode != 0:
            raise GeneratedArtifactAdjudicationError("staged generated artifact blob cannot be read")
        return blob_sha, blob.stdout

    def attest_staged_generated_pptx(
        self,
        package: Path,
        *,
        artifact_class: str,
        producer_id: str,
        declared_input_paths: Iterable[str | Path],
        execution_id: str,
        source_closure: dict[str, Any] | None = None,
        media_lineage: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Attest exact stage-0 bytes, then seal working/index parity facts."""
        record = self.attest_generated_pptx(
            package,
            artifact_class=artifact_class,
            producer_id=producer_id,
            declared_input_paths=declared_input_paths,
            execution_id=execution_id,
        )
        path = record["repository_relative_path"]
        staged_blob_sha, staged_bytes = self._staged_identity(path)
        staged_bytes_sha256 = sha256(staged_bytes).hexdigest()
        working_sha256 = sha256(Path(package).read_bytes()).hexdigest() if Path(package).is_file() else None
        if (source_closure is None) != (media_lineage is None):
            raise GeneratedArtifactAdjudicationError("source closure and media lineage must bind together")
        closure_facts: dict[str, Any] = {}
        if source_closure is not None and media_lineage is not None:
            required_closure = {"source_closure_id", "source_closure_sha256", "input_record_count", "unresolved_input_count", "private_input_count"}
            required_media = {"media_lineage_id", "media_lineage_sha256", "package_media_part_count", "unresolved_media_part_count", "undeclared_media_part_count", "duplicate_media_lineage_count"}
            if not required_closure <= set(source_closure) or not required_media <= set(media_lineage):
                raise GeneratedArtifactAdjudicationError("source/media closure evidence is incomplete")
            if any(source_closure[key] != 0 for key in ("unresolved_input_count", "private_input_count")):
                raise GeneratedArtifactAdjudicationError("source closure is not safe")
            if any(media_lineage[key] != 0 for key in ("unresolved_media_part_count", "undeclared_media_part_count", "duplicate_media_lineage_count")):
                raise GeneratedArtifactAdjudicationError("media lineage is not closed")
            if media_lineage["package_media_part_count"] != record["media_part_count"]:
                raise GeneratedArtifactAdjudicationError("media lineage does not match package inventory")
            closure_facts = {
                "source_closure_id": source_closure["source_closure_id"],
                "source_closure_sha256": source_closure["source_closure_sha256"],
                "source_closure_input_record_count": source_closure["input_record_count"],
                "media_lineage_id": media_lineage["media_lineage_id"],
                "media_lineage_sha256": media_lineage["media_lineage_sha256"],
                "media_lineage_record_count": len(media_lineage.get("media_lineage_records", [])),
            }
        record.update({
            "staged_git_blob_sha": staged_blob_sha,
            "staged_bytes_sha256": staged_bytes_sha256,
            "working_tree_sha256": working_sha256,
            "working_tree_matches_staged": working_sha256 == staged_bytes_sha256,
            "artifact_sha256": staged_bytes_sha256,
            **closure_facts,
        })
        record["evidence_sha256"] = _canonical_hash({key: value for key, value in record.items() if key != "evidence_sha256"})
        self._records[path] = record
        return dict(record)

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
        source_media_keys = ("source_closure_id", "source_closure_sha256", "source_closure_input_record_count", "media_lineage_id", "media_lineage_sha256", "media_lineage_record_count")
        present = [key in record for key in source_media_keys]
        if any(present) and not all(present):
            raise GeneratedArtifactAdjudicationError("attestation source/media binding is incomplete")
        if all(present):
            if not isinstance(record["source_closure_id"], str) or not isinstance(record["media_lineage_id"], str):
                raise GeneratedArtifactAdjudicationError("attestation source/media identity is invalid")
            if any(not isinstance(record[key], str) or len(record[key]) != 64 for key in ("source_closure_sha256", "media_lineage_sha256")):
                raise GeneratedArtifactAdjudicationError("attestation source/media hash is invalid")
            if record["source_closure_input_record_count"] < 0 or record["media_lineage_record_count"] != record.get("media_part_count"):
                raise GeneratedArtifactAdjudicationError("attestation source/media counts are invalid")
        return {**record, "status": "adjudicated_safe_generated_artifact"}

    def adjudicate(self, package: Path, *, artifact_class: str, producer_id: str) -> dict[str, Any]:
        path = self._relative_path(Path(package))
        record = self._records.get(path)
        if record is None or record.get("artifact_class") != artifact_class or record.get("producer_id") != producer_id:
            raise GeneratedArtifactAdjudicationError("no execution-owned attestation for generated artifact")
        if "staged_git_blob_sha" in record:
            staged_blob_sha, staged_bytes = self._staged_identity(path)
            staged_sha256 = sha256(staged_bytes).hexdigest()
            if (
                staged_blob_sha != record.get("staged_git_blob_sha")
                or staged_sha256 != record.get("staged_bytes_sha256")
                or staged_sha256 != record.get("artifact_sha256")
            ):
                raise GeneratedArtifactAdjudicationError("staged generated artifact identity is stale")
            current_working_sha = sha256(Path(package).read_bytes()).hexdigest() if Path(package).is_file() else None
            if current_working_sha != record.get("working_tree_sha256") or current_working_sha != staged_sha256:
                raise GeneratedArtifactAdjudicationError("working tree does not match staged generated artifact")
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
    "thesis-deck-system/artifacts/phase3/planner-composition-candidate-review.pptx": ("planner_composition_review_deck", "presentation-planner-application-builder", ("packages/thesis-deck-system/src/thesis_deck_system/presentation_planner_application.py", "packages/thesis-deck-system/src/thesis_deck_system/pptx.py", "packages/thesis-deck-system/src/thesis_deck_system/template.py")),
}

# Every source path below is a repository-owned sanitized/generated input.  The
# mapping is intentionally package-part specific: byte equality, not filename
# similarity, proves the media source relationship.
_FINAL_GENERATED_PPTX_MEDIA_SOURCES: dict[str, dict[str, str]] = {
    "thesis-deck-system/artifacts/phase2/acceptance-deck.pptx": {
        "ppt/media/A002.svg": "thesis-deck-system/artifacts/phase2/observation/observation_visual.svg",
        "ppt/media/A101.svg": "thesis-deck-system/artifacts/phase2/fishbone/FB001-rev1.svg",
        "ppt/media/A102.svg": "thesis-deck-system/artifacts/phase2/fishbone/FB001-rev2.svg",
        "ppt/media/A201.svg": "thesis-deck-system/artifacts/phase2/plots/H02_contact_pressure.svg",
        "ppt/media/image1.png": "thesis-deck-system/artifacts/phase2/fishbone/FB001-rev1.png",
        "ppt/media/image2.png": "thesis-deck-system/artifacts/phase2/observation/observation_visual.png",
        "ppt/media/image3.png": "thesis-deck-system/artifacts/phase2/plots/B001_defect_density.png",
        "ppt/media/image4.png": "thesis-deck-system/artifacts/phase2/fishbone/FB001-rev2.png",
        "ppt/media/image5.png": "thesis-deck-system/artifacts/phase2/plots/H02_contact_pressure.png",
        "ppt/media/plot-canonical.svg": "thesis-deck-system/artifacts/phase2/plots/B001_defect_density.svg",
    },
    "thesis-deck-system/artifacts/phase2/n-layer-acceptance-deck.pptx": {
        "ppt/media/A002.svg": "thesis-deck-system/artifacts/phase2/observation/observation_visual.svg",
        "ppt/media/A101.svg": "thesis-deck-system/artifacts/phase2/fishbone/FB001-rev1.svg",
        "ppt/media/A102.svg": "thesis-deck-system/artifacts/phase2/fishbone/FB001-rev2.svg",
        "ppt/media/A201.svg": "thesis-deck-system/artifacts/phase2/plots/H02_contact_pressure.svg",
        "ppt/media/A301.svg": "thesis-deck-system/artifacts/phase2/plots/H02_contact_pressure.svg",
        "ppt/media/A302.svg": "thesis-deck-system/artifacts/phase2/fishbone/FB001-rev2.svg",
        "ppt/media/image1.png": "thesis-deck-system/artifacts/phase2/fishbone/FB001-rev1.png",
        "ppt/media/image2.png": "thesis-deck-system/artifacts/phase2/observation/observation_visual.png",
        "ppt/media/image3.png": "thesis-deck-system/artifacts/phase2/plots/B001_defect_density.png",
        "ppt/media/image4.png": "thesis-deck-system/artifacts/phase2/fishbone/FB001-rev2.png",
        "ppt/media/image5.png": "thesis-deck-system/artifacts/phase2/plots/H02_contact_pressure.png",
        "ppt/media/plot-canonical.svg": "thesis-deck-system/artifacts/phase2/plots/B001_defect_density.svg",
    },
    "thesis-deck-system/artifacts/phase2/synthetic-template.pptx": {},
    "thesis-deck-system/artifacts/phase3/final-sanitized-native-template.pptx": {},
    "thesis-deck-system/artifacts/phase3/cp5-final-visual-composition-acceptance-deck.pptx": {
        "ppt/media/image1.png": "thesis-deck-system/artifacts/phase2/fishbone/FB001-rev1.png",
        "ppt/media/image2.png": "thesis-deck-system/artifacts/phase2/fishbone/FB001-rev2.png",
    },
    "thesis-deck-system/artifacts/phase3/planner-composition-candidate-review.pptx": {},
}


def _final_source_closure(root: Path, relative_path: str, producer_id: str, direct_inputs: tuple[str, ...]) -> tuple[dict[str, Any], dict[str, str], tuple[Path, ...]]:
    """Build exact direct-input and package-media closure for one fixed output."""
    media_paths = _FINAL_GENERATED_PPTX_MEDIA_SOURCES[relative_path]
    declared: dict[str, str] = {path: "direct_build_input" for path in direct_inputs}
    declared.update({path: "media_source" for path in media_paths.values()})
    entries: list[dict[str, Any]] = []
    path_to_id: dict[str, str] = {}
    for index, (path, input_role) in enumerate(sorted(declared.items()), start=1):
        input_id = f"SRC-{index:03d}"
        path_to_id[path] = input_id
        entries.append({
            "input_id": input_id,
            "repository_relative_path": path,
            "input_class": "generated_artifact" if path.endswith(".pptx") else "repository_input",
            "producer_id": producer_id,
            "input_role": input_role,
            "source_kind": "repository_sanitized",
            "privacy_status": "sanitized",
        })
    closure = build_generated_source_closure(root, entries)
    media_sources = {part: path_to_id[path] for part, path in media_paths.items()}
    declared_paths = tuple(root / path for path in declared)
    return closure, media_sources, declared_paths


def build_final_generated_pptx_evidence_bundle(root: Path, *, candidate_state_hash: str, privacy_scanner: Any, execution_id: str) -> dict[str, Any]:
    """Build exact final-output attestations plus their closure provenance.

    This is intentionally not a generic PPTX allowlist: each path must be
    produced by its registered builder, hash-bound to the frozen candidate and
    pass independent package/privacy inspection.
    """
    root = Path(root).resolve()
    producers = {
        "phase2-acceptance-builder": root / "packages/thesis-deck-system/src/thesis_deck_system/phase2_build.py",
        "sanitized-template-builder": root / "packages/thesis-deck-system/src/thesis_deck_system/template.py",
        "final-composition-builder": root / "packages/thesis-deck-system/src/thesis_deck_system/phase3_final_visual_composition.py",
        "presentation-planner-application-builder": root / "packages/thesis-deck-system/src/thesis_deck_system/presentation_planner_application.py",
    }
    contracts = {path: (artifact_class, producer) for path, (artifact_class, producer, _) in _FINAL_GENERATED_PPTX_CONTRACTS.items()}
    adjudicator = GeneratedArtifactAdjudicator(root=root, candidate_state_hash=candidate_state_hash, approved_producers=producers, generated_contracts=contracts, privacy_scanner=privacy_scanner)
    records: list[dict[str, Any]] = []
    source_closures: dict[str, dict[str, Any]] = {}
    media_lineages: dict[str, dict[str, Any]] = {}
    for relative_path, (artifact_class, producer, inputs) in _FINAL_GENERATED_PPTX_CONTRACTS.items():
        source_closure, media_sources, declared_paths = _final_source_closure(root, relative_path, producer, inputs)
        media_lineage = build_package_media_lineage(root / relative_path, source_closure["input_records"], media_sources)
        source_closures[relative_path] = source_closure
        media_lineages[relative_path] = media_lineage
        records.append(adjudicator.attest_staged_generated_pptx(
            root / relative_path,
            artifact_class=artifact_class,
            producer_id=producer,
            declared_input_paths=declared_paths,
            execution_id=execution_id,
            source_closure=source_closure,
            media_lineage=media_lineage,
        ))
    return {
        "adjudicator": adjudicator,
        "attestations": records,
        "source_closures": source_closures,
        "media_lineages": media_lineages,
    }


def attest_final_generated_pptx_set(root: Path, *, candidate_state_hash: str, privacy_scanner: Any, execution_id: str) -> list[dict[str, Any]]:
    """Compatibility projection for callers that only need final attestations."""
    return build_final_generated_pptx_evidence_bundle(
        root,
        candidate_state_hash=candidate_state_hash,
        privacy_scanner=privacy_scanner,
        execution_id=execution_id,
    )["attestations"]


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
        exit_status_path = self.evidence_root / f"{run_id}.exit-status.txt"
        record_path = self.evidence_root / f"{run_id}.json"
        record = {"run_id": run_id, "tier": tier, "command": command, "head": self._git("rev-parse", "HEAD"), "candidate_hash_pre": self.candidate_hash(), "started_at": datetime.now(timezone.utc).isoformat(), "stdout_path": str(stdout_path), "stderr_path": str(stderr_path), "exit_status_path": str(exit_status_path), "completion_status": "running"}
        record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
            completed = subprocess.run(command, cwd=self.root, stdout=stdout, stderr=stderr, check=False, text=True)
        exit_status_path.write_text(f"{completed.returncode}\n", encoding="utf-8")
        output = stdout_path.read_text(encoding="utf-8")
        passed_match = re.search(r"(?<!\d)(\d+) passed\b", output)
        failed_match = re.search(r"(?<!\d)(\d+) failed\b", output)
        record.update({"exit_code": completed.returncode, "passed": int(passed_match.group(1)) if passed_match else 0, "failed": int(failed_match.group(1)) if failed_match else 0, "candidate_hash_post": self.candidate_hash(), "ended_at": datetime.now(timezone.utc).isoformat(), "completion_status": "completed"})
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


def build_final_evidence_facts(
    *,
    candidate_state_hash: str,
    focused: dict[str, Any],
    figure_audit: dict[str, Any],
    incremental_audit: dict[str, Any],
    privacy: dict[str, Any],
) -> dict[str, Any]:
    """Unify final closure facts without allowing stale evidence to certify it."""
    checks = [
        (
            "FEC-05-FOCUSED-CANDIDATE",
            focused.get("candidate_hash_pre") == candidate_state_hash
            and focused.get("candidate_hash_post") == candidate_state_hash
            and focused.get("exit_code") == 0
            and focused.get("failed") == 0,
            {key: focused.get(key) for key in ("candidate_hash_pre", "candidate_hash_post", "exit_code", "passed", "failed")},
        ),
        (
            "FEC-03-FIGURE-BINDING",
            all(figure_audit.get(key) == 0 for key in (
                "route_only_representative_final_figure_count", "unbound_scientific_figure_count",
                "scientific_input_mismatch_count", "unapproved_figure_bypass_count", "native_mismatch_count",
                "untruthful_vector_fallback_count",
            )),
            {key: figure_audit.get(key) for key in (
                "route_only_representative_final_figure_count", "unbound_scientific_figure_count",
                "scientific_input_mismatch_count", "unapproved_figure_bypass_count", "native_mismatch_count",
                "untruthful_vector_fallback_count",
            )},
        ),
        (
            "IDL-MIXED-GENERATION",
            incremental_audit.get("stale_mixed_generation_slide_count") == 0
            and incremental_audit.get("shell_override_by_body_reference_count") == 0,
            {key: incremental_audit.get(key) for key in ("stale_mixed_generation_slide_count", "shell_override_by_body_reference_count")},
        ),
        (
            "FEC-01-02-PRIVACY-ATTESTATION",
            privacy.get("unexcepted_final_finding_count") == 0
            and privacy.get("attested_generated_pptx_count") == privacy.get("raw_pptx_candidate_count"),
            {key: privacy.get(key) for key in ("unexcepted_final_finding_count", "attested_generated_pptx_count", "raw_pptx_candidate_count")},
        ),
    ]
    owning_checks = [
        {"check_id": check_id, "status": "pass" if passed else "fail", "facts": facts, "facts_sha256": _canonical_hash(facts)}
        for check_id, passed, facts in checks
    ]
    return {
        "evidence_facts_id": "FEC-CURRENT-FACTS-001",
        "candidate_state_hash": candidate_state_hash,
        "focused_test_count": focused.get("passed"),
        "figure_binding_count": figure_audit.get("governed_figure_placement_count"),
        "aggregate_status": "pass" if all(check["status"] == "pass" for check in owning_checks) else "fail",
        "owning_checks": owning_checks,
    }
