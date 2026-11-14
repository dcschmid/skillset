"""YAML frontmatter extraction for SKILL.md files.

Uses PyYAML when importable; otherwise falls back to a minimal parser that
covers the subset actually used by skill frontmatter in the wild:
block mappings, folded scalars (>), literal scalars (|), quoted scalars,
nested one-level maps and inline lists. The fallback is deterministic and
dependency-free so validation never hard-requires PyYAML.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

try:  # pragma: no cover - environment dependent
    import yaml  # type: ignore

    HAVE_YAML = True
except Exception:  # pragma: no cover - fallback path
    yaml = None
    HAVE_YAML = False

_FM_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)


class FrontmatterError(Exception):
    """Raised when frontmatter is missing or malformed."""


@dataclass
class ParsedFrontmatter:
    data: dict[str, Any] = field(default_factory=dict)
    body: str = ""
    raw: str = ""
    yaml_error: str | None = None


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Return (raw_yaml_block_or_None, body). Raises on unclosed fence."""
    if not text.startswith("---"):
        return None, text
    m = _FM_RE.match(text)
    if m:
        return m.group(1), text[m.end():]
    # opening fence but no close -> malformed
    if re.match(r"\A---[ \t]*\r?\n", text):
        raise FrontmatterError("frontmatter opened with '---' but never closed")
    return None, text


def parse(text: str) -> ParsedFrontmatter:
    """Parse a full SKILL.md document string."""
    try:
        raw, body = split_frontmatter(text)
    except FrontmatterError as exc:
        return ParsedFrontmatter(yaml_error=str(exc), body=text)
    if raw is None:
        return ParsedFrontmatter(yaml_error="no YAML frontmatter found", body=body)
    if HAVE_YAML:
        try:
            data = yaml.safe_load(raw)
        except Exception as exc:  # yaml.YAMLError and friends
            return ParsedFrontmatter(raw=raw, body=body, yaml_error=str(exc))
        if data is None:
            data = {}
        if not isinstance(data, dict):
            return ParsedFrontmatter(
                raw=raw, body=body,
                yaml_error=f"frontmatter must be a mapping, got {type(data).__name__}",
            )
        return ParsedFrontmatter(data=data, body=body, raw=raw)
    data, err = _mini_parse(raw)
    return ParsedFrontmatter(data=data, body=body, raw=raw, yaml_error=err)


# ---------------------------------------------------------------------------
# Minimal YAML subset parser (fallback when PyYAML is absent)
# ---------------------------------------------------------------------------

_KEY_RE = re.compile(r"^([A-Za-z0-9_][A-Za-z0-9_.\- ]*):(.*)$")


def _scalar(value: str) -> Any:
    v = value.strip()
    if v == "" or v in (">", "|", ">-", "|-"):
        return ""
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [_scalar(p) for p in inner.split(",")] if inner else []
    if v in ("true", "True"):
        return True
    if v in ("false", "False"):
        return False
    if v == "null" or v == "~":
        return None
    try:
        return int(v)
    except ValueError:
        pass
    return v


def _mini_parse(raw: str) -> tuple[dict[str, Any], str | None]:
    """Parse mappings with optional one-level nesting and block scalars."""
    out: dict[str, Any] = {}
    lines = raw.splitlines()
    i, n = 0, len(lines)
    err: str | None = None
    try:
        while i < n:
            line = lines[i]
            if not line.strip() or line.lstrip().startswith("#"):
                i += 1
                continue
            m = _KEY_RE.match(line)
            if not m:
                i += 1  # tolerate continuation/unknown lines at top level
                continue
            key, rest = m.group(1).strip(), m.group(2)
            rest_s = rest.strip()
            if rest_s in (">", "|", ">-", "|-"):
                block, i = _collect_block(lines, i + 1)
                out[key] = block
                continue
            if rest_s == "":
                nxt = _peek_next_value_line(lines, i + 1)
                if nxt is not None and _is_nested(lines, i, nxt):
                    block, i = _collect_nested(lines, nxt)
                    out[key] = block
                    continue
                out[key] = ""
                i += 1
                continue
            out[key] = _scalar(rest)
            i += 1
    except ValueError as exc:
        err = str(exc)
    return out, err


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _peek_next_value_line(lines: list[str], start: int) -> int | None:
    for j in range(start, len(lines)):
        if lines[j].strip() and not lines[j].lstrip().startswith("#"):
            return j
    return None


def _is_nested(lines: list[str], parent_i: int, child_i: int) -> bool:
    return _indent(lines[child_i]) > _indent(lines[parent_i])


def _collect_block(lines: list[str], start: int) -> tuple[str, int]:
    parts: list[str] = []
    i = start
    base = None
    while i < len(lines):
        line = lines[i]
        if line.strip() and _indent(line) == 0:
            break
        if line.strip():
            ind = _indent(line)
            if base is None:
                base = ind
            parts.append(line[min(base or ind, len(line)):])
        else:
            parts.append("")
        i += 1
    return "\n".join(parts).rstrip(), i


def _collect_nested(lines: list[str], start: int) -> tuple[dict[str, Any], int]:
    base = _indent(lines[start])
    out: dict[str, Any] = {}
    i = start
    while i < len(lines):
        line = lines[i]
        if line.strip() and _indent(line) <= base and not _is_blank(line):
            break
        stripped = line.strip()
        if stripped and _indent(line) >= base:
            m = _KEY_RE.match(stripped)
            if m:
                key, rest = m.group(1).strip(), m.group(2).strip()
                if rest in (">", "|", ">-", "|-"):
                    block, i = _collect_block(lines, i + 1)
                    out[key] = block
                    continue
                out[key] = _scalar(rest) if rest else ""
        i += 1
    return out, i


def _is_blank(line: str) -> bool:
    return not line.strip()
