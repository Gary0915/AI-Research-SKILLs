"""Backend-neutral deterministic Slide Specs for the Phase 1 recipes."""

from __future__ import annotations


RECIPES = {
    "photo_observation": {"native_layout_role": "photo_observation", "allowed_assets": ["observation_photo", "microscopy_image"], "text_budget": 180, "citation_zone": "footer", "speaker_note": True, "failure": "split_or_block"},
    "hero_plot_discussion": {"native_layout_role": "hero_plot_discussion", "allowed_assets": ["data_plot"], "text_budget": 220, "citation_zone": "footer", "speaker_note": True, "failure": "split_or_block"},
}


def compile_slide(block_id: str, stage: str, recipe: str, source_cursor: int, *, revision: int = 1, content: dict | None = None, asset_path: str | None = None, asset_id: str = "A001") -> dict:
    if recipe not in RECIPES:
        raise ValueError(f"unknown recipe: {recipe}")
    if stage not in {"observation", "result", "discussion"}:
        raise ValueError(f"unsupported slide stage: {stage}")
    config = RECIPES[recipe]
    content = content or {}
    placement = {"slot": "hero_visual", "asset_id": asset_id}
    if asset_path: placement["asset_path"] = asset_path
    return {
        "schema_version": "1.0.0", "slide_id": f"S-{block_id}-{stage.upper()}-01", "revision": revision,
        "deck_role": "research_block", "block_refs": [{"block_id": block_id, "revision": revision}], "stage": stage,
        "native_layout_role": config["native_layout_role"], "recipe": recipe,
        "title": {"text": content.get("title", "Synthetic observation" if recipe == "photo_observation" else "Synthetic results"), "assertion_claim_refs": ["C001"]},
        "placements": [placement], "citations": [],
        "speaker_notes": {"source_refs": content.get("evidence_refs", ["E001"]), "text": "Synthetic fixture — verify evidence provenance."},
        "story_visibility": {"master": "main", "meeting": "main", "defense": "appendix"}, "source_cursor": source_cursor,
        "bindings": {"claim_refs": content.get("claim_refs", ["C001"]), "evidence_refs": content.get("evidence_refs", ["E001"]), "asset_refs": [asset_id], "action_refs": ["NS001"], "professor_profile_ref": {"profile_id": "PROF-SYNTH-001", "version": "1.0.0"}, "template_profile_ref": {"profile_id": "TP-SYNTH-001", "version": "1.0.0"}},
        "content": content,
    }
