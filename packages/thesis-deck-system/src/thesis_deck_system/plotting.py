"""Reproducible synthetic quantitative plotting."""

from __future__ import annotations

import hashlib
from pathlib import Path
import csv
import json

import matplotlib.pyplot as plt


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_plot(csv_path: Path, output_dir: Path) -> dict:
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8", newline="")))
    positions = ["center", "mid_radius", "edge"]
    values = {position: [float(row["defect_density_count_per_mm2"]) for row in rows if row["position"] == position] for position in positions}
    means = [sum(values[position]) / len(values[position]) for position in positions]
    errors = [(sum((value - means[index]) ** 2 for value in values[position]) / (len(values[position]) - 1)) ** 0.5 for index, position in enumerate(positions)]
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.2, 4.0), constrained_layout=True)
    ax.bar(positions, means, yerr=errors, capsize=4, color="#4472C4", edgecolor="#1F1F1F")
    ax.set_ylabel("Defect density (count/mm²)")
    ax.set_xlabel("Synthetic sample position")
    ax.set_title("Synthetic fixture: positional defect density")
    ax.grid(axis="y", alpha=0.25)
    svg = output_dir / "B001_defect_density.svg"
    png = output_dir / "B001_defect_density.png"
    fig.savefig(svg, format="svg")
    fig.savefig(png, format="png", dpi=180)
    plt.close(fig)
    manifest = {
        "schema_version": "1.0.0", "asset_id": "A001", "asset_type": "data_plot",
        "title": "Synthetic positional defect density", "evidence_role": "synthetic_test_evidence",
        "source_evidence": ["E001"], "path": svg.as_posix(), "preview_path": png.as_posix(),
        "mime_type": "image/svg+xml", "sha256": sha256(svg), "editable": True,
        "generator": {"kind": "matplotlib", "script": "plot.py", "version": plt.matplotlib.__version__},
        "transform_chain": [{"input_sha256": sha256(csv_path), "operation": "mean and sample SD by position", "output_sha256": sha256(svg)}],
        "provenance": "synthetic_fixture", "license_or_usage": "synthetic_test_only", "accessibility": {"alt_text": "Synthetic edge mean exceeds center mean with sample standard deviation error bars."}, "status": "approved",
    }
    (output_dir / "A001.asset.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"means": means, "sample_sd": errors, "svg": svg, "png": png, "manifest": manifest}

