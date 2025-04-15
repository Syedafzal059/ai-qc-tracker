# my_server.py
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Dummy")

@mcp.tool()
def ping() -> str:
    return "pong"

if __name__ == "__main__":
    print("✅ Dummy MCP server running...", flush=True)
    mcp.run()
