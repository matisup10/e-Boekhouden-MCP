"""Configuration for the e-Boekhouden MCP server."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPConfig(BaseSettings):
    """Configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="EBOEKHOUDEN_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # e-Boekhouden API settings
    secret_token: str
    api_url: str = "https://api.e-boekhouden.nl/"
    source: str = "MCP-Server"

    # MCP server settings
    server_name: str = "eboekhouden"
    server_version: str = "0.1.0"
