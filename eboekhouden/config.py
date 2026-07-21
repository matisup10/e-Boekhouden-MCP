"""Configuration for the e-Boekhouden SDK."""

from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT_ENV = Path(__file__).resolve().parent.parent / ".env"


class EBoekhoudenConfig(BaseSettings):
    """Configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="EBOEKHOUDEN_",
        env_file=(".env", str(PROJECT_ROOT_ENV)),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_url: str = "https://api.e-boekhouden.nl/"
    secret_token: SecretStr
    source: str = "PythonSDK"
    session_refresh_buffer: int = 60  # seconds before expiry to refresh
