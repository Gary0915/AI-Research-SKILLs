"""Reproducible synthetic plot entry point (delegates to package implementation)."""
from pathlib import Path
from thesis_deck_system.plotting import build_plot

if __name__ == "__main__":
    root = Path(__file__).parent
    build_plot(root / "measurements.csv", root / "generated-plot")
