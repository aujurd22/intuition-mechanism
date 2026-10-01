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
from intuition_pack.verifiers import run_verifier, VERIFIERS
from intuition_pack.regression import mechanical_gate, load_testset

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
    return json.dumps({"domain": domain, "version": pack.version,
                       "charter": pack.charter,
                       "prompt_block": pack.prompt_block(),
                       "verifier": pack.verifier.name,
                       "verifier_rule": pack.verifier.rule})


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
