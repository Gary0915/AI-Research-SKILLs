"""Deterministic Traditional Chinese wrapping helpers."""

from __future__ import annotations

import re


_CLOSING = "，。！？；：、）】》」』％%"


def wrap_zh_tw(text: str, *, max_chars: int) -> list[str]:
    if max_chars < 4:
        raise ValueError("max_chars must be at least 4")
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9 /+_.-]*[A-Za-z0-9]|\s+|.", text)
    lines: list[str] = []
    current = ""
    for token in tokens:
        if token.isspace() and not current:
            continue
        candidate = current + token
        if current and len(candidate) > max_chars:
            if token and token[0] in _CLOSING:
                if len(current) >= max_chars:
                    lines.append(current[:-1].rstrip())
                    current = current[-1:] + token
                else:
                    current += token
                continue
            lines.append(current.rstrip())
            current = token.lstrip()
        else:
            current = candidate
    if current:
        lines.append(current.rstrip())
    return lines
