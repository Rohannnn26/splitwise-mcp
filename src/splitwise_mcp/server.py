"""Splitwise MCP Server — entry point.

Imports the shared mcp instance from app.py, registers all tools,
and provides the CLI entry point.
"""

from splitwise_mcp.app import mcp  # noqa: F401

# Register all tools (side-effect imports)
import splitwise_mcp.tools  # noqa: E402, F401


def main() -> None:
    """CLI entry point."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
