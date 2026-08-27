"""Generate the committed synthetic H02 contact-pressure result figure."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def build(csv_path: Path, svg_path: Path, png_path: Path) -> None:
    rows = list(csv.DictReader(Path(csv_path).read_text(encoding="utf-8").splitlines()))
    pressures = sorted({float(row["pressure_kpa"]) for row in rows})
    cv = [[float(row["signal_cv_percent"]) for row in rows if float(row["pressure_kpa"]) == pressure] for pressure in pressures]
    resistance = [[float(row["contact_resistance_ohm"]) for row in rows if float(row["pressure_kpa"]) == pressure] for pressure in pressures]
    with plt.rc_context({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False, "svg.fonttype": "none"}):
        fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.8), layout="constrained")
        for ax, values, ylabel, color in (
            (axes[0], cv, "Signal CV (%)", "#B42318"),
            (axes[1], resistance, "Contact resistance (Ω)", "#175CD3"),
        ):
            means = [np.mean(group) for group in values]
            sd = [np.std(group, ddof=1) for group in values]
            ax.errorbar(pressures, means, yerr=sd, color=color, marker="o", linewidth=2.2, capsize=4, label="Mean ± SD")
            for pressure, group in zip(pressures, values):
                ax.scatter([pressure] * len(group), group, facecolors="white", edgecolors=color, s=28, zorder=3)
            ax.set(xlabel="Contact pressure (kPa)", ylabel=ylabel)
            ax.set_xlim(0, 35)
            ax.legend(frameon=False, loc="upper right")
            ax.grid(axis="y", color="#D0D5DD", linewidth=.7)
        fig.suptitle("Synthetic matched-conductivity control (n=5 per pressure)", fontsize=14, fontweight="bold")
        svg_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(svg_path, facecolor="white")
        fig.savefig(png_path, dpi=220, facecolor="white")
        plt.close(fig)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    build(root / "contact-pressure.csv", root / "contact-pressure.svg", root / "contact-pressure.png")
