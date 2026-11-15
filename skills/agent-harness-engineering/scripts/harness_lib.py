#!/usr/bin/env python3
"""harness_lib.py — shared stdlib-only core for agent-harness-engineering.

Platform-independent primitives: a draft-07-subset JSON-Schema validator,
tool-definition and observation contracts, loop detection, risk model and
transparent scoring. No third-party imports; runs on python3 >= 3.10.
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------- contracts

OBSERVATION_STATUSES = ("success", "warning", "error")
ERROR_CATEGORIES = ("invalid-parameters", "permission", "timeout", "rate-limit",
                    "connection", "dependency-missing", "corrupt-state", "unknown")
RISK_LEVELS = ("LOW", "MEDIUM", "HIGH", "CRITICAL")
TOOL_GRANULARITY = ("micro", "medium", "macro")

# Minimal portable JSON-Schema subset (draft-07). Enough for tool I/O schemas
# and the observation contract; unknown keywords are ignored, never invented.
_SCHEMA_TYPES = {"object": dict, "array": list, "string": str,
                 "integer": int, "number": (int, float), "boolean": bool,
                 "null": type(None)}


def validate_schema(value, schema, path="$", errors=None):
    """Validate `value` against `schema` (draft-07 subset). Returns list of
    error strings; empty list == valid. Bounded recursion, no eval."""
    errors = errors if errors is not None else []
    if len(path) > 512:
        return errors
    if not isinstance(schema, dict):
        return errors
    for key, sub in schema.items():
        if key == "$defs" or key == "definitions" or key == "$schema" or key == "$id":
            continue
    t = schema.get("type")
    if t is not None:
        types = t if isinstance(t, list) else [t]
        if not any(isinstance(value, _SCHEMA_TYPES.get(x, object)) for x in types):
            # int is acceptable for "number"; bool is not an int for schema purposes
            if not ("number" in types and isinstance(value, (int, float)) and not isinstance(value, bool)):
                errors.append(f"{path}: expected type {types}, got {type(value).__name__}")
                return errors
    if isinstance(value, bool) and t == "integer":
        errors.append(f"{path}: boolean is not an integer")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in enum {schema['enum']}")
    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                errors.append(f"{path}: missing required '{req}'")
        props = schema.get("properties", {})
        ap = schema.get("additionalProperties", True)
        for k, v in value.items():
            if k in props:
                validate_schema(v, props[k], f"{path}.{k}", errors)
            elif ap is False:
                errors.append(f"{path}: additional property '{k}' not allowed")
            elif isinstance(ap, dict):
                validate_schema(v, ap, f"{path}.{k}", errors)
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: fewer than {schema['minItems']} items")
        item = schema.get("items")
        if isinstance(item, dict):
            for i, v in enumerate(value):
                validate_schema(v, item, f"{path}[{i}]", errors)
        if isinstance(item, list):  # tuple validation
            for i, sch in enumerate(item):
                if i < len(value):
                    validate_schema(value[i], sch, f"{path}[{i}]", errors)
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path}: longer than maxLength {schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: does not match pattern {schema['pattern']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: {value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: {value} > maximum {schema['maximum']}")
    for alt in schema.get("oneOf", []) if isinstance(schema.get("oneOf"), list) else []:
        probe = []
        validate_schema(value, alt, path, probe)
        if not probe:
            pass
    if isinstance(schema.get("oneOf"), list):
        passing = 0
        for alt in schema["oneOf"]:
            probe = []
            validate_schema(value, alt, path, probe)
            if not probe:
                passing += 1
        if passing != 1:
            errors.append(f"{path}: oneOf matched {passing} alternatives, expected exactly 1")
    if isinstance(schema.get("anyOf"), list):
        if not any(_silent(value, alt) for alt in schema["anyOf"]):
            errors.append(f"{path}: no anyOf alternative matched")
    return errors


def _silent(value, schema):
    return not validate_schema(value, schema, "$", [])


# ------------------------------------------------------- observation audit

def audit_observation(obj):
    """Contract checks on an observation dict -> list of finding strings."""
    errs = []
    if not isinstance(obj, dict):
        return ["observation must be an object"]
    status = obj.get("status")
    if status not in OBSERVATION_STATUSES:
        errs.append(f"status {status!r} not in {OBSERVATION_STATUSES}")
    summary = obj.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        errs.append("summary must be a non-empty one-line string")
    elif "\n" in summary.strip():
        errs.append("summary must stay one line")
    if status == "error":
        err = obj.get("error")
        if not isinstance(err, dict):
            errs.append("status=error requires an error contract object")
            return errs
        if err.get("category") not in ERROR_CATEGORIES:
            errs.append(f"error.category {err.get('category')!r} not classified")
        if not err.get("stop_condition"):
            errs.append("error contract missing stop_condition (explicit abort criterion)")
        if "retryable" not in err:
            errs.append("error contract missing retryable flag")
        if err.get("retryable") and "max_retries" not in err:
            errs.append("retryable error without max_retries bound")
        if err.get("max_retries", 0) and err["max_retries"] > 10:
            errs.append("max_retries > 10 is an unbounded-retry smell")
    for key in ("artifacts", "next_actions"):
        v = obj.get(key)
        if v is not None and not isinstance(v, list):
            errs.append(f"{key} must be an array of references")
    return errs


# --------------------------------------------------------- tool definition

def audit_tool(tool):
    """Contract checks on one tool definition dict -> finding strings."""
    errs = []
    if not isinstance(tool, dict):
        return ["tool must be an object"]
    name = tool.get("name") or tool.get("function", {}).get("name") if isinstance(tool.get("function"), dict) else tool.get("name")
    if not name:
        errs.append("tool missing name")
    elif not re.fullmatch(r"[a-z][a-z0-9_\-]{0,63}", name):
        errs.append(f"tool name {name!r} not stable/explicit (lower snake/kebab)")
    desc = tool.get("description") or (tool.get("function", {}) or {}).get("description")
    if not desc or not str(desc).strip():
        errs.append("tool missing description")
    elif len(desc.split()) > 60:
        errs.append("tool description over 60 words — ambiguous, prompt-costly")
    schema = tool.get("parameters") or (tool.get("function", {}) or {}).get("parameters")
    if schema is None:
        errs.append("tool missing input schema (schema-first required)")
    elif isinstance(schema, dict):
        if schema.get("type") != "object":
            errs.append("parameters schema root must be type object")
        props = schema.get("properties", {})
        if not props:
            errs.append("parameters schema declares no properties")
        for pname, pspec in props.items():
            if isinstance(pspec, dict) and "description" not in pspec:
                errs.append(f"parameter {pname} lacks description (selection ambiguity)")
        req = schema.get("required", [])
        if isinstance(req, list):
            for r in req:
                if r not in props:
                    errs.append(f"required parameter {r} not in properties")
    else:
        errs.append("parameters must be a JSON Schema object")
    timeout = tool.get("timeout_ms")
    if timeout is not None and (not isinstance(timeout, int) or timeout <= 0 or timeout > 600_000):
        errs.append("timeout_ms must be a positive bound <= 600000")
    if tool.get("idempotent") is not None and not isinstance(tool["idempotent"], bool):
        errs.append("idempotent must be a boolean flag")
    return errs


def audit_tool_set(tools):
    """Cross-tool checks: duplicates, overlap, breadth. -> findings list."""
    findings = []
    names = {}
    for i, t in enumerate(tools if isinstance(tools, list) else []):
        n = t.get("name") if isinstance(t, dict) else None
        if n:
            if n in names:
                findings.append(f"duplicate tool name '{n}' at index {i} (first at {names[n]})")
            names[n] = i
    if len(tools) > 30:
        findings.append(f"{len(tools)} tools in one namespace — selection accuracy drops; group or gate")
    descs = {}
    for t in tools if isinstance(tools, list) else []:
        n, d = (t or {}).get("name"), " ".join(str((t or {}).get("description", "")).lower().split())
        if n and d:
            if d in descs:
                findings.append(f"tools '{n}' and '{descs[d]}' share an identical description — ambiguous selection")
            else:
                descs[d] = n
    return findings


# -------------------------------------------------------------- risk model

def classify_risk(operation):
    """Operation name/description -> LOW|MEDIUM|HIGH|CRITICAL (conservative)."""
    s = str(operation).lower()
    if re.search(r"delete|drop|rm -rf|truncate|wipe|irreversible|migrat|deploy|produce|release", s):
        return "CRITICAL" if re.search(r"delete|drop|rm -rf|wipe|irreversible", s) else "HIGH"
    if re.search(r"permission|grant|secret|credential|write|edit|modify|patch|commit", s):
        return "HIGH" if re.search(r"permission|secret|credential", s) else "MEDIUM"
    if re.search(r"read|list|search|grep|inspect|stat|show", s):
        return "LOW"
    return "MEDIUM"


def approval_required(risk):
    return risk in ("HIGH", "CRITICAL")


# ----------------------------------------------------------- loop detection

@dataclass
class TraceStep:
    index: int
    kind: str                    # tool_call | agent_step | handoff | observation
    name: str = ""
    args_key: str = ""           # stable serialization for repeat detection
    ok: bool = True


def parse_trace(raw):
    """Parse a JSON trace (list of step objects or {"steps": [...]}) into
    TraceSteps. Unknown shapes degrade to empty — never a fabricated trace."""
    if isinstance(raw, dict):
        raw = raw.get("steps") or raw.get("trace") or []
    if not isinstance(raw, list):
        return []
    steps = []
    for i, s in enumerate(raw):
        if not isinstance(s, dict):
            continue
        args = s.get("arguments") or s.get("args") or s.get("input") or ""
        try:
            key = json.dumps(args, sort_keys=True, default=str)[:400]
        except (TypeError, ValueError):
            key = str(args)[:400]
        steps.append(TraceStep(
            index=i,
            kind=str(s.get("kind") or s.get("type") or ("tool_call" if s.get("tool") or s.get("name") else "agent_step")),
            name=str(s.get("tool") or s.get("name") or ""),
            args_key=key,
            ok=bool(s.get("ok", s.get("success", s.get("status") in (None, "success", "warning")))),
        ))
    return steps


def detect_loops(steps, window=8, min_repeats=3):
    """Deterministic loop/anti-pattern detection over a trace.

    Reports: identical-call repeats (tool call loop), alternating ping-pong
    (delegation loop), unbounded retries on identical errors, no-progress
    cycles. Returns finding strings; [] == no loop evidence."""
    findings = []
    if not steps:
        return findings
    sig = [(s.kind, s.name, s.args_key) for s in steps]
    # identical consecutive repeats
    run, start = 1, 0
    for i in range(1, len(sig) + 1):
        if i < len(sig) and sig[i] == sig[i - 1]:
            run += 1
            continue
        if run >= min_repeats:
            findings.append(f"tool-call loop: step {sig[start][1] or sig[start][0]} repeated {run}x "
                            f"identically at indices {start}..{i-1} — no progress between retries")
        run, start = 1, i
    # ping-pong delegation between two agents
    names = [s.name for s in steps if s.kind in ("handoff", "agent_step") and s.name]
    for period in (2, 3):
        if len(names) >= period * min_repeats:
            block = names[:period]
            reps, i = 1, period
            while i + period <= len(names) and names[i:i + period] == block:
                reps, i = reps + 1, i + period
            if reps >= min_repeats:
                findings.append(f"delegation loop: {' <-> '.join(block)} cycle repeated {reps}x "
                                f"— mutual handoff without convergence")
    # unbounded error retries on the same target
    err_runs = {}
    for s in steps:
        if not s.ok:
            err_runs.setdefault((s.name, s.args_key), []).append(s.index)
    for (nm, _), idxs in err_runs.items():
        if len(idxs) > 3 and idxs == list(range(idxs[0], idxs[-1] + 1)):
            findings.append(f"retry storm: '{nm}' failed {len(idxs)}x consecutively without strategy change")
    # windowed no-progress: same block repeats with all-ok still no state change marker
    if len(steps) > window * 2:
        blocks = {}
        for i in range(0, len(steps) - window + 1, window):
            b = tuple(sig[i:i + window])
            blocks[b] = blocks.get(b, 0) + 1
        for b, c in blocks.items():
            if c >= 3:
                findings.append(f"context/step loop: identical {window}-step block recurs {c}x — likely context pollution")
    return findings


# ------------------------------------------------------------- context est.

def estimate_tokens(text):
    """Transparent heuristic (no platform token data): ~4 chars/token for ASCII,
    CJK counted per char. Marked as estimate by callers."""
    if not text:
        return 0
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff" or "\u3040" <= ch <= "\u30ff")
    other = len(text) - cjk
    return cjk + math.ceil(other / 4)


def audit_context_layers(layers):
    """layers: dict layer_name -> text. Returns findings + per-layer estimates."""
    findings, sizes = [], {}
    budget = 0
    for name, text in (layers or {}).items():
        text = text if isinstance(text, str) else ""
        tok = estimate_tokens(text)
        sizes[name] = tok
        budget += tok
        if name == "system" and tok > 1500:
            findings.append(f"system layer {tok} tok (est) — move depth into on-demand references")
        if len(text) > 20_000 and "file:" not in text and "://" not in text:
            findings.append(f"layer '{name}' inlines {tok} tok (est) with no file references — prefer references over inlining")
    for dup in _duplicate_blocks(layers or {}):
        findings.append(f"duplicated content across layers: {dup} — repeat-pollution")
    return findings, sizes, budget


def _duplicate_blocks(layers, min_len=200):
    out = []
    blocks = {}
    for name, text in layers.items():
        for block in re.split(r"\n\s*\n", str(text)):
            b = " ".join(block.split())
            if len(b) >= min_len:
                blocks.setdefault(b, []).append(name)
    for b, owners in blocks.items():
        if len(owners) > 1:
            out.append(f"'{b[:60]}…' in {'+'.join(sorted(set(owners)))}")
    return out


# ----------------------------------------------------------------- scoring

@dataclass
class ScoreCard:
    """Transparent weighted 0..100. Categories absent from the audit are
    excluded from the denominator — never scored as 0, never credited."""
    weights: dict = field(default_factory=dict)
    earned: dict = field(default_factory=dict)
    notes: dict = field(default_factory=dict)

    def add(self, category, points, max_points, weight=1.0, note=""):
        self.weights[category] = weight
        self.earned[category] = (points, max_points)
        self.notes[category] = note

    def skip(self, category, note="not applicable / not observable"):
        self.weights.setdefault(category, 1.0)
        self.notes[category] = note

    @property
    def total(self):
        num = den = 0.0
        for cat, w in self.weights.items():
            if cat not in self.earned:
                continue
            p, m = self.earned[cat]
            if m <= 0:
                continue
            num += w * (p / m)
            den += w
        return round(100 * num / den, 1) if den else 0.0

    def to_dict(self):
        return {
            "score": self.total,
            "categories": {c: {"earned": self.earned[c][0] if c in self.earned else None,
                               "max": self.earned[c][1] if c in self.earned else None,
                               "weight": self.weights.get(c, 0),
                               "status": "scored" if c in self.earned else "skipped",
                               "note": self.notes.get(c, "")}
                           for c in sorted(set(self.weights) | set(self.earned))},
        }


# ------------------------------------------------------------ report render

def findings_to_markdown(findings, title="Harness Audit"):
    lines = [f"# {title}", ""]
    if not findings:
        return "\n".join(lines + ["No findings.", ""])
    lines += ["| ID | Category | Severity | Component | Evidence | Fix | Fixable | Risk |",
              "|---|---|---|---|---|---|---|---|"]
    for f in findings:
        lines.append("| {id} | {category} | {severity} | {component} | {evidence} | {fix} "
                     "| {fixable} | {risk} |".format_map({
                         k: str(f.get(k, "")).replace("|", "\\|").replace("\n", " ")
                         for k in ("id", "category", "severity", "component",
                                   "evidence", "fix", "fixable", "risk")}))
    return "\n".join(lines) + "\n"


def load_json(path):
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"no such file: {p}")
    return json.loads(p.read_text(encoding="utf-8"))
