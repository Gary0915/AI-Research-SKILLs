"""Version-aware hierarchical, editable SVG fishbone renderer."""

from __future__ import annotations

from html import escape
from pathlib import Path


COLORS = {
    "current": ("#b42318", "#fff1f0"), "completed": ("#2f6b4f", "#eef7f1"),
    "failed_but_informative": ("#7a4e00", "#fff5d6"), "partial": ("#7a4e00", "#fff5d6"),
    "future": ("#7a8592", "#f2f4f6"), "superseded": ("#7a8592", "#eceff1"),
}


def validate_fishbone_revision(revision: dict) -> list[str]:
    branches = revision.get("branches", [])
    ids = [str(branch.get("branch_id", "")) for branch in branches]
    errors: list[str] = []
    duplicates = sorted({branch_id for branch_id in ids if ids.count(branch_id) > 1})
    if duplicates:
        errors.append(f"duplicate branch IDs: {duplicates}")
    known = set(ids)
    for branch in branches:
        parent = branch.get("parent_ref")
        if parent is not None and parent not in known:
            errors.append(f"orphan parent {parent} for {branch.get('branch_id')}")
    for branch in branches:
        seen: set[str] = set()
        current = branch.get("branch_id")
        while current is not None:
            if current in seen:
                errors.append(f"cycle detected at {current}")
                break
            seen.add(current)
            parent = next((item.get("parent_ref") for item in branches if item.get("branch_id") == current), None)
            current = parent
    return sorted(set(errors))


def _positions(branches: list[dict]) -> dict[str, tuple[float, float]]:
    """Return deterministic positions; unrelated roots never move when a child is added."""
    roots = [branch for branch in branches if branch.get("parent_ref") is None]
    positions: dict[str, tuple[float, float]] = {}
    for index, branch in enumerate(roots):
        positions[branch["branch_id"]] = (270 + (index % 4) * 220, 120 if index % 2 == 0 else 500)
    children_by_parent: dict[str, list[dict]] = {}
    for branch in branches:
        if branch.get("parent_ref") is not None:
            children_by_parent.setdefault(branch["parent_ref"], []).append(branch)
    def visit(parent_id: str, depth: int = 0) -> None:
        parent_x, parent_y = positions[parent_id]
        for index, child in enumerate(children_by_parent.get(parent_id, [])):
            x = min(1060.0, parent_x + 95 + depth * 24)
            delta = 60 + (index % 3) * 55
            # Hang descendants away from the thesis spine.  A lower root's
            # children therefore remain visibly below that root rather than
            # crossing the spine into another branch's row.
            y = parent_y - delta if parent_y < 325 else min(610.0, parent_y + delta)
            positions[child["branch_id"]] = (x, y)
            visit(child["branch_id"], depth + 1)
    for root in roots:
        visit(root["branch_id"])
    return positions


def branch_positions(revision: dict) -> dict[str, tuple[float, float]]:
    """Expose the deterministic position map for revision QA evidence."""
    errors = validate_fishbone_revision(revision)
    if errors:
        raise ValueError("invalid fishbone revision: " + "; ".join(errors))
    return _positions(revision.get("branches", []))


def render_fishbone_svg(revision: dict, focus_branch_refs: list[str], layer_label: str, output_path: Path) -> Path:
    errors = validate_fishbone_revision(revision)
    if errors:
        raise ValueError("invalid fishbone revision: " + "; ".join(errors))
    branches = revision.get("branches", [])
    ids = {branch["branch_id"] for branch in branches}
    unknown = sorted(set(focus_branch_refs) - ids)
    if unknown:
        raise ValueError(f"unknown focus branch: {unknown}")
    width, height = 1200, 650
    positions = _positions(branches)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="1200" height="650" fill="white"/>', '<style>text{font-family:sans-serif}.label{font-size:22px}.small{font-size:15px}</style>', '<line x1="180" y1="325" x2="1040" y2="325" stroke="#344054" stroke-width="8"/>', '<polygon points="1040,305 1100,325 1040,345" fill="#344054"/>', '<text x="920" y="382" class="small" fill="#344054">THESIS OUTCOME</text>']
    for branch in branches:
        branch_id = branch["branch_id"]
        x, y = positions[branch_id]
        parent = branch.get("parent_ref")
        if parent is None:
            start_x, start_y = x + 50, 325
        else:
            parent_x, parent_y = positions[parent]
            start_x, start_y = parent_x + 50, parent_y
        line_end = y + 34 if y < 325 else y - 34
        status = "current" if branch_id in focus_branch_refs else branch.get("status", "future")
        stroke, fill = COLORS.get(status, COLORS["future"])
        parts.append(f'<line x1="{start_x:.1f}" y1="{start_y:.1f}" x2="{x:.1f}" y2="{line_end:.1f}" stroke="{stroke}" stroke-width="{5 if status == "current" else 3}" data-parent-ref="{escape(parent or "spine")}"/>')
        parts.append(f'<g id="{escape(branch_id)}" data-branch-id="{escape(branch_id)}" data-parent-ref="{escape(parent or "spine")}" data-status="{status}" data-position="{x:.1f},{y:.1f}"><rect x="{x-65:.1f}" y="{y-34:.1f}" width="210" height="68" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="{5 if status == "current" else 2}"/><text x="{x+40:.1f}" y="{y+7:.1f}" text-anchor="middle" class="label" fill="{stroke}">{escape(branch["label"])}</text></g>')
        if status == "current":
            parts.append(f'<text x="{x+40:.1f}" y="{y-48:.1f}" text-anchor="middle" class="small" fill="{stroke}">CURRENT / {escape(layer_label)}</text>')
        elif status == "completed":
            parts.append(f'<text x="{x+120:.1f}" y="{y-22:.1f}" class="small" fill="{stroke}">✓</text>')
        elif status in {"failed_but_informative", "partial"}:
            parts.append(f'<text x="{x+40:.1f}" y="{y+52:.1f}" text-anchor="middle" class="small" fill="{stroke}">INFORMATIVE / PARTIAL</text>')
    parts.append('</svg>')
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(parts), encoding="utf-8")
    return output_path
