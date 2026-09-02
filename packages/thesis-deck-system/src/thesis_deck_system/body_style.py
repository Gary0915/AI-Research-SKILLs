"""Thesis-owned body visual treatments, separate from scientific content."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .incremental_deck_lineage import BODY_COMPOSITION_FAMILIES


_THEME_ROLES = frozenset({
    "background", "foreground", "muted", "border", "caption_background",
    "accent_primary", "focus", "warning", "measurement_reference",
})


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def build_spacing_scale() -> dict[str, Any]:
    """System-owned spacing tokens; values are not professor measurements."""
    return {
        "schema_version": "1.0.0", "spacing_scale_id": "PSS-001", "evidence_status": "synthetic_system_owned",
        "tokens": {
            "shell_title_gap": 0.18, "region_gap": 0.16, "panel_gap": 0.12,
            "figure_caption_gap": 0.06, "caption_to_next_content_gap": 0.12,
            "table_cell_padding": 0.06, "text_box_margin": 0.04,
            "callout_padding": 0.08, "section_separation": 0.22,
        },
    }


def _style(family: str) -> dict[str, Any]:
    return {
        "body_style_recipe_id": f"BSR-{family.removeprefix('BCF-')}",
        "body_family_id": family,
        "style_recipe_version": "1.0.0",
        "spacing_scale_id": "PSS-001",
        "source_evidence_ids": ["JDP-TSMC-2026-0814-BODY"],
        "evidence_status": "body_reference_supported",
        "panel_treatment": {"color_role": "background", "border_role": "border"},
        "visual_frame_treatment": {"border_role": "border"},
        "caption_treatment": {"color_role": "caption_background", "typography_role": "caption", "spacing_token": "figure_caption_gap"},
        "citation_treatment": {"color_role": "background", "typography_role": "citation"},
        "metric_callout_treatment": {"color_role": "focus", "typography_role": "metric_primary"},
        "table_treatment": {"header_color_role": "foreground", "body_color_role": "background", "padding_token": "table_cell_padding"},
        "equation_treatment": {"color_role": "foreground", "typography_role": "formula"},
        "focus_annotation": {"color_role": "focus", "typography_role": "callout"},
        "connector_roles": {"major": "foreground", "warning": "warning", "measurement": "measurement_reference"},
        "section_divider": {"color_role": "border"},
        "supporting_context_treatment": {"color_role": "background", "typography_role": "body"},
        "hierarchy": {"primary": "primary_visual", "secondary": "secondary_visual", "supporting": "compact_context", "caption": "caption", "metric": "metric_callout", "decision": "decision_callout"},
    }


def validate_body_style_recipe(recipe: dict[str, Any]) -> dict[str, Any]:
    """Fail closed on raw color payloads or unknown semantic theme roles."""
    if not isinstance(recipe, dict) or not isinstance(recipe.get("body_style_recipe_id"), str):
        raise ValueError("body style recipe has no stable identity")
    if recipe.get("body_family_id") not in BODY_COMPOSITION_FAMILIES:
        raise ValueError("unknown body family")
    if recipe.get("spacing_scale_id") != "PSS-001":
        raise ValueError("uncontrolled spacing scale")

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            if "rgb" in value or "hex" in value or "color" in value and value.get("color") not in _THEME_ROLES:
                raise ValueError("uncontrolled body-style color literal")
            for key, nested in value.items():
                if key.endswith("_role") and key not in {"typography_role", "presentation_role"} and isinstance(nested, str) and nested not in _THEME_ROLES:
                    raise ValueError("unknown semantic theme role")
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    walk(recipe)
    return recipe


def build_body_style_recipe_registry(root: Path) -> list[dict[str, Any]]:
    """Return one controlled treatment per existing physical body recipe."""
    Path(root).resolve()  # keeps the public API parallel to other calibration builders
    styles = [validate_body_style_recipe(_style(family)) for family in sorted(BODY_COMPOSITION_FAMILIES)]
    if {item["body_family_id"] for item in styles} != BODY_COMPOSITION_FAMILIES:
        raise ValueError("body style registry coverage drift")
    return styles


def write_body_style_artifacts(root: Path, destination: Path | None = None) -> dict[str, Path]:
    root = Path(root).resolve()
    destination = Path(destination or root / "thesis-deck-system/artifacts/phase3")
    destination.mkdir(parents=True, exist_ok=True)
    spacing = build_spacing_scale()
    styles = build_body_style_recipe_registry(root)
    spacing_path = destination / "spacing-scale.json"
    styles_path = destination / "body-style-recipe-registry.json"
    spacing_path.write_text(json.dumps(spacing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    styles_path.write_text(json.dumps({"schema_version": "1.0.0", "registry_id": "BSR-REG-001", "recipes": styles}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"spacing_scale": spacing_path, "body_style_registry": styles_path}
