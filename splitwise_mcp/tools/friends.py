"""MCP tools for Splitwise friend operations."""

from __future__ import annotations

from fastmcp import Context

from splitwise_mcp.app import mcp
from splitwise_mcp.client import SplitwiseAPIError
from splitwise_mcp.utils.formatters import (
    format_friend,
    format_friend_list,
    format_success,
)


@mcp.tool()
async def list_friends(ctx: Context) -> str:
    """List all Splitwise friends of the authenticated user with balances."""
    try:
        client = ctx.request_context.lifespan_context.splitwise
        friends = await client.get_friends()
        return format_friend_list(friends)
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def get_friend(friend_id: int, ctx: Context) -> str:
    """Get detailed information about a specific Splitwise friend.

    Args:
        friend_id: The Splitwise friend (user) ID.
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        friend = await client.get_friend(friend_id)
        return format_friend(friend)
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def add_friend(
    user_email: str,
    ctx: Context,
    user_first_name: str | None = None,
    user_last_name: str | None = None,
) -> str:
    """Add a friend on Splitwise by their email address.

    Args:
        user_email: Email address of the person to add.
        user_first_name: First name (optional, for new users).
        user_last_name: Last name (optional, for new users).
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        friend = await client.create_friend(
            user_email=user_email,
            user_first_name=user_first_name,
            user_last_name=user_last_name,
        )
        return f"Friend added.\n{format_friend(friend)}"
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def add_friends(
    friends: list[dict[str, str]],
    ctx: Context,
) -> str:
    """Add multiple friends at once on Splitwise.

    Args:
        friends: A list of dicts, each with "email", and optionally
                 "first_name" and "last_name".
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        data = await client.create_friends(friends)
        return format_success(data)
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def delete_friend(friend_id: int, ctx: Context) -> str:
    """Remove a friend from Splitwise. You must be settled up first.

    Args:
        friend_id: The Splitwise friend (user) ID to remove.
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        data = await client.delete_friend(friend_id)
        return format_success(data)
    except SplitwiseAPIError as e:
        return f"Error: {e}"
