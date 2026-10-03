"""MCP stdio server for the hallucination-gate plugin (v1).
Tools: gate_claim, gate_batch, audit_tail.  Reuses intuition_pack verifiers.
Register in the client config:
  {
    "mcpServers": {
      "hallucination-gate": {
        "command": "python",
        "args": ["<repo>/hallucination_gate/server.py"]
      }
    }
  }
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hallucination_gate.gate import gate_claim, gate_batch, audit_tail  # noqa: E402

# minimal stdio MCP loop (JSON-RPC 2.0, tools/list + tools/call)
def tool_defs():
    return [
        {"name": "gate_claim", "description": "Route an LLM claim through the "
         "hallucination toll booth. kind: sixrow|fact|rule|novel. Returns "
         "VERIFIED/REFUTED/ABSTAIN/SPECULATION + evidence.",
         "inputSchema": {"type": "object", "properties": {
             "claim": {"type": "string"},
             "kind": {"type": "string", "enum": ["auto", "sixrow", "fact", "rule", "novel"]},
             "payload": {"type": "object"}},
             "required": ["claim"]}},
        {"name": "gate_batch", "description": "Gate a list of claims.",
         "inputSchema": {"type": "object", "properties": {
             "claims": {"type": "array"}}, "required": ["claims"]}},
        {"name": "audit_tail", "description": "Last n toll-booth receipts.",
         "inputSchema": {"type": "object", "properties": {"n": {"type": "integer"}}}},
    ]


def main():
    for line in sys.stdin:
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = req.get("method", "")
        rid = req.get("id")
        if method == "initialize":
            resp = {"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "hallucination-gate", "version": "1.0"}}}
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            resp = {"jsonrpc": "2.0", "id": rid, "result": {"tools": tool_defs()}}
        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})
            if name == "gate_claim":
                out = gate_claim(args.get("claim", ""), args.get("kind", "auto"),
                                 args.get("payload"))
            elif name == "gate_batch":
                out = {"receipts": gate_batch(args.get("claims", []))}
            else:
                out = {"receipts": audit_tail(int(args.get("n", 10)))}
            resp = {"jsonrpc": "2.0", "id": rid, "result": {
                "content": [{"type": "text", "text": json.dumps(out, ensure_ascii=False)}]}}
        else:
            continue
        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
