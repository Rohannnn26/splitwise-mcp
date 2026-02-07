"""User models."""

from __future__ import annotations

from pydantic import BaseModel


class Picture(BaseModel):
    small: str | None = None
    medium: str | None = None
    large: str | None = None


class User(BaseModel):
    id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    registration_status: str | None = None
    picture: Picture | None = None
    custom_picture: bool | None = None


class CurrentUser(User):
    """Extends User with account-level fields."""
    notifications_read: str | None = None
    notifications_count: int | None = None
    notifications: dict | None = None
    default_currency: str | None = None
    locale: str | None = None
