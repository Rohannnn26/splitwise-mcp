"""MCP tools for Splitwise comment operations."""

from __future__ import annotations

from fastmcp import Context

from splitwise_mcp.app import mcp
from splitwise_mcp.client import SplitwiseAPIError
from splitwise_mcp.utils.formatters import format_comment, format_comment_list


@mcp.tool()
async def get_comments(expense_id: int, ctx: Context) -> str:
    """Get all comments on a Splitwise expense.

    Args:
        expense_id: The Splitwise expense ID.
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        comments = await client.get_comments(expense_id)
        return format_comment_list(comments)
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def create_comment(
    expense_id: int,
    content: str,
    ctx: Context,
) -> str:
    """Add a comment to a Splitwise expense.

    Args:
        expense_id: The Splitwise expense ID to comment on.
        content: The comment text.
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        comment = await client.create_comment(expense_id, content)
        return f"Comment added.\n{format_comment(comment)}"
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def delete_comment(comment_id: int, ctx: Context) -> str:
    """Delete a comment from a Splitwise expense.

    Args:
        comment_id: The comment ID to delete.
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        data = await client.delete_comment(comment_id)
        return f"Comment deleted (ID: {comment_id})."
    except SplitwiseAPIError as e:
        return f"Error: {e}"
