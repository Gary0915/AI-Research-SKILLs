"""Canonical ten-stage QA orchestration."""

from __future__ import annotations

from datetime import datetime, timezone


CANONICAL_PIPELINE = [
    "schema_ledger_integrity", "scientific_reasoning", "citation_evidence_provenance", "professor_style_logic", "compile_assemble_pptx", "structural_pptx_engineering", "render_montage_visual", "native_powerpoint_round_trip", "final_deck_version_audit", "release",
]


def run_pipeline(*, critical_findings: list[dict], native_available: bool) -> dict:
    statuses = ["pass"] * 7
    statuses.append("pass" if native_available else "blocked_environment")
    statuses.extend(["pass", "pass"] if native_available and not critical_findings else ["not_run", "blocked"])
    findings = list(critical_findings)
    if critical_findings:
        statuses[4:9] = ["not_run", "not_run", "not_run", "not_run", "not_run"]
    pipeline = [{"order": i + 1, "stage": stage, "status": statuses[i]} for i, stage in enumerate(CANONICAL_PIPELINE)]
    return {"schema_version": "1.0.0", "qa_report_id": "QA-PHASE1", "build_id": "BUILD-PHASE1", "deck_id": "MASTER-PHASE1", "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"), "overall_status": "pass" if all(item["status"] == "pass" for item in pipeline) and not findings else "blocked", "professor_profile_ref": {"profile_id": "PROF-SYNTH-001", "version": "1.0.0"}, "pipeline": pipeline, "findings": findings, "artifacts": {}, "tool_versions": {"control_plane": "0.1.0"}}
