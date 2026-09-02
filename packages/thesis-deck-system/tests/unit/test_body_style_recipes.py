"""Body treatment and spacing authority tests."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def test_body_style_recipes_cover_every_existing_body_family_with_semantic_roles():
    from thesis_deck_system.body_style import build_body_style_recipe_registry, build_spacing_scale
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.incremental_deck_lineage import BODY_COMPOSITION_FAMILIES

    styles = build_body_style_recipe_registry(ROOT)
    spacing = build_spacing_scale()

    assert {item["body_family_id"] for item in styles} == BODY_COMPOSITION_FAMILIES
    assert all(item["caption_treatment"]["color_role"] == "caption_background" for item in styles)
    assert all(item["focus_annotation"]["color_role"] == "focus" for item in styles)
    assert {"shell_title_gap", "panel_gap", "figure_caption_gap", "table_cell_padding"} <= set(spacing["tokens"])
    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", schema_names=("body-style-recipe-registry", "spacing-scale"))
    registry.validate("body-style-recipe-registry", {"schema_version": "1.0.0", "registry_id": "BSR-REG-001", "recipes": styles})
    registry.validate("spacing-scale", spacing)


def test_body_style_uses_semantic_theme_roles_not_uncontrolled_rgb_literals():
    from thesis_deck_system.body_style import validate_body_style_recipe

    recipe = {
        "body_style_recipe_id": "BSR-TEST", "body_family_id": "BCF-REAL-RESULT-VALIDATION",
        "spacing_scale_id": "PSS-001", "source_evidence_ids": ["JDP-TSMC-2026-0814-BODY"],
        "caption_treatment": {"color_role": "caption_background"}, "focus_annotation": {"color_role": "focus"},
        "connector_roles": {"major": "foreground", "warning": "warning", "measurement": "measurement_reference"},
    }

    assert validate_body_style_recipe(recipe) == recipe
    recipe["caption_treatment"]["rgb"] = "FF0000"
    try:
        validate_body_style_recipe(recipe)
    except ValueError:
        pass
    else:
        raise AssertionError("body style recipe accepted an uncontrolled RGB literal")
