"""MCP tools for Splitwise currencies and categories."""

from __future__ import annotations

from fastmcp import Context

from splitwise_mcp.app import mcp
from splitwise_mcp.client import SplitwiseAPIError
from splitwise_mcp.utils.formatters import format_category_list, format_currency_list


def _get_client(ctx: Context):
    request_context = ctx.request_context
    if request_context is None or request_context.lifespan_context is None:
        raise RuntimeError("MCP session not initialized")
    return request_context.lifespan_context.splitwise


@mcp.tool()
async def list_currencies(ctx: Context) -> str:
    """List all currencies supported by Splitwise."""
    try:
        client = _get_client(ctx)
        currencies = await client.get_currencies()
        return format_currency_list(currencies)
    except SplitwiseAPIError as e:
        return f"Error: {e}"
    except RuntimeError as e:
        return f"Error: {e}"


@mcp.tool()
async def list_categories(ctx: Context) -> str:
    """List all expense categories available on Splitwise, including subcategories."""
    try:
        client = _get_client(ctx)
        categories = await client.get_categories()
        return format_category_list(categories)
    except SplitwiseAPIError as e:
        return f"Error: {e}"
    except RuntimeError as e:
        return f"Error: {e}"
