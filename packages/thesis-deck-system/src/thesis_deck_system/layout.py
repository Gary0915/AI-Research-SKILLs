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


def load_archetype_registry(path: Path) -> dict:
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    return {record["archetype_id"]: record for record in records}


class LayoutDirector:
    def __init__(self, registry: dict, template_profile: dict | None = None):
        self.registry = registry
        self.template_profile = template_profile or {}

    def select(self, request: dict) -> dict:
        role = request.get("semantic_role")
        if role == "hypothesis_problem_merged":
            raise ValueError("Hypothesis and Problem must remain separate")
        archetype_id = ROLE_TO_ARCHETYPE.get(role)
        if not archetype_id or archetype_id not in self.registry:
            raise ValueError(f"no governed archetype for semantic role: {role}")
        archetype = self.registry[archetype_id]
        text_units = request.get("text_units", 0)
        over_budget = text_units > archetype["text_budget"]
        role_profile = self.template_profile.get("semantic_roles", {}).get(archetype["native_layout_role"], {})
        placement_plan = [{"slot": "content", "left": 0.7, "top": 1.45, "width": 12.0, "height": 5.25, "z_order": 1, "element_role": "scientific_content", "font_size_pt": max(16, archetype["zh_tw_typography"]["minimum_font_pt"])}]
        return {
            "selected_archetype": archetype_id,
            "native_template_layout": role_profile,
            "placement_plan": placement_plan,
            "figure_text_hierarchy": ["primary_figure", "interpretation", "provenance"],
            "expected_professor_checks": archetype["professor_rules"],
            "candidate_alternatives": [],
            "rejection_reasons": [],
            "warnings": ["text_over_budget"] if over_budget else [],
            "density_estimate": "over_budget" if over_budget else request.get("density_estimate", "medium"),
            "split_recommendation": bool(over_budget and archetype["failure_policy"] == "split"),
            "rationale": f"Deterministic semantic-role mapping {role} → {archetype_id}",
        }
