"""Team Copilot - Core - Configuration."""

from functools import lru_cache
from pydantic_settings import BaseSettings

from team_copilot import __version__ as version


class Settings(BaseSettings):
    """Team Copilot settings."""

    debug: bool = False
    app_name: str = "Team Copilot"
    app_version: str = version
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_secret_key: str
    app_hash_algorithm: str = "HS256"
    app_acc_token_exp_min: int = 60
    app_docs_max_size_bytes: int = 1024 * 1024 * 10  # 10 MB
    app_docs_dir: str
    app_admin_user: str | None = None
    app_admin_password: str | None = None
    db_url: str
    llm_api_key: str
    llm_model: str
    llm_max_retries: int = 2
    llm_timeout_sec: int = 60
    emb_api_key: str
    emb_model: str
    emb_dim: int
    emb_max_retries: int = 2
    emb_timeout_sec: int = 60

    class Config:
        env_file = ".env"
        env_prefix = "TEAM_COPILOT_"


@lru_cache()
def get_settings() -> Settings:
    """Get settings.

    Returns:
        Settings: Settings object.
    """
    return Settings()


settings = get_settings()
