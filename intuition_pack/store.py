"""Pack storage: atomic loads, versioned writes.

ARCHITECTURE (P139, revised by the P140 integration probe):
  - AUTHORITY: LocalFileStore (packs/*.json, atomic replace, version bump).
  - AUDIT MIRROR: flymemory compartment "intuition-packs" receives a
    compact audit record per version (domain, version, charter, source,
    exemplar count) — NOT the full JSON: the P140 probe measured that
    flymemory's dedup/merge semantics (designed for conversational
    memory) REJECT same-key updates (novelty 0.00) and MERGE near-
    identical neighbors into one entry, destroying pack versioning.
    Verdicts are kept queryable for audit; the pack bytes live locally.
"""
import json
import os
import re
import time
import urllib.request

from .pack import Pack


_DEFAULT_ROOT = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "packs")


class LocalFileStore:
    def __init__(self, root=None):
        # default: <repo>/packs — independent of the MCP launch cwd
        self.root = root or os.environ.get("INTUITION_PACK_ROOT") or _DEFAULT_ROOT
        os.makedirs(self.root, exist_ok=True)

    def _path(self, domain):
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in domain)
        return os.path.join(self.root, f"{safe}.json")

    def put(self, domain: str, pack_json: str) -> int:
        p = self._path(domain)
        version = 1
        if os.path.exists(p):
            old = Pack.from_json(open(p, encoding="utf-8").read())
            version = old.version + 1
            d = json.loads(pack_json)
            d["version"] = version
            pack_json = json.dumps(d, indent=1)
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(pack_json)
        os.replace(tmp, p)          # atomic on same volume
        self._audit(domain, version, pack_json)
        return version

    def _audit(self, domain, version, pack_json):
        """Best-effort compact audit record into flymemory."""
        try:
            s = FlyMemoryStore()
            s._ensure_init()
        except Exception:
            return
        d = json.loads(pack_json)
        record = (f"[PACK-AUDIT:{domain}] v{version} "
                  f"exemplars={len(d.get('exemplars', []))} "
                  f"verifier={d.get('verifier', {}).get('name')} "
                  f"source={d.get('source', '')} "
                  f"charter={d.get('charter', '')[:120]}")
        try:
            s._call_tool("flymemory_remember", {
                "text": record, "tags": "intuition-pack-audit,pack",
                "compartment": "intuition-packs",
                "state_key": f"intuition-pack-audit.{domain}.v{version}"})
        except Exception:
            pass  # audit is best-effort; authority is the local file

    def get(self, domain: str):
        p = self._path(domain)
        if not os.path.exists(p):
            return None
        return open(p, encoding="utf-8").read()

    def list(self):
        if not os.path.isdir(self.root):
            return []
        return [f[:-5] for f in os.listdir(self.root) if f.endswith(".json")]


class FlyMemoryStore:
    """flymemory HTTP MCP client.

    P140 PROBE VERDICT: NOT viable for versioned pack storage — same-key
    updates are rejected by the novelty gate ([REJECTED] too similar),
    near-identical neighbors are MERGED into one entry ([STRENGTHENED],
    version destroyed).  Kept for the audit mirror and as a client for
    flymemory-native tools; do not store pack bytes here.
    """

    def __init__(self, url="http://127.0.0.1:8765/mcp",
                 compartment="intuition-packs", timeout=10):
        self.url = url
        self.compartment = compartment
        self.timeout = timeout
        self._rid = 0
        self._init = None

    def _rpc(self, method, params):
        self._rid += 1
        body = json.dumps({"jsonrpc": "2.0", "id": self._rid,
                           "method": method, "params": params}).encode()
        req = urllib.request.Request(
            self.url, data=body, method="POST",
            headers={"Content-Type": "application/json",
                     "Accept": "application/json, text/event-stream"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            raw = r.read().decode()
        if raw.startswith("event:") or "\ndata:" in raw or raw.startswith("data:"):
            for line in raw.splitlines():
                if line.startswith("data:"):
                    return json.loads(line[5:].strip())
            raise RuntimeError("no data line in SSE response")
        return json.loads(raw)

    def _ensure_init(self):
        if self._init is None:
            self._rpc("initialize", {
                "protocolVersion": "2024-11-05", "capabilities": {},
                "clientInfo": {"name": "intuition-pack", "version": "1.0"}})
            try:
                self._rpc("notifications/initialized", {})
            except Exception:
                pass
            self._init = True

    def _call_tool(self, name, arguments):
        self._ensure_init()
        resp = self._rpc("tools/call", {"name": name, "arguments": arguments})
        if "error" in resp:
            raise RuntimeError(resp["error"])
        content = resp.get("result", {}).get("content", [])
        return "\n".join(c.get("text", "") for c in content
                         if c.get("type") == "text")

    def probe(self) -> bool:
        try:
            self._ensure_init()
            self._rpc("tools/list", {})
            return True
        except Exception:
            return False


def get_store():
    return LocalFileStore()
