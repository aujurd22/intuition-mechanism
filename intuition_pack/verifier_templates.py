"""Verifier TEMPLATES (P149): the generalization lever — new domains
become CONFIGURATION (template + params) instead of new code.

Three shapes cover most agent-verifier needs beyond the existing
execution/predicate/census trio:

  schema_check    JSON-schema-subset compliance with structured
                  violation report (required/type/enum/range/pattern)
  set_match       exact/set equality between produced and expected
                  collections (dedup, retrieval ground truth)
  all_match       list of regex constraints over string fields
"""
import json
import re


def _type_ok(value, t):
    return {
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
    }.get(t, lambda v: True)(value)


def _check_node(value, schema, path, violations):
    t = schema.get("type")
    if t and not _type_ok(value, t):
        violations.append({"path": path, "constraint": "type:" + t,
                           "got": type(value).__name__})
        return                      # deeper checks meaningless on wrong type
    if "enum" in schema and value not in schema["enum"]:
        violations.append({"path": path, "constraint": "enum",
                           "got": value, "allowed": schema["enum"]})
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            violations.append({"path": path, "constraint": "minimum:"
                               + str(schema["minimum"]), "got": value})
        if "maximum" in schema and value > schema["maximum"]:
            violations.append({"path": path, "constraint": "maximum:"
                               + str(schema["maximum"]), "got": value})
    if isinstance(value, str) and "pattern" in schema:
        if not re.search(schema["pattern"], value):
            violations.append({"path": path, "constraint": "pattern:"
                               + schema["pattern"], "got": value})
    if isinstance(value, dict) and schema.get("type") == "object":
        for req in schema.get("required", []):
            if req not in value:
                violations.append({"path": path + "." + req if path else req,
                                   "constraint": "required", "got": "missing"})
        for key, sub in schema.get("properties", {}).items():
            if key in value:
                _check_node(value[key], sub,
                            path + "." + key if path else key, violations)
    if isinstance(value, list) and schema.get("type") == "array":
        if "items" in schema:
            for i, el in enumerate(value):
                _check_node(el, schema["items"], f"{path}[{i}]", violations)
        if schema.get("uniqueItems"):
            marks = [json.dumps(x, sort_keys=True) for x in value]
            if len(set(marks)) != len(marks):
                violations.append({"path": path, "constraint": "uniqueItems"})


def schema_check(payload: dict) -> dict:
    """payload: {"object": <json value>, "schema": <json-schema-subset>,
    "name": optional domain label}.  Returns structured violations."""
    obj, schema = payload["object"], payload["schema"]
    violations = []
    _check_node(obj, schema, "", violations)
    passed = not violations
    return {"verdict": "PASS" if passed else "FAIL",
            "confidence": 1.0 - 1e-9,
            "typed": {"kind": "choice",
                      "options": {"PASS": 1.0 - 1e-9 if passed else 1e-9,
                                  "FAIL": 1e-9 if passed else 1.0 - 1e-9}},
            "confidence_basis": "direct_execution",
            "violations": violations,
            "violation_count": len(violations)}


def set_match(payload: dict) -> dict:
    """payload: {"produced": [...], "expected": [...],
    "mode": "exact"|"set"|"multiset"}"""
    produced, expected = payload["produced"], payload["expected"]
    mode = payload.get("mode", "set")
    if mode == "exact":
        ok = produced == expected
    elif mode == "set":
        ok = sorted(json.dumps(x, sort_keys=True) for x in produced) == \
             sorted(json.dumps(x, sort_keys=True) for x in expected)
    else:
        ok = len(produced) == len(expected)
    return {"verdict": "MATCH" if ok else "MISMATCH",
            "confidence": 1.0 - 1e-9,
            "typed": {"kind": "choice",
                      "options": {"MATCH": 1.0 - 1e-9 if ok else 1e-9,
                                  "MISMATCH": 1e-9 if ok else 1.0 - 1e-9}},
            "confidence_basis": "direct_execution"}


def all_match(payload: dict) -> dict:
    """payload: {"text": str, "patterns": [{"name", "regex"}]} — all must
    match."""
    text = payload["text"]
    results = []
    for p in payload["patterns"]:
        ok = re.search(p["regex"], text) is not None
        results.append({"name": p["name"], "ok": ok})
    failed = [r["name"] for r in results if not r["ok"]]
    return {"verdict": "PASS" if not failed else "FAIL",
            "confidence": 1.0 - 1e-9,
            "typed": {"kind": "choice",
                      "options": {"PASS": 1.0 - 1e-9 if not failed else 1e-9,
                                  "FAIL": 1e-9 if not failed else 1.0 - 1e-9}},
            "confidence_basis": "direct_execution",
            "failed_patterns": failed,
            "per_pattern": results}
