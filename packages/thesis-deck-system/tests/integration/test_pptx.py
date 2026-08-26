from pathlib import Path

from thesis_deck_system.pptx import PythonPptxAssembler, audit_pptx
from thesis_deck_system.slides import compile_slide
from thesis_deck_system.template import create_synthetic_template


def test_python_backend_preserves_native_layout_and_editable_content(tmp_path: Path):
    template = create_synthetic_template(tmp_path / "template.pptx")
    output = tmp_path / "deck.pptx"
    result = PythonPptxAssembler().assemble(template, [compile_slide("B001", "observation", "photo_observation", 1), compile_slide("B001", "result", "hero_plot_discussion", 1)], output)
    assert result.output_path == output
    report = audit_pptx(output)
    assert report["slide_count"] == 4
    assert report["has_editable_text"] is True
    assert report["orphan_parts"] == []
