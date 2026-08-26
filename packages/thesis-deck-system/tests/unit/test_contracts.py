from copy import deepcopy
from pathlib import Path

import pytest

from thesis_deck_system.contracts import (
    REQUIRED_SCHEMA_NAMES,
    SchemaRegistry,
    semantic_findings,
)


REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_DIR = REPO_ROOT / "thesis-deck-system" / "schemas"


def valid_bundle() -> dict:
    return {
        "research_blocks": [{
            "schema_version": "1.0.0",
            "block_id": "B001",
            "revision": 1,
            "title": "Synthetic block",
            "research_question": {"question_id": "RQ-B001", "text": "Does synthetic treatment vary by position?", "scope": "Synthetic fixture only"},
            "problem_statement": "A synthetic positional effect requires a controlled test.",
            "research_status": "active",
            "story_visibility": {"master": "main", "meeting": "main", "defense": "appendix"},
            "hypothesis_claim_refs": ["C001"],
            "mechanism_claim_refs": ["C002"],
            "prediction_claim_refs": ["C003"],
            "stage_refs": {"observation": "ST-OBS", "literature": "ST-LIT", "mechanism": "ST-MECH", "solution": "ST-SOL", "experiment": "ST-EXP", "result": "ST-RES", "discussion": "ST-DISC", "next_step": "NS001"},
            "claim_refs": ["C001", "C002", "C003"],
            "evidence_refs": ["E001"],
            "asset_refs": ["A001"],
            "action_item_refs": ["NS001"],
            "decision_refs": ["D001"],
            "decision_criteria_ref": "ST-EXP#/data/decision_rules",
            "provenance": "synthetic_fixture",
            "created_at": "2026-08-27T00:00:00Z",
            "updated_at": "2026-08-27T00:00:00Z",
        }],
        "claims": [{
            "schema_version": "1.0.0", "claim_id": "C001", "revision": 1,
            "claim_type": "hypothesis", "text": "Synthetic treatment produces a positional gradient.",
            "block_ref": {"block_id": "B001", "revision": 1}, "stage": "mechanism",
            "scope": {"population": "synthetic samples", "conditions": "fixture", "exclusions": []},
            "epistemic_status": "testing", "confidence": {"level": "medium", "rationale": "Synthetic test"},
            "evidence_support_refs": [], "evidence_contradict_refs": [], "assumptions": ["Position is controlled"],
            "falsifiable_predictions": [{"prediction_claim_ref": "C003", "observation_that_falsifies": "No positional gradient"}],
            "discriminating_evidence_requirements": [{"requirement_id": "REQ001", "description": "Controlled position comparison"}],
            "provenance": "synthetic_fixture", "supersedes": [], "superseded_by": [],
            "created_at": "2026-08-27T00:00:00Z", "updated_at": "2026-08-27T00:00:00Z",
        }, {
            "schema_version": "1.0.0", "claim_id": "C002", "revision": 1,
            "claim_type": "mechanism", "text": "Synthetic transport differs by position.",
            "block_ref": {"block_id": "B001", "revision": 1}, "stage": "mechanism",
            "scope": {"population": "synthetic samples", "conditions": "fixture", "exclusions": []},
            "epistemic_status": "testing", "confidence": {"level": "low", "rationale": "Synthetic test"},
            "evidence_support_refs": [], "evidence_contradict_refs": [], "assumptions": ["Transport proxy is valid"],
            "falsifiable_predictions": [{"prediction_claim_ref": "C003", "observation_that_falsifies": "No positional gradient"}],
            "discriminating_evidence_requirements": [{"requirement_id": "REQ001", "description": "Controlled position comparison"}],
            "provenance": "synthetic_fixture", "supersedes": [], "superseded_by": [],
            "created_at": "2026-08-27T00:00:00Z", "updated_at": "2026-08-27T00:00:00Z",
        }, {
            "schema_version": "1.0.0", "claim_id": "C003", "revision": 1,
            "claim_type": "prediction", "text": "The synthetic edge mean exceeds the center mean.",
            "block_ref": {"block_id": "B001", "revision": 1}, "stage": "experiment",
            "scope": {"population": "synthetic samples", "conditions": "fixture", "exclusions": []},
            "epistemic_status": "testing", "confidence": {"level": "medium", "rationale": "Synthetic test"},
            "evidence_support_refs": [], "evidence_contradict_refs": [], "assumptions": [],
            "provenance": "synthetic_fixture", "supersedes": [], "superseded_by": [],
            "created_at": "2026-08-27T00:00:00Z", "updated_at": "2026-08-27T00:00:00Z",
        }],
        "stages": [], "evidence_cards": [], "assets": [], "actions": [], "decisions": [],
    }


def test_all_required_schemas_exist_and_reject_empty_objects():
    registry = SchemaRegistry(SCHEMA_DIR)
    assert set(registry.names) == set(REQUIRED_SCHEMA_NAMES)
    for name in REQUIRED_SCHEMA_NAMES:
        errors = registry.errors(name, {})
        assert errors, f"{name} accepted an arbitrary empty dictionary"


def test_dangling_claim_reference_is_reported_at_schema_ledger_gate():
    bundle = valid_bundle()
    bundle["research_blocks"][0]["claim_refs"].append("C999")
    findings = semantic_findings(bundle)
    assert ("REF-DANGLING-CLAIM", "schema_ledger_integrity") in {(f.rule_id, f.stage) for f in findings}


def test_hypothesis_requires_falsification_and_discriminating_evidence():
    bundle = valid_bundle()
    claim = deepcopy(bundle["claims"][0])
    claim.pop("falsifiable_predictions")
    claim.pop("discriminating_evidence_requirements")
    bundle["claims"][0] = claim
    findings = semantic_findings(bundle)
    assert ("SCI-HYPOTHESIS-NOT-FALSIFIABLE", "scientific_reasoning") in {(f.rule_id, f.stage) for f in findings}

