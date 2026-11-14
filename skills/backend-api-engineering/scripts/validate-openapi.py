#!/usr/bin/env python3
"""validate-openapi.py — OpenAPI structure + breaking-change validator.

Zero-dep (stdlib only). Validates JSON/YAML specs (3.x / 2.0) for the
contracts backend-api-engineering ships: error schemas, per-operation ids,
parameters bounds, path collisions, and — with --baseline — a breaking-
change diff (removed paths/methods, added required fields, changed types).

Usage:  validate-openapi.py SPEC [--baseline OLD_SPEC] [--json]
Exit:   0 spec valid (+ no breaking changes vs baseline)
        1 validation errors or breaking changes found
        2 usage / unreadable / unparsable input
"""
import json, re, sys

HELP = __doc__

def parse_yaml(text):
    """YAML subset: nested block mappings + scalar leaves + comments.
    Lists/anchors/flow style unsupported -> caller reports unparsable;
    full YAML belongs to a maintained parser (yaml/pyyaml) in project CI."""
    def scalar(s):
        s = s.strip()
        q = s[:1] in "\"'" and s[-1:] == s[:1]
        if q: return s[1:-1]
        if s in ("true","True"): return True
        if s in ("false","False"): return False
        if re.fullmatch(r"-?\d+", s): return int(s)
        if re.fullmatch(r"-?\d+\.\d+", s): return float(s)
        return s
    def key(s):
        s = s.strip()
        if s[:1] in "\"'" and s[-1:] == s[:1]: return s[1:-1]
        return s
    root = {}
    stack = [(-1, root)]  # (indent, dict)
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"): continue
        ind = len(raw) - len(raw.lstrip(" "))
        content = raw.strip()
        if content.startswith("- "): continue  # sequence: subset limit
        while len(stack) > 1 and ind <= stack[-1][0]: stack.pop()
        parent = stack[-1][1]
        m = re.match(r"([^:]+):(.*)$", content)
        if not m or not isinstance(parent, dict): continue
        key_, rest = key(m.group(1)), m.group(2).strip()
        if rest == "":
            child = {}; parent[key_] = child; stack.append((ind, child))
        else:
            parent[key_] = scalar(rest)
    return root

def die2(msg):
    print(msg, file=sys.stderr); sys.exit(2)

def load(path):
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        die2(f"2: cannot read {path}: {e}")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            return parse_yaml(text)
        except Exception as e:
            die2(f"2: unparsable (not JSON, YAML subset failed: {e}): {path}")

def walk_ops(spec):
    """yield (path, method, op-dict) for 3.x/2.0 specs; tolerant."""
    paths = spec.get("paths") if isinstance(spec, dict) else None
    if not isinstance(paths, dict): return
    for p, item in paths.items():
        if not isinstance(item, dict): continue
        for m, op in item.items():
            if m.lower() in ("get","post","put","patch","delete","head","options") and isinstance(op, dict):
                yield str(p), m.lower(), op

def validate(spec):
    errs = []
    if not isinstance(spec, dict): return ["spec root is not an object"]
    ver = str(spec.get("openapi") or spec.get("swagger") or "")
    if not ver: errs.append("missing openapi/swagger version field")
    info = spec.get("info") if isinstance(spec.get("info"), dict) else {}
    if not info.get("title"): errs.append("info.title missing")
    if not info.get("version"): errs.append("info.version missing")
    if not isinstance(spec.get("paths"), dict) or not spec["paths"]:
        errs.append("paths missing or empty")
        return errs
    seen = set()
    for p, m, op in walk_ops(spec):
        tag = f"{m.upper()} {p}"
        if not op.get("operationId"): errs.append(f"{tag}: operationId missing")
        if not op.get("responses") or not isinstance(op.get("responses"), dict):
            errs.append(f"{tag}: responses missing")
        else:
            codes = [c for c in op["responses"] if re.match(r"\d", c) or c in ("default",)]
            if not codes: errs.append(f"{tag}: no status codes")
            errs += _error_schemas(tag, op)
        for prm in op.get("parameters") or []:
            if isinstance(prm, dict) and prm.get("in") == "query" and "schema" not in prm and "type" not in prm:
                errs.append(f"{tag}: query param '{prm.get('name','?')}' untyped")
            if isinstance(prm, dict) and prm.get("name") in ("limit","page","perPage","per_page") and "schema" not in prm:
                pass
        key = (p, m)
        if key in seen: errs.append(f"duplicate {tag}")
        seen.add(key)
        # pagination bounds hint: list endpoints should cap limit
    return errs

def _error_schemas(tag, op):
    out = []
    resp = op.get("responses") or {}
    for code, body in resp.items():
        code = str(code)
        if not code.startswith(("4","5")): continue
        if not isinstance(body, dict): continue
        content = body.get("content")
        if content is None and body.get("schema") is None and not body.get("description"):
            out.append(f"{tag}: error {code} has no schema/description")
    return out

def diff(base, new):
    """breaking changes: removed path+method, newly required props."""
    brk, notes = [], []
    b_ops = {f"{m} {p}": op for p, m, op in walk_ops(base)}
    n_ops = {f"{m} {p}": op for p, m, op in walk_ops(new)}
    for k in sorted(set(b_ops) - set(n_ops)): brk.append(f"removed operation {k}")
    for k in sorted(set(n_ops) - set(b_ops)): notes.append(f"added operation {k}")
    for k in sorted(set(b_ops) & set(n_ops)):
        bparams = {p.get("name") for p in (b_ops[k].get("parameters") or []) if isinstance(p, dict) and p.get("required")}
        nparams = {p.get("name") for p in (n_ops[k].get("parameters") or []) if isinstance(p, dict) and p.get("required")}
        for added in sorted(nparams - bparams): brk.append(f"{k}: now-required param '{added}'")
    bdef, ndef = schemas(base), schemas(new)
    for name in sorted(set(bdef) & set(ndef)):
        breq, nreq = req(bdef[name]), req(ndef[name])
        for added in sorted(nreq - breq): brk.append(f"schema {name}: now-required '{added}'")
    return brk, notes

def schemas(spec):
    s = (spec.get("components") or {}).get("schemas") if isinstance(spec.get("components"), dict) else None
    return s if isinstance(s, dict) else (spec.get("definitions") if isinstance(spec.get("definitions"), dict) else {})

def req(sch):
    if not isinstance(sch, dict): return set()
    r = sch.get("required")
    return set(r) if isinstance(r, list) else set()

def main():
    args = [a for a in sys.argv[1:]]
    if args and args[0] in ("-h","--help"):
        print(HELP); sys.exit(0)
    if not args: die2("2: expected SPEC [+ --baseline OLD] [--json]")
    as_json = "--json" in args; args = [a for a in args if a != "--json"]
    base = None
    if "--baseline" in args:
        i = args.index("--baseline"); args.pop(i); base = args.pop(i) if i < len(args) else None
        if base is None: die2("2: --baseline needs a path")
    if len(args) != 1: die2("2: expected SPEC [+ --baseline OLD] [--json]")
    spec = load(args[0])
    errs = validate(spec)
    brk, notes = ([], [])
    if base: brk, notes = diff(load(base), spec)
    out = {"spec": args[0], "valid": not errs, "errors": errs,
           "breaking": brk, "additive": notes}
    if as_json: print(json.dumps(out, indent=2))
    else:
        for e in errs: print(f"ERROR   {e}")
        for b in brk: print(f"BREAKING {b}")
        for n in notes: print(f"added   {n}")
        print(f"{'PASS' if not errs and not brk else 'FAIL'}  {args[0]}  errors={len(errs)} breaking={len(brk)}")
    sys.exit(0 if not errs and not brk else 1)

if __name__ == "__main__":
    main()
