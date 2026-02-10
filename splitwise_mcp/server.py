"""Splitwise MCP Server — entry point.

Imports the shared mcp instance from app.py, registers all tools,
and provides the CLI entry point.
"""

import os

from splitwise_mcp.app import mcp  # noqa: F401

# Register all tools (side-effect imports)
import splitwise_mcp.tools  # noqa: E402, F401


def main() -> None:
    """CLI entry point."""
    # Use SSE transport for cloud deployment (Render), stdio for local dev
    transport = os.getenv("MCP_TRANSPORT", "sse")
    
    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        # SSE mode for Render - reads PORT from environment
        port = int(os.getenv("PORT", "8000"))
        mcp.run(transport="sse", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
