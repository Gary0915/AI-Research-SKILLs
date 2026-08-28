"""Synthetic-only Phase 3 Checkpoint 1 contract and privacy tests."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess

import pytest

from thesis_deck_system.contracts import SchemaRegistry
from thesis_deck_system.concept_images import validate_concept_provider
from thesis_deck_system.image_review import preflight_image_review
from thesis_deck_system.phase3_contracts import (
    validate_fabrication_process,
    validate_observation_visual_binding,
    validate_skill_routing,
)
from thesis_deck_system.phase3_checkpoint import checkpoint1_qa_record, write_checkpoint1_qa
from thesis_deck_system.phase3_privacy import (
    PrivacyViolation,
    PrivateProfileStore,
    RepositoryPrivacyScanner,
    sanitize_profile,
)


ROOT = Path(__file__).resolve().parents[4]
SCHEMA_DIR = ROOT / "thesis-deck-system" / "schemas"
SHA = "a" * 64


def _registry() -> SchemaRegistry:
    return SchemaRegistry(SCHEMA_DIR, include_phase3=True)


def _provider(**changes: object) -> dict:
    value = {
        "provider_id": "synthetic_image_reviewer",
        "image_capable": True,
        "hash_binding_supported": True,
        "private_content_allowed": True,
        "approved_for_private_exemplars": True,
        "egress_mode": "local_only",
        "retention_class": "ephemeral",
        "supported_input_forms": ["repository_relative_path", "local_private_handle"],
    }
    value.update(changes)
    return value


def _figure_manifest(figure_type: str, artifact_kind: str, artifact: dict) -> dict:
    return {
        "schema_version": "3.0.0",
        "figure_output_id": "FOM001",
        "figure_id": "FIG001",
        "figure_type": figure_type,
        "primary_artifact_kind": artifact_kind,
        "renderer": "synthetic_renderer",
        "source_spec_sha256": SHA,
        "provenance_refs": ["E001"],
        "style_profile_ref": "VSP001",
        "evidence_status": (
            "empirical" if figure_type == "real_photo" else
            "literature_evidence" if figure_type == "literature_figure" else
            "synthetic_test_evidence" if figure_type == "scientific_plot" else
            "non_evidence"
        ),
        "primary_artifact": artifact,
        "output_part_lineage": [{
            "real_photo": "source_evidence",
            "literature_figure": "extracted_source",
            "native_shape_figure": "native_plan",
        }.get(figure_type, "generated")],
    }


def test_private_root_rejects_repo_root_and_symlink_before_any_source_open(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(PrivacyViolation, match="outside"):
        PrivateProfileStore(ROOT, repository_root=ROOT)
    redirect = tmp_path / "redirect"
    monkeypatch.setattr(Path, "is_symlink", lambda path: path.name == "redirect")
    with pytest.raises(PrivacyViolation, match="symlink"):
        PrivateProfileStore(redirect, repository_root=ROOT)


def test_private_root_requires_gitignore_and_untracked_status(tmp_path: Path):
    root = ROOT / ".phase3-test-unignored"
    with pytest.raises(PrivacyViolation, match="ignored"):
        PrivateProfileStore(root, repository_root=ROOT)


def test_ignored_private_root_is_valid_before_any_private_alias_operation():
    store = PrivateProfileStore(ROOT / ".private" / "phase3" / "synthetic-run", repository_root=ROOT)
    assert store.retention_policy() == {
        "root_kind": "ignored_local",
        "cleanup_required": True,
        "private_source_open_permitted": False,
    }
    prepared = store.prepare_for_future_open()
    assert prepared["writable"] is True


@pytest.mark.parametrize("payload", [
    {"path": "D:/PRIVATE_CANARY/slide.pptx"},
    {"note": "PRIVATE_TEXT_CANARY"},
    {"speaker_notes": "PRIVATE_NOTES_CANARY"},
    {"author": "PRIVATE_AUTHOR_CANARY"},
    {"company": "PRIVATE_COMPANY_CANARY"},
    {"media_name": "PRIVATE_MEDIA_CANARY"},
    {"relationship": "<Relationship Target='x'/>"},
    {"url": "https://private.example.test/record"},
])
def test_sanitizer_and_scanner_detect_synthetic_private_canaries(payload: dict):
    with pytest.raises(PrivacyViolation):
        sanitize_profile(payload)
    findings = RepositoryPrivacyScanner().scan_mapping(payload, location="synthetic.json")
    assert findings


def test_sanitizer_constructs_only_allowlisted_profile_fields_and_fails_unknown_keys():
    raw = {
        "alias_uri": "private://template_primary_1",
        "resolved_status": "resolved",
        "source_sha256": SHA,
        "sanitized_profile_id": "SP001",
        "slide_size": {"width": 13.333, "height": 7.5},
    }
    clean = sanitize_profile(raw)
    assert clean == raw
    with pytest.raises(PrivacyViolation, match="unknown"):
        sanitize_profile({**raw, "untyped_private_field": "nope"})


def test_scanner_detects_staged_private_pptx_and_render_candidates(tmp_path: Path):
    scanner = RepositoryPrivacyScanner()
    pptx = tmp_path / "PRIVATE_CANARY.pptx"
    render = tmp_path / "private-render.png"
    pptx.write_bytes(b"PK\x03\x04synthetic")
    render.write_bytes(b"\x89PNG\r\n\x1a\nsynthetic")
    findings = scanner.scan_paths([pptx, render], location_root=tmp_path)
    assert {item.classification for item in findings} >= {"private_pptx_candidate", "private_render_candidate"}


def test_repository_scanner_checks_the_actual_staged_file_list(monkeypatch: pytest.MonkeyPatch):
    def staged_git(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 0, "synthetic/PRIVATE_CANARY.pptx\nsynthetic/private-render.png\n", "")

    monkeypatch.setattr("thesis_deck_system.phase3_privacy.subprocess.run", staged_git)
    findings = RepositoryPrivacyScanner().scan_staged(ROOT)
    assert {item.classification for item in findings} == {"private_pptx_candidate", "private_render_candidate"}


def test_repository_scanner_reads_staged_text_content(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    candidate = tmp_path / "candidate.py"
    candidate.write_text("PRIVATE_AUTHOR_CANARY", encoding="utf-8")

    def staged_git(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 0, "candidate.py\n", "")

    monkeypatch.setattr("thesis_deck_system.phase3_privacy.subprocess.run", staged_git)
    findings = RepositoryPrivacyScanner().scan_staged(tmp_path)
    assert {item.classification for item in findings} == {"private_text_canary"}


def test_private_image_review_requires_full_capability_authorization():
    approved = preflight_image_review(_provider(), private_reference=True)
    assert approved.status == "approved"
    blocked = preflight_image_review(_provider(approved_for_private_exemplars=False), private_reference=True)
    assert blocked.status == "blocked_visual_review"
    assert "private authorization" in blocked.reason


def test_private_image_review_requires_an_authorized_private_input_form():
    empty = preflight_image_review(_provider(supported_input_forms=[]), private_reference=True)
    wrong = preflight_image_review(_provider(supported_input_forms=["repository_relative_path"]), private_reference=True)
    assert empty.status == "blocked_visual_review"
    assert wrong.status == "blocked_visual_review"


def test_provider_contract_schemas_are_registered_and_fail_closed():
    registry = _registry()
    assert registry.errors("image-review-provider", _provider()) == []
    assert registry.errors("image-review-provider", {**_provider(), "vendor": "forbidden"})
    assert registry.errors("concept-image-provider", {"provider_id": "synthetic_concept_provider", "image_capable": True, "generation_provenance_required": True, "allowed_evidence_statuses": ["non_evidence"]}) == []


@pytest.mark.parametrize("changes", [
    {"retention_class": "persistent"},
    {"egress_mode": "external_network"},
    {"hash_binding_supported": False},
])
def test_private_image_review_rejects_retention_egress_and_hash_failures(changes: dict):
    result = preflight_image_review(_provider(**changes), private_reference=True)
    assert result.status == "blocked_visual_review"


def test_sanitized_only_image_review_cannot_certify_private_fidelity():
    result = preflight_image_review(_provider(approved_for_private_exemplars=False), private_reference=False)
    assert result.status == "approved_sanitized_only"
    assert result.professor_fidelity_status == "blocked_visual_review"


def test_concept_provider_is_abstract_and_non_evidence_only():
    assert validate_concept_provider({
        "provider_id": "synthetic_concept_provider",
        "image_capable": True,
        "generation_provenance_required": True,
        "allowed_evidence_statuses": ["non_evidence"],
    }) == []
    errors = validate_concept_provider({
        "provider_id": "synthetic_concept_provider",
        "image_capable": True,
        "generation_provenance_required": True,
        "allowed_evidence_statuses": ["empirical"],
    })
    assert "P3-CONCEPT-EVIDENCE-STATUS" in errors


def test_figure_output_variants_validate_their_real_primary_identity():
    registry = _registry()
    cases = [
        _figure_manifest("vector_diagram", "svg_vector", {"path": "artifacts/cp1/diagram.svg", "sha256": SHA}),
        _figure_manifest("scientific_plot", "pdf_vector", {"path": "artifacts/cp1/plot.pdf", "sha256": SHA, "data_provenance_refs": ["E001"]}),
        _figure_manifest("real_photo", "source_evidence_asset", {"asset_id": "A001", "source_sha256": SHA, "evidence_card_ref": "E001"}),
        _figure_manifest("literature_figure", "extracted_source_figure", {"asset_id": "A002", "source_sha256": SHA, "evidence_card_ref": "E001", "citation_ref": "E001"}),
        _figure_manifest("native_shape_figure", "native_shape_plan", {"plan_id": "NSP001", "geometry_manifest_path": "artifacts/cp1/native.json", "geometry_manifest_sha256": SHA}),
    ]
    for value in cases:
        assert registry.errors("figure-output-manifest", value) == []


def test_figure_plan_spec_critic_and_style_contracts_reject_untyped_payloads():
    registry = _registry()
    plan = {
        "schema_version": "3.0.0", "figure_id": "FIG001", "figure_type": "vector_diagram", "scientific_purpose": "synthetic process", "evidence_status": "non_evidence", "source_refs": [], "claim_refs": [], "hypothesis_layer_ref": "H001", "research_block_refs": ["B001"], "director_skill": "fabrication-process-director", "renderer": "vector_builder", "ai_allowed": False, "source_requirement": "structured_spec", "canonical_output_kind": "svg_vector", "required_qa": ["figure_critic"], "handoff_cursor": 1,
    }
    assert registry.errors("figure-production-plan", plan) == []
    assert registry.errors("figure-production-plan", {**plan, "unknown": True})
    critic = {"schema_version": "3.0.0", "report_id": "FCR001", "figure_id": "FIG001", "output_manifest_ref": "FOM001", "executed_checks": ["provenance"], "findings": [], "status": "APPROVED_FIGURE"}
    assert registry.errors("figure-critic-report", critic) == []
    style = {"schema_version": "3.0.0", "style_profile_id": "VSP001", "status": "synthetic_checkpoint", "token_provenance": [{"token_id": "synthetic", "source_role": "synthetic_checkpoint"}], "material_tokens": {}, "arrow_tokens": {}, "emphasis_tokens": {}, "annotation_tokens": {}}
    assert registry.errors("visual-style-profile", style) == []


def test_figure_output_rejects_cross_class_masquerading_and_nonvector_plot():
    registry = _registry()
    masked = _figure_manifest("real_photo", "svg_vector", {"path": "artifacts/cp1/fake.svg", "sha256": SHA})
    raster_plot = _figure_manifest("scientific_plot", "png_preview", {"path": "artifacts/cp1/plot.png", "sha256": SHA})
    assert registry.errors("figure-output-manifest", masked)
    assert registry.errors("figure-output-manifest", raster_plot)


def test_evidence_figure_lineage_cannot_claim_generated_output():
    registry = _registry()
    photo = _figure_manifest("real_photo", "source_evidence_asset", {"asset_id": "A001", "source_sha256": SHA, "evidence_card_ref": "E001"})
    literature = _figure_manifest("literature_figure", "extracted_source_figure", {"asset_id": "A002", "source_sha256": SHA, "evidence_card_ref": "E001", "citation_ref": "E001"})
    photo["output_part_lineage"] = ["generated"]
    literature["output_part_lineage"] = ["generated"]
    assert registry.errors("figure-output-manifest", photo)
    assert registry.errors("figure-output-manifest", literature)


def test_concept_figure_is_non_evidence_and_cannot_support_scientific_claims():
    registry = _registry()
    concept = _figure_manifest("concept_illustration", "generated_non_evidence_substrate", {"asset_id": "A003", "generation_provenance_ref": "GEN001"})
    concept["evidence_status"] = "non_evidence"
    assert registry.errors("figure-output-manifest", concept) == []
    concept["evidence_status"] = "empirical"
    assert registry.errors("figure-output-manifest", concept)


def test_concept_scientific_figure_spec_cannot_be_empirical_or_claim_supporting():
    registry = _registry()
    spec = {
        "schema_version": "3.0.0", "figure_id": "FIG001", "figure_type": "concept_illustration", "scientific_purpose": "synthetic context", "evidence_status": "non_evidence", "source_refs": [], "claim_refs": [], "hypothesis_layer_ref": "H001", "research_block_refs": ["B001"], "director_skill": "concept-illustration-director", "renderer": "concept_provider", "style_profile_ref": "VSP001", "canvas": {"width": 100, "height": 100}, "components": [], "connections": [], "annotations": [], "labels": [], "visual_states": [], "provenance": {"source_cursor": 1}, "output_targets": ["generated_non_evidence_substrate"], "qa_requirements": ["provenance"],
    }
    assert registry.errors("scientific-figure-spec", spec) == []
    assert registry.errors("scientific-figure-spec", {**spec, "evidence_status": "empirical"})
    assert registry.errors("scientific-figure-spec", {**spec, "claim_refs": ["C001"]})


def test_observation_requires_real_empirical_evidence_and_keeps_concepts_auxiliary():
    valid = {
        "observation_id": "OBS001",
        "empirical_evidence_required": True,
        "observation_evidence_ref": "E001",
        "evidence_refs": ["E001"],
        "evidence_catalog": {"E001": {"origin": "experimental_photo"}},
        "auxiliary_visuals": [{"figure_id": "FIGC01", "figure_type": "concept_illustration", "evidence_status": "non_evidence"}],
    }
    assert validate_observation_visual_binding(valid) == []
    generated = {**valid, "observation_evidence_ref": "E002", "evidence_refs": ["E002"], "evidence_catalog": {"E002": {"origin": "generated_concept"}}}
    assert "P3-OBSERVATION-GENERATED-AS-EVIDENCE" in validate_observation_visual_binding(generated)
    missing = {**valid, "observation_evidence_ref": None, "evidence_refs": []}
    assert "P3-OBSERVATION-EMPIRICAL-EVIDENCE-MISSING" in validate_observation_visual_binding(missing)
    assert _registry().errors("observation-visual-binding", valid) == []


def test_fabrication_process_preserves_order_unknowns_and_provenance():
    valid = {
        "process_id": "FP001",
        "process_kind": "fabrication_process",
        "provenance_refs": ["E001"],
        "steps": [
            {"ordinal": 1, "operation": "mix", "material_refs": ["M001"], "state_before": "precursors", "state_after": "mixture", "conditions": {"temperature_c": "unknown", "duration_min": "unknown"}},
            {"ordinal": 2, "operation": "cure", "material_refs": ["M001"], "state_before": "mixture", "state_after": "gel", "conditions": {"temperature_c": 25, "duration_min": 60}},
        ],
    }
    assert validate_fabrication_process(valid) == []
    mutated = {**valid, "steps": [valid["steps"][1], valid["steps"][0]]}
    assert "P3-FABRICATION-ORDER" in validate_fabrication_process(mutated)
    no_provenance = {**valid, "provenance_refs": []}
    assert "P3-FABRICATION-PROVENANCE-MISSING" in validate_fabrication_process(no_provenance)
    assert _registry().errors("fabrication-process", valid) == []


def test_fabrication_contract_does_not_allow_mechanism_or_measurement_substitution():
    mechanism = {"process_id": "FP001", "process_kind": "mechanism_diagram", "provenance_refs": ["E001"], "steps": []}
    measurement = {"process_id": "FP001", "process_kind": "experiment_schematic", "provenance_refs": ["E001"], "steps": []}
    assert "P3-FABRICATION-KIND" in validate_fabrication_process(mechanism)
    assert "P3-FABRICATION-KIND" in validate_fabrication_process(measurement)


def test_skill_routing_requires_bounded_fabrication_specialist_not_mechanism_substitution():
    routing = {
        "schema_version": "3.0.0",
        "skills": [{
            "skill_id": "fabrication-process-director",
            "trigger": "fabrication_process",
            "output_contract": "fabrication-process",
            "forbidden_responsibilities": ["mechanism_explanation", "measurement_schematic"],
            "handoff": "figure-critic",
            "qa_owner": "provenance-qa",
        }],
        "routes": [{"request_kind": "fabrication_process", "skill_id": "fabrication-process-director", "next_skill_id": "figure-critic"}],
    }
    assert validate_skill_routing(routing) == []
    assert _registry().errors("skill-routing", routing) == []
    routing["routes"][0]["skill_id"] = "mechanism-diagram-director"
    assert "P3-SKILL-ROUTING-FABRICATION" in validate_skill_routing(routing)


def test_checkpoint_qa_contract_proves_zero_private_operations():
    record = checkpoint1_qa_record(phase1_phase2_regression_status="pass")
    assert _registry().errors("checkpoint-qa", record) == []
    record["private_source_open_attempts"] = 1
    assert _registry().errors("checkpoint-qa", record)


def test_checkpoint_qa_writer_emits_only_schema_valid_nonprivate_evidence(tmp_path: Path):
    output = tmp_path / "checkpoint-qa.json"
    record = write_checkpoint1_qa(output, phase1_phase2_regression_status="pass")
    assert output.is_file()
    assert _registry().errors("checkpoint-qa", record) == []
