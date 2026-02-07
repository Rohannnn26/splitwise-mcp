"""MCP tools for Splitwise user operations."""

from __future__ import annotations

from mcp.server.fastmcp import Context

from splitwise_mcp.app import mcp
from splitwise_mcp.client import SplitwiseAPIError
from splitwise_mcp.utils.formatters import format_user


@mcp.tool()
async def get_current_user(ctx: Context) -> str:
    """Get the currently authenticated Splitwise user's profile information."""
    try:
        client = ctx.request_context.lifespan_context.splitwise
        user = await client.get_current_user()
        return format_user(user)
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def get_user(user_id: int, ctx: Context) -> str:
    """Get profile information for a specific Splitwise user by their ID.

    Args:
        user_id: The Splitwise user ID to look up.
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        user = await client.get_user(user_id)
        return format_user(user)
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def update_user(
    user_id: int,
    ctx: Context,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    default_currency: str | None = None,
    locale: str | None = None,
) -> str:
    """Update a Splitwise user's profile information.

    Args:
        user_id: The Splitwise user ID to update.
        first_name: New first name.
        last_name: New last name.
        email: New email address.
        default_currency: New default currency code (e.g. "USD", "INR").
        locale: New locale (e.g. "en").
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        user = await client.update_user(
            user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            default_currency=default_currency,
            locale=locale,
        )
        return f"User updated successfully.\n{format_user(user)}"
    except SplitwiseAPIError as e:
        return f"Error: {e}"
