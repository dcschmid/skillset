"""Skill validation with strict separation of rule tiers.

Tiers (never conflated — a valid Claude-Code field is not a portable error):
  standard   — open Agent Skills spec (agentskills.io/specification)
  host       — host-specific extensions (claude / codex profiles)
  repo       — repository conventions (skillset AGENTS.md)
  unknown    — fields outside every known registry

Profiles:
  portable — open standard only (host keys reported as info, not errors)
  claude   — standard + Claude Code extensions
  codex    — standard + agents/openai.yaml style metadata
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# --- field registries -------------------------------------------------------
STANDARD_FIELDS = {"name", "description", "license", "compatibility",
                   "metadata", "allowed-tools"}
CLAUDE_EXTRA = {"allowed-tools"}          # also in standard but Claude-first
CODEX_HINT_PATH = "agents/openai.yaml"
REPO_CONVENTIONS_DOC = "AGENTS.md"

NAME_MAX, DESC_MAX, COMPAT_MAX = 64, 1024, 500
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

TIERS = ("standard", "host", "repo", "unknown")

BODY_MAX_LINES = 500            # spec guidance: keep SKILL.md under 500 lines
DESC_TRIGGER_HINTS = ("use when", "use for", "activate", "use this",
                      "verwende", "benutze", "einsatz", "when to",
                      "tasks", "audit", "build")


@dataclass
class Finding:
    check: str
    tier: str                  # standard | host | repo | unknown
    severity: str              # error | warn | info
    message: str
    evidence: str = ""

    def to_dict(self) -> dict:
        return {"check": self.check, "tier": self.tier,
                "severity": self.severity, "message": self.message,
                "evidence": self.evidence[:200]}


@dataclass
class ValidationReport:
    skill_id: str
    profile: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def blockers(self) -> list[Finding]:
        return [f for f in self.errors
                if f.check.startswith(("meta.", "security."))]

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {"skill": self.skill_id, "profile": self.profile,
                "ok": self.ok,
                "findings": [f.to_dict() for f in self.findings]}


def validate_skill(skill, profile: str = "portable",
                   repo_conventions: bool = True) -> ValidationReport:
    """skill: DiscoveredSkill. Deterministic checks only; anything that
    cannot be checked from files is reported, not assumed."""
    rep = ValidationReport(skill_id=skill.dir_name, profile=profile)
    fm_data = skill.frontmatter or {}

    if skill.yaml_error:
        rep.findings.append(Finding(
            "meta.yaml", "standard", "error",
            f"SKILL.md frontmatter invalid: {skill.yaml_error}",
            evidence=(skill.frontmatter and str(fm_data)[:80]) or ""))
        return rep
    if not fm_data:
        rep.findings.append(Finding(
            "meta.missing", "standard", "error",
            "no YAML frontmatter in SKILL.md"))
        return rep

    _check_name(rep, fm_data, skill)
    _check_description(rep, fm_data)
    _check_optional_standard(rep, fm_data)
    _check_fields(rep, fm_data, profile)
    if repo_conventions:
        _check_repo_conventions(rep, fm_data, skill)
    _check_structure(rep, skill)
    _check_content(rep, skill)
    _check_security(rep, skill)
    return rep


# -- standard tier -----------------------------------------------------------

def _check_name(rep, fm_data, skill):
    name = fm_data.get("name")
    if name is None:
        rep.findings.append(Finding("meta.name.required", "standard", "error",
                                    "`name` is required"))
        return
    name = str(name)
    if len(name) > NAME_MAX:
        rep.findings.append(Finding("meta.name.length", "standard", "error",
                                    f"`name` exceeds {NAME_MAX} chars", name))
    if not NAME_RE.match(name):
        rep.findings.append(Finding(
            "meta.name.format", "standard", "error",
            "`name` must be lowercase alnum + single hyphens, no edge hyphens",
            name))
    if name != skill.dir_name:
        rep.findings.append(Finding(
            "meta.name.dirmatch", "repo", "error",
            f"name '{name}' != directory '{skill.dir_name}' "
            "(repository convention, AGENTS.md)", name))


def _check_description(rep, fm_data):
    desc = fm_data.get("description")
    if not desc:
        rep.findings.append(Finding("meta.description.required", "standard",
                                    "error", "`description` is required"))
        return
    desc = str(desc).strip()
    if len(desc) > DESC_MAX:
        rep.findings.append(Finding("meta.description.length", "standard",
                                    "error",
                                    f"`description` exceeds {DESC_MAX} chars",
                                    f"len={len(desc)}"))
    low = desc.lower()
    if not any(h in low for h in DESC_TRIGGER_HINTS):
        rep.findings.append(Finding(
            "content.activation", "repo", "warn",
            "description lacks trigger/activation phrasing "
            "(repo authoring rule: description mentions trigger phrases)"))


def _check_optional_standard(rep, fm_data):
    comp = fm_data.get("compatibility")
    if comp is not None and len(str(comp)) > COMPAT_MAX:
        rep.findings.append(Finding("meta.compatibility.length", "standard",
                                    "error",
                                    f"`compatibility` exceeds {COMPAT_MAX} chars",
                                    f"len={len(str(comp))}"))
    meta = fm_data.get("metadata")
    if meta is not None and not isinstance(meta, dict):
        rep.findings.append(Finding("meta.metadata.shape", "standard", "error",
                                    "`metadata` must be a string→string map"))
    elif isinstance(meta, dict):
        for k, v in meta.items():
            if not isinstance(v, (str, int, float)) and v is not None:
                rep.findings.append(Finding(
                    "meta.metadata.shape", "standard", "warn",
                    f"metadata.{k} is not a scalar value"))
                break
    at = fm_data.get("allowed-tools")
    if at is not None and not isinstance(at, str):
        rep.findings.append(Finding("meta.allowed-tools.shape", "standard",
                                    "warn",
                                    "`allowed-tools` should be a space-separated string"))


def _check_fields(rep, fm_data, profile):
    known = set(STANDARD_FIELDS)
    if profile == "claude":
        known |= CLAUDE_EXTRA
    for key in fm_data:
        key = str(key)
        if key in STANDARD_FIELDS:
            continue
        if key in CLAUDE_EXTRA:
            if profile in ("claude",):
                rep.findings.append(Finding(
                    "host.allowed-tools", "host", "info",
                    "`allowed-tools` accepted (Claude Code extension / "
                    "experimental standard field)"))
            else:
                rep.findings.append(Finding(
                    "host.allowed-tools", "host", "info",
                    "`allowed-tools` is a host extension; not an error "
                    f"under profile {profile}", key))
            continue
        if profile == "codex" and key in ("metadata",):
            rep.findings.append(Finding("host.codex-metadata", "host", "info",
                                        "metadata carries Codex host data"))
            continue
        rep.findings.append(Finding(
            "meta.unknown-field", "unknown", "warn",
            f"field `{key}` is not part of the open standard; treated as "
            f"host-specific extension under profile '{profile}' — not a "
            "portability failure until verified for the target host", key))


# -- repo tier ----------------------------------------------------------------

def _check_repo_conventions(rep, fm_data, skill):
    body = skill.body or ""
    if len(body.splitlines()) > BODY_MAX_LINES:
        rep.findings.append(Finding(
            "size.body", "repo", "warn",
            f"SKILL.md body exceeds {BODY_MAX_LINES} lines "
            "(progressive-disclosure rule: depth belongs in references/)",
            f"lines={len(body.splitlines())}"))
    p = skill.path / "scripts"
    if p.is_dir():
        for s in sorted(p.glob("*.py")):
            try:
                compile(s.read_text(encoding="utf-8", errors="replace"),
                        str(s), "exec")
            except SyntaxError as exc:
                rep.findings.append(Finding(
                    "scripts.syntax", "repo", "error",
                    f"scripts/{s.name} does not compile: {exc}",
                    f"line {exc.lineno}"))


# -- structure ----------------------------------------------------------------

_LINK_RE = re.compile(r"\]\((?!https?://|#)([^)#\s]+)")


def _check_structure(rep, skill):
    base = skill.path
    body = skill.body or ""
    seen_ids = set()
    for m in _LINK_RE.finditer(body):
        target = m.group(1).strip()
        seen_ids.add(target)
        if not any((base / target).exists() for _ in (0,)) \
                and not (base / target).resolve().exists():
            rep.findings.append(Finding(
                "structure.broken-link", "standard", "error",
                f"relative link target missing: {target}",
                f"line {body[:m.start()].count(chr(10)) + 1}"))
    # referenced-but-missing helper names in inline code (common failure mode)
    for rel_dir in ("references", "scripts", "assets", "workflows", "templates"):
        d = base / rel_dir
        if not d.is_dir():
            continue  # missing optional dir is not a fault (repo rule)
        for f in sorted(d.iterdir()):
            if f.is_file() and f.suffix in (".md", ".py", ".sh"):
                if f.name in body or f.stem in body:
                    continue
                linked = any(f.name in t or str(f) in t for t in seen_ids)
                if not linked and rel_dir in ("references",):
                    rep.findings.append(Finding(
                        "structure.orphan-reference", "repo", "info",
                        f"{rel_dir}/{f.name} exists but is not linked from "
                        "SKILL.md (dead context weight)"))


# -- content ------------------------------------------------------------------

def _check_content(rep, skill):
    body = (skill.body or "").lower()
    if not body.strip():
        rep.findings.append(Finding("content.empty-body", "standard", "error",
                                    "SKILL.md has no instructions body"))
        return
    if not any(h in body for h in ("when", "activat", "trigger", "einsatz")):
        rep.findings.append(Finding(
            "content.activation-section", "repo", "warn",
            "no activation/when-to-use section in body"))
    if "do not" not in body and "don't" not in body and "not activate" not in body \
            and "nicht" not in body and "avoid" not in body:
        rep.findings.append(Finding(
            "content.negative-examples", "repo", "info",
            "no negative activation examples found "
            "(routing precision depends on them)"))
    if "pass" not in body and "fail" not in body and "review_required" not in body:
        rep.findings.append(Finding(
            "content.success-criteria", "repo", "warn",
            "no PASS/FAIL/REVIEW_REQUIRED success criteria found "
            "(repo rule: gates produce verdicts, not vibes)"))
    dup = _duplicated_blocks(body)
    if dup:
        rep.findings.append(Finding(
            "content.duplication", "repo", "info",
            f"{dup} duplicated paragraph(s) >=120 chars", ""))


def _duplicated_blocks(body: str) -> int:
    paras = [p.strip() for p in body.split("\n\n") if len(p.strip()) >= 120]
    seen, dup = set(), 0
    for p in paras:
        key = " ".join(p.lower().split())
        if key in seen:
            dup += 1
        seen.add(key)
    return dup


# -- security -----------------------------------------------------------------
# Skill content is DATA. These checks flag instructions that would be risky
# if executed blindly; they never authorize execution.

_SECURITY_PATTERNS = [
    ("security.rm-rf", re.compile(r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r"),
     "error", "recursive force delete (`rm -rf`) without target guard"),
    ("security.sudo", re.compile(r"\bsudo\b"), "warn",
     "elevated privileges (`sudo`) requested"),
    ("security.pipe-shell", re.compile(r"curl[^|]*\|\s*(ba)?sh|wget[^|]*\|\s*(ba)?sh"),
     "warn", "remote code piped to shell"),
    ("security.secrets", re.compile(r"(cat|echo|print)[^\n]*(\.env|id_rsa|secrets?\.(json|env))"),
     "warn", "reads a secret-bearing file"),
    ("secret.exfil", re.compile(r"curl[^\n]*-d[^\n]*(key|token|secret)|POST[^\n]*token"),
     "warn", "outbound transmission of credential-looking data"),
]


def _check_security(rep, skill):
    body = skill.body or ""
    for line_no, line in enumerate(body.splitlines(), 1):
        s = line.strip()
        if s.startswith("```") or s.startswith("#"):
            continue
        for check, rx, sev, msg in _SECURITY_PATTERNS:
            if rx.search(line):
                rep.findings.append(Finding(check, "repo", sev, msg,
                                            f"line {line_no}: {s[:120]}"))
