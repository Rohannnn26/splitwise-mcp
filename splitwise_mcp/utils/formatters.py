"""Format Splitwise API responses into concise, LLM-friendly text."""

from __future__ import annotations

from typing import Any


def _name(user: dict) -> str:
    first = user.get("first_name") or ""
    last = user.get("last_name") or ""
    return f"{first} {last}".strip() or "Unknown"


def format_user(user: dict) -> str:
    lines = [
        f"User: {_name(user)} (ID: {user.get('id')})",
        f"  Email: {user.get('email', 'N/A')}",
        f"  Status: {user.get('registration_status', 'N/A')}",
    ]
    if user.get("default_currency"):
        lines.append(f"  Default currency: {user['default_currency']}")
    if user.get("locale"):
        lines.append(f"  Locale: {user['locale']}")
    return "\n".join(lines)


def format_group(group: dict) -> str:
    lines = [
        f"Group: {group.get('name', 'N/A')} (ID: {group.get('id')})",
        f"  Type: {group.get('group_type', 'N/A')}",
        f"  Simplify debts: {group.get('simplify_by_default', False)}",
    ]
    members = group.get("members") or []
    if members:
        member_names = [_name(m) for m in members]
        lines.append(f"  Members ({len(members)}): {', '.join(member_names)}")
    debts = group.get("simplified_debts") or group.get("original_debts") or []
    if debts:
        lines.append("  Debts:")
        for d in debts:
            lines.append(
                f"    User {d.get('from')} owes User {d.get('to')}: "
                f"{d.get('amount')} {d.get('currency_code', '')}"
            )
    if group.get("invite_link"):
        lines.append(f"  Invite link: {group['invite_link']}")
    return "\n".join(lines)


def format_group_list(groups: list[dict]) -> str:
    if not groups:
        return "No groups found."
    parts = []
    for g in groups:
        members = g.get("members") or []
        parts.append(
            f"- {g.get('name', 'N/A')} (ID: {g.get('id')}, "
            f"type: {g.get('group_type', 'N/A')}, "
            f"{len(members)} members)"
        )
    return f"Groups ({len(groups)}):\n" + "\n".join(parts)


def format_friend(friend: dict) -> str:
    lines = [
        f"Friend: {_name(friend)} (ID: {friend.get('id')})",
        f"  Email: {friend.get('email', 'N/A')}",
    ]
    balances = friend.get("balance") or []
    if balances:
        for b in balances:
            amt = b.get("amount", "0")
            cur = b.get("currency_code", "")
            sign = "owed to you" if float(amt) > 0 else "you owe"
            lines.append(f"  Balance: {abs(float(amt))} {cur} ({sign})")
    else:
        lines.append("  Balance: settled up")
    return "\n".join(lines)


def format_friend_list(friends: list[dict]) -> str:
    if not friends:
        return "No friends found."
    parts = []
    for f in friends:
        bal_str = "settled"
        balances = f.get("balance") or []
        if balances:
            bal_parts = []
            for b in balances:
                amt = float(b.get("amount", "0"))
                cur = b.get("currency_code", "")
                if amt > 0:
                    bal_parts.append(f"+{amt} {cur}")
                elif amt < 0:
                    bal_parts.append(f"{amt} {cur}")
            if bal_parts:
                bal_str = ", ".join(bal_parts)
        parts.append(f"- {_name(f)} (ID: {f.get('id')}) [{bal_str}]")
    return f"Friends ({len(friends)}):\n" + "\n".join(parts)


def format_expense(expense: dict) -> str:
    lines = [
        f"Expense #{expense.get('id')}: {expense.get('description', 'N/A')}",
        f"  Cost: {expense.get('cost')} {expense.get('currency_code', '')}",
        f"  Date: {expense.get('date', 'N/A')}",
    ]
    if expense.get("group_id"):
        lines.append(f"  Group ID: {expense['group_id']}")
    if expense.get("category") and expense["category"].get("name"):
        lines.append(f"  Category: {expense['category']['name']}")
    if expense.get("details"):
        lines.append(f"  Notes: {expense['details']}")
    if expense.get("payment"):
        lines.append("  Type: Payment")

    users = expense.get("users") or []
    if users:
        payers = [
            f"{_name(u.get('user', u))} paid {u.get('paid_share', '0')}"
            for u in users
            if float(u.get("paid_share", "0")) > 0
        ]
        debtors = [
            f"{_name(u.get('user', u))} owes {u.get('owed_share', '0')}"
            for u in users
            if float(u.get("owed_share", "0")) > 0
        ]
        if payers:
            lines.append(f"  Paid by: {'; '.join(payers)}")
        if debtors:
            lines.append(f"  Split: {'; '.join(debtors)}")

    if expense.get("repeat_interval") and expense["repeat_interval"] != "never":
        lines.append(f"  Repeats: {expense['repeat_interval']}")
    if expense.get("deleted_at"):
        lines.append(f"  DELETED at {expense['deleted_at']}")
    return "\n".join(lines)


def format_expense_list(expenses: list[dict]) -> str:
    if not expenses:
        return "No expenses found."
    parts = []
    for e in expenses:
        desc = e.get("description", "N/A")
        cost = e.get("cost", "?")
        cur = e.get("currency_code", "")
        date = (e.get("date") or "")[:10]
        deleted = " [DELETED]" if e.get("deleted_at") else ""
        parts.append(f"- #{e.get('id')} {desc} — {cost} {cur} ({date}){deleted}")
    return f"Expenses ({len(expenses)}):\n" + "\n".join(parts)


def format_comment(comment: dict) -> str:
    user = comment.get("user") or {}
    return (
        f"[{comment.get('comment_type', 'User')}] "
        f"{_name(user)} ({comment.get('created_at', '')}): "
        f"{comment.get('content', '')}"
    )


def format_comment_list(comments: list[dict]) -> str:
    if not comments:
        return "No comments."
    parts = [format_comment(c) for c in comments]
    return f"Comments ({len(comments)}):\n" + "\n".join(parts)


def format_notification(n: dict) -> str:
    # Strip HTML tags for cleaner LLM reading
    import re
    content = re.sub(r"<[^>]+>", "", n.get("content", ""))
    return f"[{n.get('created_at', '')}] {content}"


def format_notification_list(notifications: list[dict]) -> str:
    if not notifications:
        return "No notifications."
    parts = [format_notification(n) for n in notifications]
    return f"Notifications ({len(notifications)}):\n" + "\n".join(parts)


def format_currency_list(currencies: list[dict]) -> str:
    if not currencies:
        return "No currencies found."
    parts = [
        f"- {c.get('currency_code')}: {c.get('unit', '')}"
        for c in currencies
    ]
    return f"Currencies ({len(currencies)}):\n" + "\n".join(parts)


def format_category_list(categories: list[dict]) -> str:
    if not categories:
        return "No categories found."
    parts = []
    for cat in categories:
        parts.append(f"- {cat.get('name', 'N/A')} (ID: {cat.get('id')})")
        for sub in cat.get("subcategories") or []:
            parts.append(f"    - {sub.get('name', 'N/A')} (ID: {sub.get('id')})")
    return f"Categories ({len(categories)}):\n" + "\n".join(parts)


def format_success(data: Any) -> str:
    if isinstance(data, dict):
        if data.get("success") is True:
            return "Success."
        if data.get("success") is False:
            return f"Failed: {data.get('errors', 'Unknown error')}"
    return str(data)
