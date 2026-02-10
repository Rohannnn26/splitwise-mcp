# Splitwise MCP Server

A **Model Context Protocol (MCP)** server that exposes the full [Splitwise API](https://dev.splitwise.com/) as LLM-callable tools. Works with Claude Desktop, VS Code Copilot, and any MCP-compatible client.

## Features

- **27 tools** covering all Splitwise domains: Users, Groups, Friends, Expenses, Comments, Notifications, Currencies, Categories
- **Async HTTP client** powered by `httpx` for fast, non-blocking API calls
- **LLM-friendly output** — responses are formatted as concise, readable text
- **API key auth** now, with OAuth 2.0 architecture ready for future SaaS deployment

## Quick Start

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure your API key

Copy `.env.example` to `.env` and add your Splitwise API key:

```bash
cp .env.example .env
# Edit .env and set SPLITWISE_API_KEY=your-key-here
```

Get an API key at [https://secure.splitwise.com/apps](https://secure.splitwise.com/apps).

### 3. Test with MCP Inspector (local)

```bash
# Test in SSE mode (default)
npx @modelcontextprotocol/inspector uv run splitwise-mcp

# Or test in stdio mode for Claude Desktop
$env:MCP_TRANSPORT="stdio"  # On Windows
# export MCP_TRANSPORT=stdio  # On macOS/Linux
npx @modelcontextprotocol/inspector uv run splitwise-mcp
```

### 4. Add to Claude Desktop (local)

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "splitwise": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\Rohan Gupta\\Documents\\coding\\splitwise_mcp_server",
        "run",
        "splitwise-mcp"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

On macOS/Linux, adjust the path accordingly.

## Deploy to Render

This server can be deployed to [Render](https://render.com) as a web service accessible via SSE transport.

### 1. Push to GitHub

Ensure your code is in a GitHub repository (`.env` is already gitignored).

### 2. Create a Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Render will auto-detect the `render.yaml` configuration

### 3. Set Environment Variables

In Render Dashboard > Environment, add:
- `SPLITWISE_API_KEY` - Your Splitwise API key (keep as secret)

The server will automatically run in SSE mode when deployed.

### 4. Connect from Claude Desktop

After deployment, update your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "splitwise": {
      "url": "https://your-app-name.onrender.com/sse"
    }
  }
}
```

### Local Development

For local testing with stdio transport (default for Claude Desktop):

```bash
# Set transport to stdio
export MCP_TRANSPORT=stdio  # On Windows: $env:MCP_TRANSPORT="stdio"
uv run splitwise-mcp
```

## Available Tools

| Domain         | Tools                                                                                  |
| -------------- | -------------------------------------------------------------------------------------- |
| **Users**      | `get_current_user`, `get_user`, `update_user`                                          |
| **Groups**     | `list_groups`, `get_group`, `create_group`, `delete_group`, `restore_group`, `add_user_to_group`, `remove_user_from_group` |
| **Friends**    | `list_friends`, `get_friend`, `add_friend`, `add_friends`, `delete_friend`             |
| **Expenses**   | `list_expenses`, `get_expense`, `create_expense`, `update_expense`, `delete_expense`, `restore_expense` |
| **Comments**   | `get_comments`, `create_comment`, `delete_comment`                                     |
| **Notifications** | `get_notifications`                                                                 |
| **Other**      | `list_currencies`, `list_categories`                                                   |

## Project Structure

```
splitwise_mcp/
├── server.py          # MCP server entry point (FastMCP + lifespan)
├── app.py             # FastMCP instance + lifespan management
├── config.py          # Settings loaded from .env
├── client.py          # Async Splitwise API client (httpx)
├── models/            # Pydantic models for API responses
├── tools/             # MCP tool definitions (one file per domain)
│   ├── users.py
│   ├── groups.py
│   ├── friends.py
│   ├── expenses.py
│   ├── comments.py
│   ├── notifications.py
│   └── other.py
└── utils/
    └── formatters.py  # LLM-friendly text formatters
```

## Development

```bash
# Install dev dependencies
uv sync --dev

# Lint
uv run ruff check src/

# Format
uv run ruff format src/
```

## License

MIT
