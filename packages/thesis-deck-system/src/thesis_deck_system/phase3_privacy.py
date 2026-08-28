"""Fail-closed Phase 3 privacy controls; this module never opens a fixture."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable


class PrivacyViolation(ValueError):
    """Raised before unsafe private data can cross the Checkpoint 1 boundary."""


_ALLOWED_PROFILE_FIELDS = {
    "alias_uri",
    "resolved_status",
    "source_sha256",
    "sanitized_profile_id",
    "slide_size",
}
_CANARY_PATTERNS = (
    ("absolute_path", re.compile(r"(?:[A-Za-z]:[\\/](?!/)|\\\\|/(?:home|Users)/)")),
    ("url_or_doi", re.compile(r"(?:https?://|doi:\s*|10\.\d{4,9}/)", re.I)),
    ("private_text_canary", re.compile(r"PRIVATE_(?:(?:TEXT|NOTES|AUTHOR|COMPANY|MEDIA)_)?CANARY", re.I)),
    ("ooxml_fragment", re.compile(r"<(?:Relationship|p:|a:|w:)[^>]*>")),
    ("private_filename", re.compile(r"(?:private[-_](?:render|media|slide)[^\s]*\.(?:pptx|png|jpe?g)|PRIVATE_[A-Z0-9_-]+\.(?:pptx|png|jpe?g))", re.I)),
)


@dataclass(frozen=True)
class PrivacyFinding:
    classification: str
    location: str


class PrivateProfileStore:
    """Validates a local-only destination before a future profiler could open input."""

    def __init__(self, root: Path | str, *, repository_root: Path | str):
        self.root = Path(root)
        self.repository_root = Path(repository_root).resolve()
        self._validate_root()

    def _validate_root(self) -> None:
        if self.root.is_symlink():
            raise PrivacyViolation("private root symlink is forbidden")
        resolved = self.root.resolve(strict=False)
        if resolved == self.repository_root:
            raise PrivacyViolation("private root must be outside committed artifact directories")
        try:
            resolved.relative_to(self.repository_root)
        except ValueError:
            return
        if not self._git_ignored(resolved):
            raise PrivacyViolation("private root inside repository must be ignored")
        if self._git_tracked_or_staged(resolved):
            raise PrivacyViolation("private root must be untracked and unstaged")

    def _git_ignored(self, root: Path) -> bool:
        rel = root.relative_to(self.repository_root).as_posix()
        result = subprocess.run(
            ["git", "check-ignore", "-q", "--", rel],
            cwd=self.repository_root,
            check=False,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def _git_tracked_or_staged(self, root: Path) -> bool:
        rel = root.relative_to(self.repository_root).as_posix()
        for args in (("ls-files", "--cached", "--", rel), ("diff", "--cached", "--name-only", "--", rel)):
            result = subprocess.run(["git", *args], cwd=self.repository_root, check=False, capture_output=True, text=True)
            if result.stdout.strip():
                return True
        return False

    def retention_policy(self) -> dict[str, Any]:
        return {"root_kind": "ignored_local" if self.root.resolve(strict=False).is_relative_to(self.repository_root) else "external_local", "cleanup_required": True, "private_source_open_permitted": False}

    def prepare_for_future_open(self) -> dict[str, Any]:
        """Verify an empty local run root can be written, without resolving any alias."""
        self.root.mkdir(parents=True, exist_ok=True)
        probe = self.root / ".privacy-write-probe"
        try:
            probe.write_text("probe", encoding="utf-8")
            if not probe.is_file():
                raise PrivacyViolation("private root is not writable")
        finally:
            probe.unlink(missing_ok=True)
        if self.root.resolve().is_relative_to(self.repository_root) and self._git_tracked_or_staged(self.root):
            raise PrivacyViolation("private root became tracked or staged")
        return {**self.retention_policy(), "writable": True, "retention_manifest_required": True}


class RepositoryPrivacyScanner:
    """Scans synthetic candidate content without retaining the forbidden value."""

    def scan_mapping(self, value: Any, *, location: str) -> list[PrivacyFinding]:
        findings: list[PrivacyFinding] = []

        def visit(item: Any, item_location: str) -> None:
            if isinstance(item, dict):
                for key, nested in item.items():
                    visit(key, f"{item_location}/key")
                    visit(nested, f"{item_location}/{key}")
            elif isinstance(item, list):
                for index, nested in enumerate(item):
                    visit(nested, f"{item_location}/{index}")
            elif isinstance(item, str):
                for classification, pattern in _CANARY_PATTERNS:
                    if pattern.search(item):
                        findings.append(PrivacyFinding(classification, item_location))
                        break

        visit(value, location)
        return findings

    def scan_paths(self, paths: Iterable[Path | str], *, location_root: Path | str) -> list[PrivacyFinding]:
        root = Path(location_root)
        findings: list[PrivacyFinding] = []
        for path_value in paths:
            path = Path(path_value)
            location = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.name
            suffix = path.suffix.lower()
            if suffix in {".pptx", ".pptm", ".ppsx", ".potx"}:
                findings.append(PrivacyFinding("private_pptx_candidate", location))
            elif suffix in {".png", ".jpg", ".jpeg", ".webp"} and "private" in path.name.lower():
                findings.append(PrivacyFinding("private_render_candidate", location))
        return findings

    def scan_staged(self, repository_root: Path | str) -> list[PrivacyFinding]:
        repo = Path(repository_root)
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=repo, check=False, capture_output=True, text=True)
        paths = [repo / line for line in result.stdout.splitlines() if line]
        content_paths = [path for path in paths if "/tests/" not in path.as_posix() and "/schemas/" not in path.as_posix() and path.name != "phase3_privacy.py"]
        return self.scan_paths(paths, location_root=repo) + self._scan_text_paths(content_paths, repo)

    def _scan_text_paths(self, paths: Iterable[Path], repository_root: Path) -> list[PrivacyFinding]:
        findings: list[PrivacyFinding] = []
        for path in paths:
            if not path.is_file() or path.suffix.lower() not in {".json", ".yaml", ".yml", ".md", ".py"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                findings.append(PrivacyFinding("binary_candidate", path.relative_to(repository_root).as_posix()))
                continue
            findings.extend(self.scan_mapping(text, location=path.relative_to(repository_root).as_posix()))
        return findings

    def scan_repository(self, repository_root: Path | str) -> list[PrivacyFinding]:
        """Scan tracked files and staged candidates without returning any private content."""
        repo = Path(repository_root)
        result = subprocess.run(["git", "ls-files", "--cached"], cwd=repo, check=False, capture_output=True, text=True)
        paths = [repo / line for line in result.stdout.splitlines() if line]
        findings = self.scan_staged(repo)
        artifact_roots = (repo / "thesis-deck-system" / "artifacts", repo / "thesis-deck-system" / "profiles", repo / "thesis-deck-system" / "reports")
        canonical_paths = [path for path in paths if path.suffix.lower() in {".json", ".yaml", ".yml", ".md"} and "/schemas/" not in path.as_posix() and any(path.is_relative_to(root) for root in artifact_roots)]
        findings.extend(self._scan_text_paths(canonical_paths, repo))
        return findings


def sanitize_profile(raw: dict[str, Any]) -> dict[str, Any]:
    """Construct a small allowlisted profile and reject the complete input on any defect."""
    unknown = set(raw) - _ALLOWED_PROFILE_FIELDS
    if unknown:
        raise PrivacyViolation("unknown sanitizer key")
    required = {"alias_uri", "resolved_status", "source_sha256", "sanitized_profile_id", "slide_size"}
    if set(raw) != required:
        raise PrivacyViolation("sanitizer input is incomplete")
    if not isinstance(raw["alias_uri"], str) or not raw["alias_uri"].startswith("private://"):
        raise PrivacyViolation("invalid private alias URI")
    if raw["resolved_status"] not in {"resolved", "blocked_fixture"}:
        raise PrivacyViolation("invalid resolved status")
    if not isinstance(raw["source_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", raw["source_sha256"]):
        raise PrivacyViolation("invalid source hash")
    if not isinstance(raw["sanitized_profile_id"], str) or not re.fullmatch(r"SP[0-9]{3,}", raw["sanitized_profile_id"]):
        raise PrivacyViolation("invalid sanitized profile ID")
    size = raw["slide_size"]
    if not isinstance(size, dict) or set(size) != {"width", "height"} or not all(isinstance(size[key], (int, float)) and size[key] > 0 for key in size):
        raise PrivacyViolation("invalid slide size")
    scanner = RepositoryPrivacyScanner()
    if scanner.scan_mapping(raw, location="sanitizer_input"):
        raise PrivacyViolation("sanitizer detected prohibited content")
    return {
        "alias_uri": raw["alias_uri"],
        "resolved_status": raw["resolved_status"],
        "source_sha256": raw["source_sha256"],
        "sanitized_profile_id": raw["sanitized_profile_id"],
        "slide_size": {"width": raw["slide_size"]["width"], "height": raw["slide_size"]["height"]},
    }
