from pathlib import Path

from thesis_deck_system.plotting import build_plot


def test_synthetic_plot_has_registered_lineage_and_expected_gradient(tmp_path: Path):
    csv_path = tmp_path / "measurements.csv"
    csv_path.write_text("condition,position,replicate_id,defect_density_count_per_mm2\nsynthetic,center,R1,1.0\nsynthetic,center,R2,1.2\nsynthetic,center,R3,0.8\nsynthetic,mid_radius,R1,2.0\nsynthetic,mid_radius,R2,2.1\nsynthetic,mid_radius,R3,1.9\nsynthetic,edge,R1,3.1\nsynthetic,edge,R2,3.0\nsynthetic,edge,R3,3.2\n", encoding="utf-8")
    result = build_plot(csv_path, tmp_path / "plots")
    assert result["means"][2] > result["means"][0]
    assert result["svg"].exists() and result["png"].exists()
    assert len(result["manifest"]["sha256"]) == 64
    assert result["manifest"]["transform_chain"][0]["input_sha256"]

