"""Team Copilot - Configuration."""

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
    db_url: str
    llm_api_key: str
    

    class Config:
        env_file = ".env"
        env_prefix = "TEAM_COPILOT_"


@lru_cache()
def get_settings() -> Settings:
    """Get settings.

    Returns:
        :return (Settings): Settings.
    """
    return Settings()


settings = get_settings()
