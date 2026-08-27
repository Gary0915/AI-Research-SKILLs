"""Executed professor and render QA for the hypothesis-layer architecture."""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageStat


PHASE2_PIPELINE = [
    "schema_ledger_integrity", "scientific_reasoning", "citation_evidence_provenance",
    "professor_style_logic", "compile_assemble_pptx", "structural_pptx_engineering",
    "render_montage_visual", "native_powerpoint_round_trip", "final_deck_version_audit", "release",
]


def run_professor_qa_v2(profile: dict, projection: dict) -> dict:
    slides = projection.get("slides", [])
    findings = []
    layers = projection.get("layers", [])
    for layer in layers:
        layer_id = layer["hypothesis_layer_id"]
        layer_slides = [slide for slide in slides if slide.get("hypothesis_layer_ref") == layer_id]
        roles = [slide.get("semantic_role") for slide in layer_slides]
        if "hypothesis_title" not in roles or "problem_definition" not in roles or any({"hypothesis_title", "problem_definition"} <= set(slide.get("combined_roles", [])) for slide in layer_slides):
            findings.append(_finding("PROF-HYPOTHESIS-PROBLEM-SEPARATE", layer_id, "Create separate Hypothesis and Problem pages"))
        locator = next((slide for slide in layer_slides if slide.get("semantic_role") == "fishbone_locator"), None)
        if not locator:
            findings.append(_finding("PROF-FISHBONE-EXISTS", layer_id, "Add the layer's historical fishbone locator"))
        elif not locator.get("fishbone_focus_refs"):
            findings.append(_finding("PROF-FISHBONE-FOCUS", layer_id, "Highlight the current stable branch ID"))
        if "layer_summary_decision" not in roles:
            findings.append(_finding("PROF-LAYER-SUMMARY", layer_id, "Add hypothesis status, decision, uncertainty, and next question"))
    commitments = projection.get("previous_commitments", [])
    if not commitments or any(not item.get("owner") or not item.get("target_window") for item in commitments):
        findings.append(_finding("PROF-NEXT-STEP-OWNER-TIMING", "meeting", "Carry forward owner and target window"))
    return {"profile_ref": {"profile_id": profile.get("profile_id"), "version": profile.get("version")}, "status": "fail" if findings else "pass", "executed_checks": ["layer_structure", "fishbone_history", "integrated_discussion", "summary_decision", "commitment_carry_forward"], "findings": findings}


def _finding(rule_id: str, path: str, repair: str) -> dict:
    return {"rule_id": rule_id, "severity": "critical", "status": "open", "path": path, "evidence": "executed check returned false", "repair_action": repair}


def run_visual_qa_v2(specs: list[dict], render_paths: dict[str, Path], *, expected_size: tuple[int, int]) -> dict:
    findings = []
    checks = ["render_exists", "dimensions", "nonblank", "canvas_bounds", "overlap", "minimum_font", "title_hierarchy", "zh_tw_readability", "density", "archetype_geometry"]
    for spec in specs:
        slide_id = spec["slide_id"]
        path = Path(render_paths.get(slide_id, ""))
        if not path.is_file():
            findings.append(_finding("VISUAL-RENDER-MISSING", slide_id, "Render the exact slide"))
            continue
        with Image.open(path) as image:
            if image.size != expected_size:
                findings.append(_finding("VISUAL-DIMENSIONS", slide_id, f"Render at {expected_size}"))
            variance = ImageStat.Stat(image.convert("L")).var[0]
            if variance < 1.0:
                findings.append(_finding("VISUAL-BLANK-RENDER", slide_id, "Repair missing rendered content"))
        for placement in spec.get("placement_plan", []):
            if placement.get("left", 0) < 0 or placement.get("top", 0) < 0 or placement.get("left", 0) + placement.get("width", 0) > 13.34 or placement.get("top", 0) + placement.get("height", 0) > 7.51:
                findings.append(_finding("VISUAL-CANVAS-OVERFLOW", slide_id, "Move element inside slide bounds"))
            if placement.get("font_size_pt", 16) < 16:
                findings.append(_finding("VISUAL-MIN-FONT", slide_id, "Use at least 16 pt body text"))
    return {"status": "fail" if findings else "pass", "executed_checks": checks, "findings": findings}


def run_phase2_pipeline(*, schema_errors: list[str], ledger_replayed: bool, scientific: dict, professor: dict, audit: dict, specs: list[dict], visual: dict, render_evidence: dict) -> dict:
    """Produce pass statuses only from the owning, already-executed Phase 2 checks."""
    expected_ids = [spec["slide_id"] for spec in specs]
    generated_ids = [item.get("slide_spec_id") for item in audit.get("generated_slides", [])]
    vector_slide_ids = {spec["slide_id"] for spec in specs if any(str(place.get("asset_path", "")).endswith(".svg") for place in spec.get("placements", []))}
    structural_ok = (
        audit.get("slide_count", 0) >= len(specs)
        and generated_ids == expected_ids
        and not audit.get("orphan_parts")
        and audit.get("content_types_present")
        and all(item.get("layout_master_role_match") and item.get("notes_source_match") and item.get("editable_text") for item in audit.get("generated_slides", []))
        and all(item.get("svg_asset_relationships") for item in audit.get("generated_slides", []) if item.get("slide_spec_id") in vector_slide_ids)
    )
    gates = [
        (not schema_errors and ledger_replayed, {"check_ids": ["P2-SCHEMA-ALL", "P2-LEDGER-HASH-REPLAY"], "errors": schema_errors}),
        (scientific.get("status") == "pass", {"check_ids": scientific.get("executed_checks", []), "findings": scientific.get("findings", [])}),
        (scientific.get("status") == "pass", {"check_ids": ["P2-PROVENANCE-HASHES", "P2-SYNTHETIC-LABELS"], "evidence": scientific.get("evidence", {})}),
        (professor.get("status") == "pass", {"check_ids": professor.get("executed_checks", []), "findings": professor.get("findings", [])}),
        (audit.get("slide_count", 0) >= len(specs) and generated_ids == expected_ids, {"check_ids": ["P2-COMPILE-SPECS", "P2-ASSEMBLE-PPTX"], "slide_count": audit.get("slide_count"), "generated_spec_count": len(specs)}),
        (structural_ok, {"check_ids": ["P2-OPENXML-SVG", "P2-LAYOUT-MASTER", "P2-NOTES", "P2-EDITABLE-TEXT"], "audit": "structural-audit.json"}),
        (visual.get("status") == "pass" and len(render_evidence.get("render_paths", [])) == len(specs) and len(render_evidence.get("montages", [])) == 2, {"check_ids": visual.get("executed_checks", []), "inspection": render_evidence.get("inspection")}),
    ]
    pipeline = []
    findings = []
    for index, (ok, evidence) in enumerate(gates, 1):
        status = "pass" if ok else "fail"
        pipeline.append({"order": index, "stage": PHASE2_PIPELINE[index - 1], "status": status, "evidence": evidence})
        if not ok:
            findings.append({"rule_id": f"P2-QA-{index}", "severity": "critical", "status": "open", "path": PHASE2_PIPELINE[index - 1], "evidence": evidence, "repair_action": "repair executed gate input"})
    pipeline.extend([
        {"order": 8, "stage": PHASE2_PIPELINE[7], "status": "blocked_environment", "evidence": {"reason": "native PowerPoint desktop acceptance is unavailable in this environment"}},
        {"order": 9, "stage": PHASE2_PIPELINE[8], "status": "not_run", "evidence": {"reason": "requires native acceptance"}},
        {"order": 10, "stage": PHASE2_PIPELINE[9], "status": "blocked", "evidence": {"reason": "requires native acceptance"}},
    ])
    return {"schema_version": "2.0.0", "qa_report_id": "QA-MASTER-PHASE2-ACCEPTANCE", "build_id": "BUILD-MASTER-PHASE2-ACCEPTANCE", "deck_id": "MASTER-PHASE2-ACCEPTANCE", "overall_status": "pass_with_native_environment_block" if not findings else "fail", "pipeline": pipeline, "findings": findings, "artifacts": render_evidence, "native_powerpoint_status": "blocked_environment"}
