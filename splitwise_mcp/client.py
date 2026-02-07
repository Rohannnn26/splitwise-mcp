"""Async HTTP client wrapping the Splitwise REST API."""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://secure.splitwise.com/api/v3.0"


class SplitwiseAPIError(Exception):
    """Raised when the Splitwise API returns an error."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Splitwise API error {status_code}: {detail}")


class SplitwiseClient:
    """Thin async wrapper around the Splitwise v3.0 REST API.

    All methods return raw dicts parsed from JSON responses.
    """

    def __init__(self, api_key: str, base_url: str = BASE_URL) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        resp = await self._client.get(path, params=params)
        return self._handle(resp)

    async def _post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        resp = await self._client.post(path, json=json)
        return self._handle(resp)

    @staticmethod
    def _handle(resp: httpx.Response) -> Any:
        if resp.status_code == 401:
            raise SplitwiseAPIError(401, "Invalid API key or OAuth access token")
        if resp.status_code == 403:
            raise SplitwiseAPIError(403, "Forbidden — you don't have access to this resource")
        if resp.status_code == 404:
            raise SplitwiseAPIError(404, "Resource not found")
        if resp.status_code >= 400:
            raise SplitwiseAPIError(resp.status_code, resp.text)
        return resp.json()

    @staticmethod
    def _check_success(data: dict) -> dict:
        """Some Splitwise endpoints return 200 even on failure. Check the body."""
        if "errors" in data and data["errors"]:
            raise SplitwiseAPIError(200, str(data["errors"]))
        if "success" in data and data["success"] is False:
            errors = data.get("errors", "Unknown error")
            raise SplitwiseAPIError(200, str(errors))
        return data

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    async def get_current_user(self) -> dict:
        data = await self._get("/get_current_user")
        return data.get("user", data)

    async def get_user(self, user_id: int) -> dict:
        data = await self._get(f"/get_user/{user_id}")
        return data.get("user", data)

    async def update_user(
        self,
        user_id: int,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        default_currency: str | None = None,
        locale: str | None = None,
    ) -> dict:
        body: dict[str, Any] = {}
        if first_name is not None:
            body["first_name"] = first_name
        if last_name is not None:
            body["last_name"] = last_name
        if email is not None:
            body["email"] = email
        if default_currency is not None:
            body["default_currency"] = default_currency
        if locale is not None:
            body["locale"] = locale
        data = await self._post(f"/update_user/{user_id}", json=body)
        return data.get("user", data)

    # ------------------------------------------------------------------
    # Groups
    # ------------------------------------------------------------------

    async def get_groups(self) -> list[dict]:
        data = await self._get("/get_groups")
        return data.get("groups", data)

    async def get_group(self, group_id: int) -> dict:
        data = await self._get(f"/get_group/{group_id}")
        return data.get("group", data)

    async def create_group(
        self,
        name: str,
        group_type: str = "other",
        simplify_by_default: bool = False,
        users: list[dict[str, Any]] | None = None,
    ) -> dict:
        body: dict[str, Any] = {
            "name": name,
            "group_type": group_type,
            "simplify_by_default": simplify_by_default,
        }
        # Flatten users into users__{i}__{prop} format
        if users:
            for i, user in enumerate(users):
                for key, val in user.items():
                    body[f"users__{i}__{key}"] = val
        data = await self._post("/create_group", json=body)
        return data.get("group", data)

    async def delete_group(self, group_id: int) -> dict:
        data = await self._post(f"/delete_group/{group_id}")
        return self._check_success(data)

    async def undelete_group(self, group_id: int) -> dict:
        data = await self._post(f"/undelete_group/{group_id}")
        return self._check_success(data)

    async def add_user_to_group(
        self,
        group_id: int,
        *,
        user_id: int | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ) -> dict:
        body: dict[str, Any] = {"group_id": group_id}
        if user_id is not None:
            body["user_id"] = user_id
        if first_name is not None:
            body["first_name"] = first_name
        if last_name is not None:
            body["last_name"] = last_name
        if email is not None:
            body["email"] = email
        data = await self._post("/add_user_to_group", json=body)
        return self._check_success(data)

    async def remove_user_from_group(self, group_id: int, user_id: int) -> dict:
        body = {"group_id": group_id, "user_id": user_id}
        data = await self._post("/remove_user_from_group", json=body)
        return self._check_success(data)

    # ------------------------------------------------------------------
    # Friends
    # ------------------------------------------------------------------

    async def get_friends(self) -> list[dict]:
        data = await self._get("/get_friends")
        return data.get("friends", data)

    async def get_friend(self, friend_id: int) -> dict:
        data = await self._get(f"/get_friend/{friend_id}")
        return data.get("friend", data)

    async def create_friend(
        self,
        user_email: str,
        user_first_name: str | None = None,
        user_last_name: str | None = None,
    ) -> dict:
        body: dict[str, Any] = {"user_email": user_email}
        if user_first_name is not None:
            body["user_first_name"] = user_first_name
        if user_last_name is not None:
            body["user_last_name"] = user_last_name
        data = await self._post("/create_friend", json=body)
        return data.get("friend", data)

    async def create_friends(self, users: list[dict[str, str]]) -> dict:
        body: dict[str, Any] = {}
        for i, user in enumerate(users):
            for key, val in user.items():
                body[f"friends__{i}__{key}"] = val
        data = await self._post("/create_friends", json=body)
        return data

    async def delete_friend(self, friend_id: int) -> dict:
        data = await self._post(f"/delete_friend/{friend_id}")
        return self._check_success(data)

    # ------------------------------------------------------------------
    # Expenses
    # ------------------------------------------------------------------

    async def get_expense(self, expense_id: int) -> dict:
        data = await self._get(f"/get_expense/{expense_id}")
        return data.get("expense", data)

    async def get_expenses(
        self,
        *,
        group_id: int | None = None,
        friend_id: int | None = None,
        dated_after: str | None = None,
        dated_before: str | None = None,
        updated_after: str | None = None,
        updated_before: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict]:
        params: dict[str, Any] = {}
        if group_id is not None:
            params["group_id"] = group_id
        if friend_id is not None:
            params["friend_id"] = friend_id
        if dated_after is not None:
            params["dated_after"] = dated_after
        if dated_before is not None:
            params["dated_before"] = dated_before
        if updated_after is not None:
            params["updated_after"] = updated_after
        if updated_before is not None:
            params["updated_before"] = updated_before
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        data = await self._get("/get_expenses", params=params)
        return data.get("expenses", data)

    async def create_expense(
        self,
        cost: str,
        description: str,
        *,
        group_id: int | None = None,
        split_equally: bool = False,
        currency_code: str = "USD",
        category_id: int | None = None,
        date: str | None = None,
        repeat_interval: str = "never",
        details: str | None = None,
        users: list[dict[str, Any]] | None = None,
    ) -> dict:
        body: dict[str, Any] = {
            "cost": cost,
            "description": description,
            "currency_code": currency_code,
            "repeat_interval": repeat_interval,
        }
        if group_id is not None:
            body["group_id"] = group_id
        if split_equally:
            body["split_equally"] = True
        if category_id is not None:
            body["category_id"] = category_id
        if date is not None:
            body["date"] = date
        if details is not None:
            body["details"] = details
        # Flatten user shares into users__{i}__{prop}
        if users:
            for i, user in enumerate(users):
                for key, val in user.items():
                    body[f"users__{i}__{key}"] = val
        data = await self._post("/create_expense", json=body)
        # 200 OK doesn't mean success — check errors
        if "errors" in data and data["errors"]:
            raise SplitwiseAPIError(200, str(data["errors"]))
        return data

    async def update_expense(
        self,
        expense_id: int,
        *,
        cost: str | None = None,
        description: str | None = None,
        group_id: int | None = None,
        currency_code: str | None = None,
        category_id: int | None = None,
        date: str | None = None,
        repeat_interval: str | None = None,
        details: str | None = None,
        users: list[dict[str, Any]] | None = None,
    ) -> dict:
        body: dict[str, Any] = {}
        if cost is not None:
            body["cost"] = cost
        if description is not None:
            body["description"] = description
        if group_id is not None:
            body["group_id"] = group_id
        if currency_code is not None:
            body["currency_code"] = currency_code
        if category_id is not None:
            body["category_id"] = category_id
        if date is not None:
            body["date"] = date
        if repeat_interval is not None:
            body["repeat_interval"] = repeat_interval
        if details is not None:
            body["details"] = details
        if users:
            for i, user in enumerate(users):
                for key, val in user.items():
                    body[f"users__{i}__{key}"] = val
        data = await self._post(f"/update_expense/{expense_id}", json=body)
        if "errors" in data and data["errors"]:
            raise SplitwiseAPIError(200, str(data["errors"]))
        return data

    async def delete_expense(self, expense_id: int) -> dict:
        data = await self._post(f"/delete_expense/{expense_id}")
        return self._check_success(data)

    async def undelete_expense(self, expense_id: int) -> dict:
        data = await self._post(f"/undelete_expense/{expense_id}")
        return self._check_success(data)

    # ------------------------------------------------------------------
    # Comments
    # ------------------------------------------------------------------

    async def get_comments(self, expense_id: int) -> list[dict]:
        data = await self._get("/get_comments", params={"expense_id": expense_id})
        return data.get("comments", data)

    async def create_comment(self, expense_id: int, content: str) -> dict:
        body = {"expense_id": expense_id, "content": content}
        data = await self._post("/create_comment", json=body)
        return data.get("comment", data)

    async def delete_comment(self, comment_id: int) -> dict:
        data = await self._post(f"/delete_comment/{comment_id}")
        return data.get("comment", data)

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    async def get_notifications(
        self,
        *,
        updated_after: str | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        params: dict[str, Any] = {}
        if updated_after is not None:
            params["updated_after"] = updated_after
        if limit is not None:
            params["limit"] = limit
        data = await self._get("/get_notifications", params=params)
        return data.get("notifications", data)

    # ------------------------------------------------------------------
    # Other (currencies, categories)
    # ------------------------------------------------------------------

    async def get_currencies(self) -> list[dict]:
        data = await self._get("/get_currencies")
        return data.get("currencies", data)

    async def get_categories(self) -> list[dict]:
        data = await self._get("/get_categories")
        return data.get("categories", data)
