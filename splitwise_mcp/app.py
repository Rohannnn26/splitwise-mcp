"""Singleton FastMCP instance — imported by server.py and all tool modules.

This module holds the mcp instance + lifespan. It only imports from
client.py and config.py (which never import from here), avoiding circular deps.
"""

import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP

from splitwise_mcp.client import SplitwiseClient
from splitwise_mcp.config import Settings

# Walk up from this file to find .env at the project root
_project_root = Path(__file__).resolve().parent.parent
_env_path = _project_root / ".env"
load_dotenv(_env_path if _env_path.exists() else None)

logger = logging.getLogger("splitwise_mcp")
logging.basicConfig(level=logging.INFO, stream=sys.stderr)


@dataclass
class AppContext:
    """Shared state available to all tools via the MCP lifespan."""

    splitwise: SplitwiseClient


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Create and tear down the Splitwise HTTP client."""
    settings = Settings()
    client = SplitwiseClient(
        api_key=settings.splitwise_api_key,
        base_url=settings.splitwise_base_url,
    )
    logger.info("Splitwise MCP server starting — client connected")
    try:
        yield AppContext(splitwise=client)
    finally:
        await client.close()
        logger.info("Splitwise MCP server shutting down")


mcp = FastMCP("splitwise-mcp", lifespan=app_lifespan)
