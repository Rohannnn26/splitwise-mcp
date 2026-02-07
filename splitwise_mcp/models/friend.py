"""Friend models."""

from __future__ import annotations

from pydantic import BaseModel

from splitwise_mcp.models.common import Balance


class FriendGroup(BaseModel):
    group_id: int | None = None
    balance: list[Balance] | None = None


class Friend(BaseModel):
    id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    registration_status: str | None = None
    picture: dict | None = None
    custom_picture: bool | None = None
    groups: list[FriendGroup] | None = None
    balance: list[Balance] | None = None
    updated_at: str | None = None
