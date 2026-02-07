"""Notification models."""

from __future__ import annotations

from pydantic import BaseModel


class NotificationSource(BaseModel):
    type: str | None = None
    id: int | None = None
    url: str | None = None


class Notification(BaseModel):
    id: int | None = None
    type: int | None = None
    created_at: str | None = None
    created_by: int | None = None
    source: NotificationSource | None = None
    image_url: str | None = None
    image_shape: str | None = None
    content: str | None = None
