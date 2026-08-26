from pathlib import Path

from thesis_deck_system.template import profile_template


def test_template_profile_records_native_structure(tmp_path: Path):
    pptx_path = tmp_path / "synthetic_native_template.pptx"
    from thesis_deck_system.template import create_synthetic_template
    create_synthetic_template(pptx_path)
    profile = profile_template(pptx_path, tmp_path / "template-profile.json")
    assert profile["slide_size"]["aspect_ratio"] == "16:9"
    assert len(profile["masters"]) >= 1
    assert len(profile["layouts"]) >= 2
    assert set(["photo_observation", "hero_plot_discussion"]) <= set(profile["semantic_roles"])
    assert len(profile["source_sha256"]) == 64

