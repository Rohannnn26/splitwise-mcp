"""Group models."""

from __future__ import annotations

from pydantic import BaseModel

from splitwise_mcp.models.common import Balance, Debt


class GroupMember(BaseModel):
    id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    registration_status: str | None = None
    picture: dict | None = None
    custom_picture: bool | None = None
    balance: list[Balance] | None = None


class Group(BaseModel):
    id: int | None = None
    name: str | None = None
    group_type: str | None = None
    updated_at: str | None = None
    simplify_by_default: bool | None = None
    members: list[GroupMember] | None = None
    original_debts: list[Debt] | None = None
    simplified_debts: list[Debt] | None = None
    avatar: dict | None = None
    custom_avatar: bool | None = None
    cover_photo: dict | None = None
    invite_link: str | None = None
