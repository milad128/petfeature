"""Application configuration from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "petfeature"
    debug: bool = False
    secret_key: str = "change-me"

    port: int = 8000

    database_url: str = "postgresql+asyncpg://petfeature:petfeature@localhost:5432/petfeature"

    admin_username: str = "admin"
    admin_password: str = "change-me"

    @property
    def database_url_sync(self) -> str:
        """Sync URL for Alembic migrations (strips async driver prefixes)."""
        return self.database_url.replace("+asyncpg", "").replace("+aiosqlite", "")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
