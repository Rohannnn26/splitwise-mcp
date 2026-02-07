"""MCP tools for Splitwise group operations."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from splitwise_mcp.app import mcp
from splitwise_mcp.client import SplitwiseAPIError
from splitwise_mcp.utils.formatters import (
    format_group,
    format_group_list,
    format_success,
)


@mcp.tool()
async def list_groups(ctx: Context) -> str:
    """List all Splitwise groups the authenticated user belongs to."""
    try:
        client = ctx.request_context.lifespan_context.splitwise
        groups = await client.get_groups()
        return format_group_list(groups)
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def get_group(group_id: int, ctx: Context) -> str:
    """Get detailed information about a specific Splitwise group.

    Args:
        group_id: The Splitwise group ID.
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        group = await client.get_group(group_id)
        return format_group(group)
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def create_group(
    name: str,
    ctx: Context,
    group_type: str = "other",
    simplify_by_default: bool = False,
    users: list[dict[str, Any]] | None = None,
) -> str:
    """Create a new Splitwise group.

    Args:
        name: Name of the new group.
        group_type: Group type — "apartment", "house", "trip", or "other".
        simplify_by_default: Whether to simplify debts in the group.
        users: Optional list of users to add. Each dict should have keys like
               "user_id", "first_name", "last_name", "email".
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        group = await client.create_group(
            name=name,
            group_type=group_type,
            simplify_by_default=simplify_by_default,
            users=users,
        )
        return f"Group created.\n{format_group(group)}"
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def delete_group(group_id: int, ctx: Context) -> str:
    """Delete a Splitwise group. The group can be restored later.

    Args:
        group_id: The Splitwise group ID to delete.
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        data = await client.delete_group(group_id)
        return format_success(data)
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def restore_group(group_id: int, ctx: Context) -> str:
    """Restore a previously deleted Splitwise group.

    Args:
        group_id: The Splitwise group ID to restore.
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        data = await client.undelete_group(group_id)
        return format_success(data)
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def add_user_to_group(
    group_id: int,
    ctx: Context,
    user_id: int | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
) -> str:
    """Add a user to a Splitwise group. Provide either user_id or email.

    Args:
        group_id: The Splitwise group ID.
        user_id: Existing Splitwise user ID to add.
        first_name: First name (for inviting by email).
        last_name: Last name (for inviting by email).
        email: Email address to invite.
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        data = await client.add_user_to_group(
            group_id,
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        return format_success(data)
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def remove_user_from_group(
    group_id: int,
    user_id: int,
    ctx: Context,
) -> str:
    """Remove a user from a Splitwise group.

    Args:
        group_id: The Splitwise group ID.
        user_id: The Splitwise user ID to remove.
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        data = await client.remove_user_from_group(group_id, user_id)
        return format_success(data)
    except SplitwiseAPIError as e:
        return f"Error: {e}"
