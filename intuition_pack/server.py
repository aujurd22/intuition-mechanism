"""MCP stdio server for the intuition-pack plugin (P139 architecture).

Tools exposed:
  pack_build(domain, charter, exemplars, verifier, source) -> version
  pack_get(domain)      -> the atomic pack JSON + prompt_block
  pack_list()           -> domains
  verify(domain, payload) -> EXECUTED mechanical verifier verdict + audit
  regression(domain)    -> mechanical gate report (PASS/FAIL)

Run:  py -3 -m intuition_pack.server
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP

from intuition_pack.pack import build_pack, Pack
from intuition_pack.store import get_store
from intuition_pack.verifiers import (run_verifier, VERIFIERS, score_candidates, needs_verification)
from intuition_pack.regression import mechanical_gate, load_testset
from intuition_pack.route import route

mcp = FastMCP("intuition-pack")


@mcp.tool()
def pack_build(domain: str, charter: str, exemplars: list,
               verifier_name: str, verifier_rule: str, source: str = "") -> str:
    """Build (or version-bump) a contrast-exemplar pack for a domain.

    exemplars: list of {"d": id, "inputs": {...}, "label": "RATIONAL"/"NOT",
               "note": "contrast role"}
    The pack is stored atomically; version increments automatically.
    """
    pack = build_pack(domain, charter, exemplars,
                      {"name": verifier_name, "rule": verifier_rule}, source)
    version = get_store().put(domain, pack.to_json())
    return json.dumps({"domain": domain, "version": version,
                       "exemplars": len(pack.exemplars)})


@mcp.tool()
def pack_get(domain: str) -> str:
    """Load the CURRENT pack for a domain — atomically, with its
    single-evidence-source prompt block ready for injection."""
    raw = get_store().get(domain)
    if raw is None:
        return json.dumps({"error": f"no pack for domain {domain!r}"})
    pack = Pack.from_json(raw)
    judge_prior = None
    try:
        land = json.load(open(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "p131_landscape_consolidated.json"), encoding="utf-8"))
        judge_prior = {
            "note": "P131 landscape: fast-classification carrier rates "
                    "(LLM layer, before mechanical verification)",
            "forced_choice_pooled": land.get("v4.1_forced", {}).get("rate"),
            "carriers": ["deepseek-v4.1-flash(forced)",
                         "doubao-seed-2.1-lite(forced)",
                         "deepseek-v4-flash(absolute)"],
        }
    except Exception:
        pass
    return json.dumps({"domain": domain, "version": pack.version,
                       "charter": pack.charter,
                       "prompt_block": pack.prompt_block(),
                       "verifier": pack.verifier.name,
                       "verifier_rule": pack.verifier.rule,
                       "judge_prior": judge_prior})


@mcp.tool()
def pack_list() -> str:
    return json.dumps({"domains": get_store().list()})


@mcp.tool()
def verify(domain: str, payload: dict) -> str:
    """EXECUTE the domain's registered mechanical verifier on a candidate.
    Returns verdict + full audit trail (value, residual, method).
    P138 rule: the agent runs this instead of reading raw numbers."""
    raw = get_store().get(domain)
    if raw is None:
        return json.dumps({"error": f"no pack for domain {domain!r}"})
    pack = Pack.from_json(raw)
    out = run_verifier(pack.verifier.name, payload)
    return json.dumps(out)


@mcp.tool()
def score(domain: str, candidates: list) -> str:
    """Jev `score` analogue: order candidates by P(RATIONAL), descending.
    Each item carries its typed choice distribution — the agent applies
    its own confidence threshold.  Candidates: [{"d": int}]."""
    return json.dumps({"scored": score_candidates(candidates)})


@mcp.tool()
def needs_verification_check(domain: str, verdict_json: str,
                             threshold: float = 0.9) -> str:
    """Jev-nouli-aligned abstain check: flag a verdict as ABSTAIN-candidate
    when its confidence sits below the agent's threshold.  The agent then
    escalates (deeper compute / human / another domain's verifier)."""
    out = json.loads(verdict_json)
    return json.dumps(needs_verification(out, threshold))


@mcp.tool()
def route_text(text: str) -> str:
    """Mechanical trigger: does this input touch a registered pack domain?
    Zero-LLM routing (mechanical hook > model self-trigger, per the
    measured reliability ranking).  Returns the matched domain or null."""
    store = get_store()
    packs = []
    for dom in store.list():
        raw = store.get(dom)
        if raw:
            try:
                packs.append(Pack.from_json(raw))
            except Exception:
                pass
    hit = route(text, packs)
    return json.dumps({"matched": hit[0] if hit else None,
                       "rule": hit[1] if hit else None})


@mcp.tool()
def regression(domain: str) -> str:
    """Run the mechanical regression gate (P138 protocol, deterministic
    half) over the domain's pack.  PASS required before deploying a
    pack version."""
    raw = get_store().get(domain)
    if raw is None:
        return json.dumps({"error": f"no pack for domain {domain!r}"})
    pack = Pack.from_json(raw)
    report = mechanical_gate(pack, load_testset())
    return json.dumps(report)


if __name__ == "__main__":
    mcp.run()
