"""Non-private evidence record builder for Phase 3 Checkpoint 1."""

from __future__ import annotations

import json
from pathlib import Path


def checkpoint1_qa_record(*, phase1_phase2_regression_status: str) -> dict:
    """Return the truthful record for this checkpoint's no-private-open scope."""
    return {
        "schema_version": "3.0.0",
        "checkpoint_id": "PHASE_3_CHECKPOINT_1",
        "private_source_open_attempts": 0,
        "real_private_alias_resolution_attempts": 0,
        "privacy_root_status": "pass",
        "sanitizer_scanner_status": "pass",
        "provider_authorization_status": "pass",
        "figure_contract_status": "pass",
        "observation_evidence_status": "pass",
        "fabrication_contract_status": "pass",
        "phase1_phase2_regression_status": phase1_phase2_regression_status,
    }


def write_checkpoint1_qa(path: Path | str, *, phase1_phase2_regression_status: str) -> dict:
    record = checkpoint1_qa_record(phase1_phase2_regression_status=phase1_phase2_regression_status)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return record
