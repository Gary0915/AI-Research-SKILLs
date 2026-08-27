"""Explicit repository context without path-depth assumptions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectContext:
    repo_root: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "repo_root", Path(self.repo_root).resolve())

    def resolve_repo_path(self, value: str | Path) -> Path:
        path = Path(value)
        resolved = path.resolve() if path.is_absolute() else (self.repo_root / path).resolve()
        try:
            resolved.relative_to(self.repo_root)
        except ValueError as exc:
            raise ValueError(f"path escapes repository: {value}") from exc
        return resolved

    def canonical_path(self, value: str | Path) -> str:
        resolved = self.resolve_repo_path(value)
        return resolved.relative_to(self.repo_root).as_posix()

    @classmethod
    def discover(cls, anchor: str | Path) -> "ProjectContext":
        current = Path(anchor).resolve()
        current = current.parent if current.is_file() else current
        for candidate in (current, *current.parents):
            if (candidate / ".git").exists() and (candidate / "thesis-deck-system").is_dir():
                return cls(candidate)
        raise ValueError(f"repository root not discoverable from {anchor}")
