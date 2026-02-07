"""MCP tools for Splitwise notifications."""

from __future__ import annotations

from mcp.server.fastmcp import Context

from splitwise_mcp.app import mcp
from splitwise_mcp.client import SplitwiseAPIError
from splitwise_mcp.utils.formatters import format_notification_list


@mcp.tool()
async def get_notifications(
    ctx: Context,
    updated_after: str | None = None,
    limit: int | None = None,
) -> str:
    """Get Splitwise notifications for the authenticated user.

    Args:
        updated_after: ISO date string — only notifications after this time.
        limit: Maximum number of notifications to return.
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        notifications = await client.get_notifications(
            updated_after=updated_after,
            limit=limit,
        )
        return format_notification_list(notifications)
    except SplitwiseAPIError as e:
        return f"Error: {e}"
