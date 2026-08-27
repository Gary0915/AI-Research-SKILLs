"""Governed professor-specific archetype selection."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path


ROLE_TO_ARCHETYPE = {
    "hypothesis_title": "A01", "problem_definition": "A02", "fishbone_locator": "A03",
    "observation_problem": "A04", "literature_mechanism": "A05", "mechanism_solution": "A06",
    "photo_schematic": "A07", "control_vs_proposed": "A08", "experiment_design": "A09",
    "result_single": "A10", "result_comparison": "A11", "image_matrix": "A12",
    "hero_plot_discussion": "A13", "layer_integrated_discussion": "A14",
    "layer_summary_decision": "A15", "hypothesis_transition": "A16",
    "progress_todo": "A17", "schedule_next_step": "A18",
}

# Coordinates are inches in the 13.333 x 7.5 native content canvas.  These
# are governed contracts, not labels: every semantic role receives a distinct
# slot signature and the assembler consumes these coordinates verbatim.
ROLE_GEOMETRY = {
    "hypothesis_title": [("hypothesis_statement", .8, 1.65, 11.7, 2.35, "assertion", 1, 28)],
    "problem_definition": [("previous_finding", .8, 1.45, 3.7, 1.75, "evidence", 1, 18), ("unresolved_conflict", 4.8, 1.45, 3.7, 1.75, "problem", 2, 18), ("research_question", 8.8, 1.45, 3.7, 1.75, "question", 3, 20)],
    "fishbone_locator": [("primary_figure", 4.25, 1.35, 8.35, 4.9, "fishbone", 1, 16), ("fishbone_focus", .8, 1.65, 3.0, 1.4, "annotation", 2, 16)],
    "observation_problem": [("primary_figure", 7.55, 1.4, 5.0, 3.8, "observation_visual", 1, 16), ("research_question", .8, 1.45, 6.2, .9, "question", 2, 20), ("observation_text", .8, 2.55, 6.2, 2.65, "observation", 3, 16)],
    "photo_schematic": [("primary_figure", .8, 1.45, 7.4, 4.5, "schematic", 1, 16), ("annotation", 8.55, 1.45, 4.0, 2.1, "annotation", 2, 16)],
    "literature_mechanism": [("literature_evidence", .8, 1.45, 5.8, 3.9, "literature", 1, 16), ("mechanism_diagram", 7.0, 1.45, 5.55, 3.9, "mechanism", 2, 16)],
    "mechanism_solution": [("mechanism_diagram", .8, 1.55, 5.5, 3.5, "mechanism", 1, 16), ("strategy", 6.75, 1.55, 5.8, 3.5, "strategy", 2, 16)],
    "experiment_design": [("experiment_matrix", .8, 1.4, 7.4, 4.3, "experiment", 1, 16), ("decision_rule", 8.55, 1.4, 4.0, 2.0, "decision_rule", 2, 16)],
    "result_single": [("result_plot", 6.0, 1.35, 6.55, 4.45, "result", 1, 16), ("result_annotation", .8, 1.65, 4.8, 2.3, "annotation", 2, 16)],
    # Comparison panels remain symmetric while the registered plot and its
    # annotation occupy a governed third region.  The plot is deliberately
    # separate from the proposed text panel so an asset cannot displace the
    # scientific statement.
    "result_comparison": [("control_panel", .8, 1.45, 3.7, 4.2, "comparison_control", 1, 16), ("proposed_panel", 4.8, 1.45, 3.7, 4.2, "comparison_proposed", 2, 16), ("result_plot", 8.8, 1.45, 3.7, 4.2, "result", 3, 16)],
    "control_vs_proposed": [("control_panel", .8, 1.45, 5.75, 4.2, "comparison_control", 1, 16), ("proposed_panel", 6.8, 1.45, 5.75, 4.2, "comparison_proposed", 2, 16)],
    "image_matrix": [("matrix_grid", .8, 1.45, 11.75, 4.6, "image_matrix", 1, 16), ("matrix_annotation", .8, 6.2, 11.75, .5, "annotation", 2, 16)],
    "hero_plot_discussion": [("result_plot", 6.0, 1.35, 6.55, 4.45, "result", 1, 16), ("discussion_panel", .8, 1.65, 4.8, 3.8, "interpretation", 2, 16)],
    "layer_integrated_discussion": [("supporting_results", .8, 1.4, 5.65, 2.2, "support", 1, 16), ("contradicting_results", 6.8, 1.4, 5.75, 2.2, "contradiction", 2, 16), ("uncertainty", .8, 3.9, 11.75, 1.7, "uncertainty", 3, 16)],
    "layer_summary_decision": [("decision_status", .8, 1.4, 3.7, 2.3, "status", 1, 18), ("uncertainty", 4.8, 1.4, 3.7, 2.3, "uncertainty", 2, 16), ("next_step", 8.8, 1.4, 3.7, 2.3, "next_step", 3, 16)],
    "hypothesis_transition": [("transition_nodes", .8, 1.55, 11.75, 2.7, "transition", 1, 18), ("derivation_strip", .8, 4.55, 11.75, .8, "derivation", 2, 16)],
    "progress_todo": [("commitment_table", .8, 1.45, 7.0, 3.75, "commitment", 1, 16), ("current_position", 8.15, 1.45, 4.4, 1.7, "position", 2, 16), ("parallel_work", 8.15, 3.45, 4.4, 1.75, "parallel", 3, 16)],
    "schedule_next_step": [("timeline", .8, 1.6, 8.0, 2.5, "timeline", 1, 16), ("dependencies", 9.05, 1.6, 3.5, 2.5, "dependencies", 2, 16)],
}

ROLE_GEOMETRY["observation_literature_mechanism_strategy"] = [
    ("observation_text", .8, 1.4, 3.0, 2.1, "observation", 1, 16),
    ("research_question", .8, 3.75, 3.0, 1.55, "question", 2, 18),
    ("literature_evidence", 4.1, 1.4, 4.1, 3.9, "literature", 3, 16),
    ("mechanism_diagram", 8.5, 1.4, 2.1, 2.3, "mechanism", 4, 16),
    ("strategy", 10.8, 1.4, 1.7, 2.3, "strategy", 5, 16),
    ("primary_figure", 8.5, 3.95, 4.0, 1.35, "observation_visual", 6, 14),
]
ROLE_GEOMETRY["experiment_result_combined"] = [
    ("experiment_matrix", .8, 1.4, 5.8, 4.3, "experiment", 1, 16),
    ("decision_rule", 6.8, 1.4, 2.0, 2.0, "decision_rule", 2, 16),
    ("result_plot", 9.05, 1.4, 3.5, 2.4, "result", 3, 16),
    ("result_annotation", 6.8, 3.95, 5.75, 1.75, "annotation", 4, 16),
]
ROLE_GEOMETRY["discussion_summary_combined"] = [
    ("supporting_results", .8, 1.4, 3.0, 2.1, "support", 1, 16),
    ("contradicting_results", 4.05, 1.4, 3.0, 2.1, "contradiction", 2, 16),
    ("discussion_synthesis", 7.3, 1.4, 5.25, 2.1, "interpretation", 3, 16),
    ("uncertainty", .8, 3.8, 5.75, 1.7, "uncertainty", 4, 16),
    ("decision_status", 6.8, 3.8, 2.75, 1.7, "status", 5, 16),
    ("next_step", 9.8, 3.8, 2.75, 1.7, "next_step", 6, 16),
]


def load_archetype_registry(path: Path) -> dict:
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    return {record["archetype_id"]: record for record in records}


def validate_split_resolution(plan: dict, resolution: dict | None) -> list[str]:
    """Return split-resolution contract violations without inventing approval.

    This validator intentionally accepts only evidence that already exists at
    the resolution cursor.  A builder cannot create a reviewer identity or
    point forward to a render that has not been produced yet.
    """
    if not plan.get("split_recommendation"):
        return []
    if not resolution:
        return ["unresolved_split"]
    kind = resolution.get("resolution_type")
    if kind == "split":
        return [] if resolution.get("continuation_slide_ids") else ["split_without_continuation"]
    if kind == "automated_fit_exception":
        if resolution.get("approved_by"):
            return ["automated_fit_exception_claims_human_approval"]
        if not resolution.get("measurement_artifact") or not resolution.get("measurements_pass"):
            return ["automated_fit_exception_missing_measurements"]
        if int(resolution.get("measurement_cursor", -1)) > int(resolution.get("available_cursor", -1)):
            return ["automated_fit_exception_references_future_evidence"]
        return []
    if kind == "external_review_override":
        approval = str(resolution.get("approved_by", ""))
        artifact = str(resolution.get("approval_artifact", ""))
        if not approval or approval.lower().startswith("phase 2 synthetic") or not artifact or artifact == "none":
            return ["fabricated_external_review_override"]
        return []
    return ["unknown_split_resolution"]


class LayoutDirector:
    def __init__(self, registry: dict, template_profile: dict | None = None):
        self.registry = registry
        self.template_profile = template_profile or {}

    def select(self, request: dict) -> dict:
        role = request.get("semantic_role")
        combined_roles = set(request.get("combined_roles", []))
        if role == "hypothesis_problem_merged":
            raise ValueError("Hypothesis and Problem must remain separate")
        archetype_id = ROLE_TO_ARCHETYPE.get(role)
        if not archetype_id or archetype_id not in self.registry:
            raise ValueError(f"no governed archetype for semantic role: {role}")
        archetype = self.registry[archetype_id]
        text_units = request.get("text_units", 0)
        over_budget = text_units > archetype["text_budget"]
        role_profile = self.template_profile.get("semantic_roles", {}).get(archetype["native_layout_role"], {})
        geometry_role = role
        if {"observation_problem", "literature_mechanism", "mechanism_solution"} <= combined_roles:
            geometry_role = "observation_literature_mechanism_strategy"
        elif {"experiment_design", "result_single"} <= combined_roles:
            geometry_role = "experiment_result_combined"
        elif {"layer_integrated_discussion", "layer_summary_decision"} <= combined_roles:
            geometry_role = "discussion_summary_combined"
        placement_plan = [
            {"slot": slot, "left": left, "top": top, "width": width, "height": height, "z_order": z, "element_role": element, "font_size_pt": max(16, font)}
            for slot, left, top, width, height, element, z, font in ROLE_GEOMETRY.get(geometry_role, [("content", .7, 1.45, 12.0, 5.25, "scientific_content", 1, 16)])
        ]
        slot_signature = "|".join(f"{item['slot']}@{item['left']:.2f},{item['top']:.2f},{item['width']:.2f},{item['height']:.2f}" for item in placement_plan)
        split = bool(over_budget and archetype["failure_policy"] == "split")
        return {
            "selected_archetype": archetype_id,
            "geometry_role": geometry_role,
            "native_template_layout": role_profile,
            "placement_plan": placement_plan,
            "figure_text_hierarchy": ["primary_figure", "interpretation", "provenance"],
            "expected_professor_checks": archetype["professor_rules"],
            "candidate_alternatives": [value for value in ("A04", "A05", "A09") if value != archetype_id and value in self.registry][:2],
            "rejection_reasons": ["text_budget_exceeded"] if over_budget else [],
            "warnings": ["text_over_budget"] if over_budget else [],
            "density_estimate": "over_budget" if over_budget else request.get("density_estimate", "medium"),
            "split_recommendation": split,
            "text_units": int(text_units),
            "text_budget": int(archetype["text_budget"]),
            "required_slots": [item["slot"] for item in placement_plan],
            "slot_signature": slot_signature,
            "rationale": f"Deterministic semantic-role mapping {role} → {archetype_id}; governed slot geometry selected from ROLE_GEOMETRY",
        }
