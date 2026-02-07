"""Common / shared models used across multiple domains."""

from __future__ import annotations

from pydantic import BaseModel


class Debt(BaseModel):
    """A debt between two users."""
    from_user: int | None = None
    to: int | None = None
    amount: str | None = None
    currency_code: str | None = None

    class Config:
        populate_by_name = True
        # Splitwise uses "from" which is a Python keyword
        fields = {"from_user": {"alias": "from"}}


class Balance(BaseModel):
    currency_code: str | None = None
    amount: str | None = None


class Currency(BaseModel):
    currency_code: str | None = None
    unit: str | None = None


class Share(BaseModel):
    """A user's share of an expense."""
    user: CommentUser | None = None
    user_id: int | None = None
    paid_share: str | None = None
    owed_share: str | None = None
    net_balance: str | None = None


class CommentUser(BaseModel):
    """Minimal user info embedded in comments / shares."""
    id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    picture: dict | None = None


class Category(BaseModel):
    id: int | None = None
    name: str | None = None
    icon: str | None = None
    icon_types: dict | None = None


class ParentCategory(BaseModel):
    id: int | None = None
    name: str | None = None
    icon: str | None = None
    icon_types: dict | None = None
    subcategories: list[Category] | None = None


# Rebuild Share to resolve forward reference to CommentUser
Share.model_rebuild()
