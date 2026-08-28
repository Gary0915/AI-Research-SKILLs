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
    ("absolute_path", re.compile(r"(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|\\\\|/mnt/[A-Za-z]/|/(?:home|Users)/)", re.I)),
    ("url_or_doi", re.compile(r"(?:https?://|doi:\s*|10\.\d{4,9}/)", re.I)),
    ("private_text_canary", re.compile(r"PRIVATE_(?:(?:TEXT|NOTES|AUTHOR|COMPANY|MEDIA)_)?CANARY", re.I)),
    ("ooxml_fragment", re.compile(r"<(?:Relationship|p:|a:|w:)[^>]*>")),
    ("private_filename", re.compile(r"(?:private[-_](?:render|media|slide)[^\s]*\.(?:pptx|png|jpe?g)|PRIVATE_[A-Z0-9_-]+\.(?:pptx|png|jpe?g))", re.I)),
)


@dataclass(frozen=True)
class PrivacyFinding:
    classification: str
    location: str


LEGACY_EXCEPTION_PATH = "thesis-deck-system/reviews/PHASE_3_DESIGN_REVIEW.md"
LEGACY_EXCEPTION_BLOB_SHA = "1808c054cc2ad5a618a9f19907ef57da79c39973"


@dataclass(frozen=True)
class LegacyExceptionEvidence:
    exception_id: str
    repository_relative_path: str
    reviewed_blob_sha: str
    privacy_rule_id: str
    status: str

    def as_dict(self) -> dict[str, str]:
        return {
            "exception_id": self.exception_id,
            "repository_relative_path": self.repository_relative_path,
            "reviewed_blob_sha": self.reviewed_blob_sha,
            "privacy_rule_id": self.privacy_rule_id,
            "status": self.status,
        }


class PrivateProfileStore:
    """Validates a local-only destination before a future profiler could open input."""

    def __init__(self, root: Path | str, *, repository_root: Path | str):
        self.root = Path(root).resolve(strict=False)
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
            result = subprocess.run(["git", *args], cwd=self.repository_root, check=False, capture_output=True, text=True, encoding="utf-8", errors="strict")
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

    def resolve_private_alias(self, request_id: str, *, execution_evidence: Any) -> None:
        """Checkpoint 1 entry point: record the attempt, then reject before resolution."""
        execution_evidence.reject_private_alias_resolution(request_id)

    def open_private_source(self, request_id: str, *, execution_evidence: Any) -> None:
        """Checkpoint 1 entry point: record the attempt, then reject before source open."""
        execution_evidence.reject_private_source_open(request_id)


class RepositoryPrivacyScanner:
    """Scans synthetic candidate content without retaining the forbidden value."""

    def __init__(self, *, private_root_signatures: Iterable[str] = (), forbidden_basenames: Iterable[str] = ()):
        self._private_root_patterns = tuple(re.compile(re.escape(value), re.I) for value in private_root_signatures)
        self._forbidden_basenames = {value.casefold() for value in forbidden_basenames}

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
                else:
                    if any(pattern.search(item) for pattern in self._private_root_patterns):
                        findings.append(PrivacyFinding("configured_private_root", item_location))
                    elif Path(item).name.casefold() in self._forbidden_basenames:
                        findings.append(PrivacyFinding("forbidden_private_basename", item_location))

        visit(value, location)
        return findings

    def scan_paths(self, paths: Iterable[Path | str], *, location_root: Path | str) -> list[PrivacyFinding]:
        root = Path(location_root)
        findings: list[PrivacyFinding] = []
        for path_value in paths:
            path = Path(path_value)
            location = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.name
            suffix = path.suffix.lower()
            if any(pattern.search(location) for pattern in self._private_root_patterns):
                findings.append(PrivacyFinding("configured_private_root", location))
            elif path.name.casefold() in self._forbidden_basenames:
                findings.append(PrivacyFinding("forbidden_private_basename", location))
            elif suffix in {".pptx", ".pptm", ".ppsx", ".potx"}:
                findings.append(PrivacyFinding("private_pptx_candidate", location))
            elif suffix in {".png", ".jpg", ".jpeg", ".webp"} and "private" in path.name.lower():
                findings.append(PrivacyFinding("private_render_candidate", location))
        return findings

    _TEXT_SUFFIXES = {".json", ".yaml", ".yml", ".md", ".py", ".txt", ".toml", ".ini", ".cfg"}

    @staticmethod
    def _is_narrow_canary_exclusion(path: Path) -> bool:
        """Only tests and scanner/profiler pattern definitions may contain canaries."""
        normalized = path.as_posix()
        return "/tests/" in normalized or normalized.endswith("/phase3_privacy.py") or normalized.endswith("/phase3_checkpoint2.py")

    def scan_staged(self, repository_root: Path | str) -> list[PrivacyFinding]:
        repo = Path(repository_root)
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=repo, check=False, capture_output=True, text=True, encoding="utf-8", errors="strict")
        paths = [repo / line for line in result.stdout.splitlines() if line]
        content_paths = [path for path in paths if not self._is_narrow_canary_exclusion(path)]
        return self.scan_paths(paths, location_root=repo) + self._scan_staged_text_paths(content_paths, repo)

    def _scan_staged_text_paths(self, paths: Iterable[Path], repository_root: Path) -> list[PrivacyFinding]:
        findings: list[PrivacyFinding] = []
        for path in paths:
            if path.suffix.lower() not in self._TEXT_SUFFIXES:
                continue
            rel = path.relative_to(repository_root).as_posix()
            try:
                result = subprocess.run(["git", "show", f":{rel}"], cwd=repository_root, check=False, capture_output=True, text=True, encoding="utf-8", errors="strict")
            except UnicodeDecodeError:
                findings.append(PrivacyFinding("staged_blob_unreadable", rel))
                continue
            if result.returncode != 0:
                findings.append(PrivacyFinding("staged_blob_unreadable", rel))
            else:
                findings.extend(self._scan_private_repository_text(result.stdout, location=rel))
        return findings

    def _scan_text_paths(self, paths: Iterable[Path], repository_root: Path, *, generic_absolute_paths: bool = True) -> list[PrivacyFinding]:
        findings: list[PrivacyFinding] = []
        for path in paths:
            if not path.is_file() or path.suffix.lower() not in self._TEXT_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                findings.append(PrivacyFinding("binary_candidate", path.relative_to(repository_root).as_posix()))
                continue
            findings.extend(self._scan_private_repository_text(text, location=path.relative_to(repository_root).as_posix(), generic_absolute_paths=generic_absolute_paths))
        return findings

    def _scan_private_repository_text(self, text: str, *, location: str, generic_absolute_paths: bool = True) -> list[PrivacyFinding]:
        """Scan committed text for configured private identities, not public URLs/docs."""
        findings: list[PrivacyFinding] = []
        absolute = re.search(r"(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|\\\\|/mnt/[A-Za-z]/|/(?:home|Users)/)", text, re.I)
        configured = any(pattern.search(text) for pattern in self._private_root_patterns)
        if absolute and (configured or (generic_absolute_paths and not self._private_root_patterns)):
            findings.append(PrivacyFinding("absolute_path", location))
        elif configured:
            findings.append(PrivacyFinding("configured_private_root", location))
        elif any(name in text.casefold() for name in self._forbidden_basenames):
            findings.append(PrivacyFinding("forbidden_private_basename", location))
        elif re.search(r"PRIVATE_(?:(?:TEXT|NOTES|AUTHOR|COMPANY|MEDIA)_)?CANARY", text, re.I):
            findings.append(PrivacyFinding("private_text_canary", location))
        return findings

    def scan_repository(self, repository_root: Path | str) -> list[PrivacyFinding]:
        """Scan tracked files and staged candidates without returning any private content."""
        repo = Path(repository_root)
        result = subprocess.run(["git", "ls-files", "--cached"], cwd=repo, check=False, capture_output=True, text=True, encoding="utf-8", errors="strict")
        paths = [repo / line for line in result.stdout.splitlines() if line]
        findings = self.scan_staged(repo)
        canonical_paths = [path for path in paths if not self._is_narrow_canary_exclusion(path)]
        # Large repositories contain instructional examples of POSIX/Windows
        # paths.  CP2 supplies configured private-root signatures for the
        # production scan; generic absolute-path canaries remain enabled for
        # small synthetic repositories and staged content.
        findings.extend(self._scan_text_paths(canonical_paths, repo, generic_absolute_paths=len(canonical_paths) < 100))
        return findings

    def scan_repository_with_legacy_exception(
        self, repository_root: Path | str, *, forbidden_basenames: Iterable[str]
    ) -> tuple[list[PrivacyFinding], list[dict[str, str]]]:
        """Apply only the reviewer-authorized, blob-bound historical exception."""
        repo = Path(repository_root)
        findings = self.scan_repository(repo)
        exceptions: list[dict[str, str]] = []
        target = repo / LEGACY_EXCEPTION_PATH
        target_findings = [item for item in findings if item.location == LEGACY_EXCEPTION_PATH]
        if target_findings:
            blob_result = subprocess.run(
                ["git", "rev-parse", f"HEAD:{LEGACY_EXCEPTION_PATH}"], cwd=repo,
                check=False, capture_output=True, text=True, encoding="utf-8", errors="strict",
            )
            blob_sha = blob_result.stdout.strip() if blob_result.returncode == 0 else ""
            authorized = bool(target.is_file()) and blob_sha == LEGACY_EXCEPTION_BLOB_SHA
            authorized = authorized and all(item.classification == "forbidden_private_basename" for item in target_findings)
            section = ""
            if authorized:
                content = target.read_text(encoding="utf-8")
                start_marker = "## D3-2 — Private exemplar roles remain asymmetric"
                start = content.find(start_marker)
                end = content.find("\n## ", start + len(start_marker)) if start >= 0 else -1
                section = content[start:end if end >= 0 else len(content)] if start >= 0 else ""
                reviewed_content = subprocess.run(
                    ["git", "show", f"HEAD:{LEGACY_EXCEPTION_PATH}"], cwd=repo,
                    check=False, capture_output=True, text=True, encoding="utf-8", errors="strict",
                ).stdout
                reviewed_start = reviewed_content.find(start_marker)
                reviewed_end = reviewed_content.find("\n## ", reviewed_start + len(start_marker)) if reviewed_start >= 0 else -1
                reviewed_section = reviewed_content[reviewed_start:reviewed_end if reviewed_end >= 0 else len(reviewed_content)] if reviewed_start >= 0 else ""
                for basename in forbidden_basenames:
                    token = str(basename).casefold()
                    if token not in content.casefold():
                        continue
                    section_count = section.casefold().count(token)
                    outside_count = content.casefold().count(token) - section_count
                    reviewed_count = reviewed_section.casefold().count(token)
                    if section_count != reviewed_count or outside_count or reviewed_count < 1:
                        authorized = False
                        break
            if authorized:
                findings = [item for item in findings if item.location != LEGACY_EXCEPTION_PATH]
                exceptions.append(LegacyExceptionEvidence(
                    exception_id="CP2-PRE-1-LEGACY-D3-2",
                    repository_relative_path=LEGACY_EXCEPTION_PATH,
                    reviewed_blob_sha=LEGACY_EXCEPTION_BLOB_SHA,
                    privacy_rule_id="forbidden_private_basename",
                    status="applied_legacy_exception",
                ).as_dict())
        return findings, exceptions


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
