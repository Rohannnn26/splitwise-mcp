"""Comment models."""

from __future__ import annotations

from pydantic import BaseModel

from splitwise_mcp.models.common import CommentUser


class Comment(BaseModel):
    id: int | None = None
    content: str | None = None
    comment_type: str | None = None
    relation_type: str | None = None
    relation_id: int | None = None
    created_at: str | None = None
    deleted_at: str | None = None
    user: CommentUser | None = None
