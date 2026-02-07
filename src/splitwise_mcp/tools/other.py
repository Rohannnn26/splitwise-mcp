"""MCP tools for Splitwise currencies and categories."""

from __future__ import annotations

from mcp.server.fastmcp import Context

from splitwise_mcp.app import mcp
from splitwise_mcp.client import SplitwiseAPIError
from splitwise_mcp.utils.formatters import format_category_list, format_currency_list


@mcp.tool()
async def list_currencies(ctx: Context) -> str:
    """List all currencies supported by Splitwise."""
    try:
        client = ctx.request_context.lifespan_context.splitwise
        currencies = await client.get_currencies()
        return format_currency_list(currencies)
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def list_categories(ctx: Context) -> str:
    """List all expense categories available on Splitwise, including subcategories."""
    try:
        client = ctx.request_context.lifespan_context.splitwise
        categories = await client.get_categories()
        return format_category_list(categories)
    except SplitwiseAPIError as e:
        return f"Error: {e}"
