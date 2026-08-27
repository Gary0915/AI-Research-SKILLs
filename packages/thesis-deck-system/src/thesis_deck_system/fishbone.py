"""Version-aware editable SVG fishbone renderer."""

from __future__ import annotations

from html import escape
from pathlib import Path


COLORS = {
    "current": ("#b42318", "#fff1f0"),
    "completed": ("#2f6b4f", "#eef7f1"),
    "failed_but_informative": ("#7a4e00", "#fff5d6"),
    "partial": ("#7a4e00", "#fff5d6"),
    "future": ("#7a8592", "#f2f4f6"),
    "superseded": ("#7a8592", "#eceff1"),
}


def render_fishbone_svg(revision: dict, focus_branch_refs: list[str], layer_label: str, output_path: Path) -> Path:
    branches = revision.get("branches", [])
    ids = {branch["branch_id"] for branch in branches}
    unknown = sorted(set(focus_branch_refs) - ids)
    if unknown:
        raise ValueError(f"unknown focus branch: {unknown}")
    width, height = 1200, 650
    roots = [branch for branch in branches if branch.get("parent_ref") is None]
    children = [branch for branch in branches if branch.get("parent_ref") is not None]
    rows = roots + children
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="1200" height="650" fill="white"/>', '<style>text{font-family:sans-serif}.label{font-size:22px}.small{font-size:15px}</style>', '<line x1="180" y1="325" x2="1040" y2="325" stroke="#344054" stroke-width="8"/>', '<polygon points="1040,305 1100,325 1040,345" fill="#344054"/>', '<text x="920" y="382" class="small" fill="#344054">THESIS OUTCOME</text>']
    for index, branch in enumerate(rows):
        upper = index % 2 == 0
        column = index // 2
        x = 260 + column * 150
        y = 120 if upper else 500
        line_end = y + 55 if upper else y - 55
        status = "current" if branch["branch_id"] in focus_branch_refs else branch.get("status", "future")
        stroke, fill = COLORS.get(status, COLORS["future"])
        parts.append(f'<line x1="{x+50}" y1="325" x2="{x}" y2="{line_end}" stroke="{stroke}" stroke-width="4"/>')
        parts.append(f'<g id="{escape(branch["branch_id"])}" data-branch-id="{escape(branch["branch_id"])}" data-status="{status}"><rect x="{x-65}" y="{y-34}" width="210" height="68" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="{5 if status == "current" else 2}"/><text x="{x+40}" y="{y+7}" text-anchor="middle" class="label" fill="{stroke}">{escape(branch["label"])}</text></g>')
        if status == "current":
            parts.append(f'<text x="{x+40}" y="{y-48}" text-anchor="middle" class="small" fill="{stroke}">CURRENT / {escape(layer_label)}</text>')
        elif status == "completed":
            parts.append(f'<text x="{x+120}" y="{y-22}" class="small" fill="{stroke}">✓</text>')
        elif status in {"failed_but_informative", "partial"}:
            parts.append(f'<text x="{x+40}" y="{y+52}" text-anchor="middle" class="small" fill="{stroke}">INFORMATIVE / PARTIAL</text>')
    parts.append('</svg>')
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(parts), encoding="utf-8")
    return output_path
