"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the Splitwise MCP server.

    Reads from environment variables or a `.env` file in the project root.
    """

    # Required — Splitwise Bearer API key
    splitwise_api_key: str

    # Splitwise API base URL (v3.0)
    splitwise_base_url: str = "https://secure.splitwise.com/api/v3.0"

    # Future OAuth fields (optional, for SaaS upgrade)
    oauth_client_id: str | None = None
    oauth_client_secret: str | None = None
    oauth_redirect_uri: str | None = None

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        # The .env file uses API_KEY but we map it here
        "extra": "ignore",
    }
