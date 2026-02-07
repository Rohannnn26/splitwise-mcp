"""MCP tools for Splitwise expense operations."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import Context

from splitwise_mcp.app import mcp
from splitwise_mcp.client import SplitwiseAPIError
from splitwise_mcp.utils.formatters import (
    format_expense,
    format_expense_list,
    format_success,
)


@mcp.tool()
async def list_expenses(
    ctx: Context,
    group_id: int | None = None,
    friend_id: int | None = None,
    dated_after: str | None = None,
    dated_before: str | None = None,
    updated_after: str | None = None,
    updated_before: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> str:
    """List Splitwise expenses, optionally filtered by group, friend, or date.

    Args:
        group_id: Filter by group ID.
        friend_id: Filter by friend (user) ID.
        dated_after: ISO date string — only expenses after this date.
        dated_before: ISO date string — only expenses before this date.
        updated_after: ISO date string — only expenses updated after this.
        updated_before: ISO date string — only expenses updated before this.
        limit: Maximum number of expenses to return.
        offset: Number of expenses to skip (for pagination).
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        expenses = await client.get_expenses(
            group_id=group_id,
            friend_id=friend_id,
            dated_after=dated_after,
            dated_before=dated_before,
            updated_after=updated_after,
            updated_before=updated_before,
            limit=limit,
            offset=offset,
        )
        return format_expense_list(expenses)
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def get_expense(expense_id: int, ctx: Context) -> str:
    """Get full details of a specific Splitwise expense.

    Args:
        expense_id: The Splitwise expense ID.
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        expense = await client.get_expense(expense_id)
        return format_expense(expense)
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def create_expense(
    cost: str,
    description: str,
    ctx: Context,
    group_id: int | None = None,
    split_equally: bool = False,
    currency_code: str = "USD",
    category_id: int | None = None,
    date: str | None = None,
    repeat_interval: str = "never",
    details: str | None = None,
    users: list[dict[str, Any]] | None = None,
) -> str:
    """Create a new expense on Splitwise.

    Args:
        cost: Total cost as a string (e.g. "25.00").
        description: Short description of the expense.
        group_id: Group to add the expense to (optional).
        split_equally: If True, split equally among group members.
        currency_code: Currency code (default "USD").
        category_id: Expense category ID (optional).
        date: ISO date string for the expense date.
        repeat_interval: One of "never", "weekly", "fortnightly", "monthly", "yearly".
        details: Additional notes about the expense.
        users: Custom split — list of dicts with keys like "user_id",
               "paid_share", "owed_share". Required if split_equally is False
               and no group_id is given.
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        data = await client.create_expense(
            cost=cost,
            description=description,
            group_id=group_id,
            split_equally=split_equally,
            currency_code=currency_code,
            category_id=category_id,
            date=date,
            repeat_interval=repeat_interval,
            details=details,
            users=users,
        )
        # create_expense returns {"expenses": [...]} on success
        expenses = data.get("expenses") or []
        if expenses:
            return f"Expense created.\n{format_expense(expenses[0])}"
        return f"Expense created.\n{data}"
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def update_expense(
    expense_id: int,
    ctx: Context,
    cost: str | None = None,
    description: str | None = None,
    group_id: int | None = None,
    currency_code: str | None = None,
    category_id: int | None = None,
    date: str | None = None,
    repeat_interval: str | None = None,
    details: str | None = None,
    users: list[dict[str, Any]] | None = None,
) -> str:
    """Update an existing Splitwise expense.

    Args:
        expense_id: The Splitwise expense ID to update.
        cost: New total cost.
        description: New description.
        group_id: Change the group.
        currency_code: Change the currency.
        category_id: Change the category.
        date: New date (ISO format).
        repeat_interval: New repeat interval.
        details: New notes.
        users: New custom split (list of dicts with user_id, paid_share, owed_share).
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        data = await client.update_expense(
            expense_id,
            cost=cost,
            description=description,
            group_id=group_id,
            currency_code=currency_code,
            category_id=category_id,
            date=date,
            repeat_interval=repeat_interval,
            details=details,
            users=users,
        )
        expenses = data.get("expenses") or []
        if expenses:
            return f"Expense updated.\n{format_expense(expenses[0])}"
        return f"Expense updated.\n{data}"
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def delete_expense(expense_id: int, ctx: Context) -> str:
    """Delete a Splitwise expense. It can be restored later.

    Args:
        expense_id: The Splitwise expense ID to delete.
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        data = await client.delete_expense(expense_id)
        return format_success(data)
    except SplitwiseAPIError as e:
        return f"Error: {e}"


@mcp.tool()
async def restore_expense(expense_id: int, ctx: Context) -> str:
    """Restore a previously deleted Splitwise expense.

    Args:
        expense_id: The Splitwise expense ID to restore.
    """
    try:
        client = ctx.request_context.lifespan_context.splitwise
        data = await client.undelete_expense(expense_id)
        return format_success(data)
    except SplitwiseAPIError as e:
        return f"Error: {e}"
