"""Expense models."""

from __future__ import annotations

from pydantic import BaseModel

from splitwise_mcp.models.comment import Comment
from splitwise_mcp.models.common import Share


class Repayment(BaseModel):
    """Who owes whom within one expense."""
    from_user: int | None = None
    to: int | None = None
    amount: str | None = None

    class Config:
        populate_by_name = True
        fields = {"from_user": {"alias": "from"}}


class ExpenseCategory(BaseModel):
    id: int | None = None
    name: str | None = None


class Receipt(BaseModel):
    large: str | None = None
    original: str | None = None


class Expense(BaseModel):
    id: int | None = None
    group_id: int | None = None
    friendship_id: int | None = None
    expense_bundle_id: int | None = None
    description: str | None = None
    repeats: bool | None = None
    repeat_interval: str | None = None
    email_reminder: bool | None = None
    email_reminder_in_advance: int | None = None
    next_repeat: str | None = None
    details: str | None = None
    comments_count: int | None = None
    payment: bool | None = None
    transaction_confirmed: bool | None = None
    cost: str | None = None
    currency_code: str | None = None
    repayments: list[Repayment] | None = None
    date: str | None = None
    created_at: str | None = None
    created_by: dict | None = None
    updated_at: str | None = None
    updated_by: dict | None = None
    deleted_at: str | None = None
    deleted_by: dict | None = None
    category: ExpenseCategory | None = None
    receipt: Receipt | None = None
    users: list[Share] | None = None
    comments: list[Comment] | None = None
