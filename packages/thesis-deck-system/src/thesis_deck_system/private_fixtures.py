"""Private fixture alias resolution with explicit blocked behavior."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Mapping


REQUIRED_ALIASES = ("template_primary_1", "layout_exemplar_2", "template_primary_3")


class BlockedFixtureError(RuntimeError):
    pass


@dataclass(frozen=True)
class PrivateFixtureRecord:
    alias: str
    alias_uri: str
    path: Path
    sha256: str
    file_type: str
    slide_count: int | None


class PrivateFixtureLocator:
    def __init__(self, *, explicit: Mapping[str, str | Path] | None = None, config_path: str | Path | None = None, env_var: str = "THESIS_DECK_PRIVATE_ROOT"):
        self._paths: dict[str, Path] = {key: Path(value) for key, value in (explicit or {}).items()}
        if config_path:
            config = json.loads(Path(config_path).read_text(encoding="utf-8"))
            for key, value in config.get("aliases", {}).items():
                self._paths.setdefault(key, Path(value))
        root = os.environ.get(env_var)
        if root:
            root_path = Path(root)
            for alias in REQUIRED_ALIASES:
                for suffix in (".pptx", ".pptm"):
                    candidate = root_path / f"{alias}{suffix}"
                    if candidate.exists():
                        self._paths.setdefault(alias, candidate)

    def resolve(self, alias: str) -> PrivateFixtureRecord:
        path = self._paths.get(alias)
        if path is None or not path.is_file():
            raise BlockedFixtureError(f"blocked_fixture: unresolved private alias {alias}")
        slide_count = None
        if path.suffix.lower() in {".pptx", ".pptm"}:
            try:
                from pptx import Presentation
                slide_count = len(Presentation(path).slides)
            except Exception:
                slide_count = None
        return PrivateFixtureRecord(alias, f"private://{alias}", path.resolve(), hashlib.sha256(path.read_bytes()).hexdigest(), path.suffix.lower().lstrip("."), slide_count)

    def status(self) -> dict:
        records = []
        for alias in REQUIRED_ALIASES:
            try:
                record = self.resolve(alias)
                records.append({"alias": alias, "alias_uri": record.alias_uri, "status": "resolved", "sha256": record.sha256, "file_type": record.file_type, "slide_count": record.slide_count})
            except BlockedFixtureError:
                records.append({"alias": alias, "alias_uri": f"private://{alias}", "status": "blocked_fixture"})
        return {"mode": "real" if all(item["status"] == "resolved" for item in records) else "blocked_fixture", "aliases": records}
