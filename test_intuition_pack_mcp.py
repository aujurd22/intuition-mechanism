"""MCP server smoke test: spawn the stdio server, list tools, call
pack_get + verify over the real wire (official mcp SDK client)."""
import asyncio
import json
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "intuition_pack.server"],
        cwd=os.path.dirname(os.path.abspath(__file__)))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = [t.name for t in tools.tools]
            print("tools:", names)
            assert set(names) >= {"pack_build", "pack_get", "pack_list",
                                  "verify", "regression"}

            res = await session.call_tool("pack_list", {})
            print("pack_list:", res.content[0].text[:120])

            res = await session.call_tool("pack_get",
                                          {"domain": "ramanujan-sixrow"})
            d = json.loads(res.content[0].text)
            print("pack_get: version", d.get("version"),
                  "verifier", d.get("verifier"),
                  "prompt_block bytes", len(d.get("prompt_block", "")))
            assert d.get("version") >= 1

            res = await session.call_tool(
                "verify", {"domain": "ramanujan-sixrow", "payload": {"d": 35}})
            v = json.loads(res.content[0].text)
            print("verify(35):", v["verdict"], "value", round(v["value"], 3))
            assert v["verdict"] == "NOT"

            res = await session.call_tool("regression",
                                          {"domain": "ramanujan-sixrow"})
            rep = json.loads(res.content[0].text)
            print("regression PASS:", rep["PASS"])
            assert rep["PASS"]
    print("MCP SMOKE PASS")


if __name__ == "__main__":
    asyncio.run(main())
