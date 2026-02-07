## Plan: Splitwise MCP Server (Python)

**TL;DR**: Build a Python MCP server using the official `mcp` SDK (`MCPServer`) with `uv`, wrapping all 22 Splitwise API endpoints as MCP tools. Start with API key auth over stdio transport for local use. Architecture supports future OAuth + remote HTTP deployment for SaaS. The Splitwise HTTP client is isolated behind an async service layer so tools remain thin and testable.

**Steps**

### 1. Initialize the project with `uv`

Create the project scaffold:

```
splitwise_mcp/
├── pyproject.toml
├── .env                          # SPLITWISE_API_KEY (gitignored)
├── .env.example                  # Template for users
├── .gitignore
├── README.md
├── openapi.json                  # Existing — reference only
└── src/
    └── splitwise_mcp/
        ├── __init__.py
        ├── server.py             # MCPServer instance + lifespan + transport entry
        ├── config.py             # Pydantic Settings (API key, base URL, future OAuth creds)
        ├── client.py             # Async HTTP client (httpx) wrapping Splitwise REST API
        ├── models/               # Pydantic response/request models
        │   ├── __init__.py
        │   ├── user.py
        │   ├── group.py
        │   ├── friend.py
        │   ├── expense.py
        │   ├── comment.py
        │   ├── notification.py
        │   └── common.py         # Debt, Balance, Share, Category, Currency
        ├── tools/                # MCP tool definitions (one file per domain)
        │   ├── __init__.py       # Registers all tools on the MCPServer instance
        │   ├── users.py          # 3 tools
        │   ├── groups.py         # 7 tools
        │   ├── friends.py        # 5 tools
        │   ├── expenses.py       # 6 tools
        │   ├── comments.py       # 3 tools
        │   ├── notifications.py  # 1 tool
        │   └── other.py          # 2 tools (currencies, categories)
        └── utils/
            ├── __init__.py
            └── formatters.py     # Format API responses into LLM-friendly text
```

Dependencies in `pyproject.toml`:
- `mcp[cli]` — MCP SDK with CLI for dev/install
- `httpx` — async HTTP client for Splitwise API
- `pydantic` — models + settings
- `pydantic-settings` — env-based config
- `python-dotenv` — load `.env`

Dev dependencies: `pytest`, `pytest-asyncio`, `ruff`

### 2. Build the config layer — `config.py`

Create a `Settings` class using `pydantic-settings.BaseSettings` loading from `.env`:
- `splitwise_api_key: str` — Bearer token (required for now)
- `splitwise_base_url: str = "https://secure.splitwise.com/api/v3.0"` — base URL
- Future fields: `oauth_client_id`, `oauth_client_secret`, `oauth_redirect_uri` (optional, defaulting to `None`)

### 3. Build the async Splitwise HTTP client — `client.py`

Create a `SplitwiseClient` class wrapping `httpx.AsyncClient`:
- Constructor takes `api_key` and `base_url`
- Sets `Authorization: Bearer {api_key}` header on all requests
- One method per API endpoint (22 methods), returning parsed Pydantic models or raw dicts
- Methods map 1:1 to Splitwise REST endpoints:

| Method | HTTP | Splitwise Endpoint |
|--------|------|--------------------|
| `get_current_user()` | GET | `/get_current_user` |
| `get_user(id)` | GET | `/get_user/{id}` |
| `update_user(id, **fields)` | POST | `/update_user/{id}` |
| `get_groups()` | GET | `/get_groups` |
| `get_group(id)` | GET | `/get_group/{id}` |
| `create_group(name, group_type, users)` | POST | `/create_group` |
| `delete_group(id)` | POST | `/delete_group/{id}` |
| `undelete_group(id)` | POST | `/undelete_group/{id}` |
| `add_user_to_group(group_id, user_id/email)` | POST | `/add_user_to_group` |
| `remove_user_from_group(group_id, user_id)` | POST | `/remove_user_from_group` |
| `get_friends()` | GET | `/get_friends` |
| `get_friend(id)` | GET | `/get_friend/{id}` |
| `create_friend(email, first_name, last_name)` | POST | `/create_friend` |
| `create_friends(users)` | POST | `/create_friends` |
| `delete_friend(id)` | POST | `/delete_friend/{id}` |
| `get_expense(id)` | GET | `/get_expense/{id}` |
| `get_expenses(**filters)` | GET | `/get_expenses` |
| `create_expense(...)` | POST | `/create_expense` |
| `update_expense(id, ...)` | POST | `/update_expense/{id}` |
| `delete_expense(id)` | POST | `/delete_expense/{id}` |
| `undelete_expense(id)` | POST | `/undelete_expense/{id}` |
| `get_comments(expense_id)` | GET | `/get_comments` |
| `create_comment(expense_id, content)` | POST | `/create_comment` |
| `delete_comment(id)` | POST | `/delete_comment/{id}` |
| `get_notifications(**filters)` | GET | `/get_notifications` |
| `get_currencies()` | GET | `/get_currencies` |
| `get_categories()` | GET | `/get_categories` |

Error handling: raise a custom `SplitwiseAPIError` on non-2xx responses. For endpoints where "200 OK does not indicate success" (several Splitwise quirks), check `success` / `errors` fields in the response body.

### 4. Define Pydantic models — `models/`

Create models matching the OpenAPI schemas. Key models:

- **`user.py`**: `User`, `CurrentUser` (extends `User` with `notifications_read`, `default_currency`, `locale`)
- **`group.py`**: `Group` (with `members`, `original_debts`, `simplified_debts`, `avatar`, `invite_link`)
- **`friend.py`**: `Friend` (extends `User` with `balance`, `groups`, `updated_at`)
- **`expense.py`**: `Expense` (with `repayments`, `users`/shares, `comments`, `category`, `receipt`)
- **`comment.py`**: `Comment`, `CommentUser`
- **`notification.py`**: `Notification` (with `source`, `content`, `type`)
- **`common.py`**: `Debt`, `Balance`, `Share`, `Currency`, `Category`, `ParentCategory`

### 5. Build the MCP server — `server.py`

- Instantiate `MCPServer("splitwise-mcp")`
- Use `lifespan` context manager to create/destroy the `SplitwiseClient` (shared `httpx.AsyncClient`)
- The lifespan yields a context object containing the client instance
- Import and register all tools from `tools/` subpackage

```python
# Sketch of server.py structure
@asynccontextmanager
async def app_lifespan(server: MCPServer) -> AsyncIterator[AppContext]:
    settings = Settings()
    client = SplitwiseClient(api_key=settings.splitwise_api_key)
    try:
        yield AppContext(splitwise=client)
    finally:
        await client.close()

mcp = MCPServer("splitwise-mcp", lifespan=app_lifespan)
# tools registered via imports from tools/ package
```

Entry point: `mcp.run(transport="stdio")` for local, switchable to `transport="streamable-http"` for remote.

### 6. Implement MCP tools — `tools/`

Each file registers tools on the shared `mcp` instance using `@mcp.tool()` decorators. Tools are thin wrappers that:
1. Accept typed parameters from the LLM
2. Get the `SplitwiseClient` from `ctx.session` / lifespan context
3. Call the appropriate client method
4. Format the response into LLM-friendly text using `formatters.py`

**27 total tools across 7 files:**

**`tools/users.py`** (3 tools):
- `get_current_user` — Get the authenticated user's profile
- `get_user` — Get another user's info by ID
- `update_user` — Update user's name, email, default currency, locale

**`tools/groups.py`** (7 tools):
- `list_groups` — List all groups for current user
- `get_group` — Get group details by ID (members, balances, debts)
- `create_group` — Create a new group with optional initial members
- `delete_group` — Delete a group by ID
- `restore_group` — Undelete a previously deleted group
- `add_user_to_group` — Add user to group (by user_id or email)
- `remove_user_from_group` — Remove user from group

**`tools/friends.py`** (5 tools):
- `list_friends` — List current user's friends with balances
- `get_friend` — Get friend details by ID
- `add_friend` — Add a single friend by email
- `add_friends` — Add multiple friends at once
- `delete_friend` — Remove a friendship

**`tools/expenses.py`** (6 tools):
- `list_expenses` — List expenses with filters (group_id, friend_id, dated_after/before, limit, offset)
- `get_expense` — Get single expense details
- `create_expense` — Create expense (equal split or by shares)
- `update_expense` — Update an existing expense
- `delete_expense` — Delete an expense
- `restore_expense` — Undelete a deleted expense

**`tools/comments.py`** (3 tools):
- `get_comments` — Get comments for an expense
- `create_comment` — Add a comment to an expense
- `delete_comment` — Delete a comment

**`tools/notifications.py`** (1 tool):
- `get_notifications` — Get recent notifications with optional date filter

**`tools/other.py`** (2 tools):
- `list_currencies` — List all supported currencies
- `list_categories` — List all expense categories and subcategories

### 7. Build response formatters — `utils/formatters.py`

Create functions that convert raw API response dicts/models into concise, readable text for the LLM. Examples:
- Format expense as: `"Expense #51023: Brunch — $25.00 USD (Group: Housemates) — Paid by Ada, split between Ada ($12.50), Bob ($12.50)"`
- Format group balances as a table-like summary
- Format friend with outstanding balance

This keeps tool responses human-readable rather than dumping raw JSON.

### 8. Configure for Claude Desktop (local stdio)

Add a `claude_desktop_config.json` snippet in the README showing how to register the server:
```json
{
  "mcpServers": {
    "splitwise": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/splitwise_mcp", "src/splitwise_mcp/server.py"],
      "env": {
        "SPLITWISE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 9. Add tests

Create a `tests/` directory:
- `tests/test_client.py` — Unit tests for `SplitwiseClient` using `httpx` mock transport
- `tests/test_tools.py` — Test that tool functions produce correct output given mocked client responses
- `tests/conftest.py` — Shared fixtures (mock client, sample API responses)

### 10. Future SaaS preparation (architectural hooks)

These are **not implemented now** but the architecture supports them:
- `config.py` already has optional OAuth fields
- `server.py` transport is a single-line switch from `stdio` to `streamable-http`
- Add `auth/` module later with `TokenVerifier` and `AuthSettings` for MCP OAuth 2.1
- Add `Dockerfile` and `docker-compose.yml` when deploying remotely
- Add Starlette/ASGI mounting for production HTTP with CORS middleware

---

## Verification

1. **Unit tests**: `uv run pytest tests/` — validates client methods and tool output formatting
2. **Local smoke test**: `uv run mcp dev src/splitwise_mcp/server.py` — opens MCP Inspector in browser to interactively test each tool
3. **Claude Desktop integration test**: Register in `claude_desktop_config.json`, ask Claude "What are my Splitwise groups?" and verify it calls `list_groups` and returns real data
4. **Manual endpoint check**: For each of the 27 tools, invoke via MCP Inspector and compare response with direct Splitwise API call

---

## Decisions

- **Python over TypeScript**: Faster prototyping with decorators + type hints, auto schema generation
- **`httpx` over `requests`**: Async-native, required for MCP's async tool handlers
- **API key first, OAuth later**: Keeps initial scope manageable; `config.py` is pre-wired for OAuth fields
- **Thin tools, fat client**: Business logic lives in `SplitwiseClient`, tools are just parameter mapping + formatting — makes testing and future transport switching trivial
- **All 22 API endpoints covered**: Full Splitwise coverage from day one — no partial gaps
- **`uv` for packaging**: Recommended by MCP SDK docs, fastest Python dependency resolution
