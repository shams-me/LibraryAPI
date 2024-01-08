from functools import lru_cache

from pathlib import Path
from pydantic import Field

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.settings.auth import AuthSettings

from src.settings.db import PostgresSettings, RedisSettings

from src.settings.jaeger import JaegerSettings

from src.settings.logging import LoggingSettings
from src.settings.service import ServiceSettings

ENV_DIR = Path(__file__).resolve().parent.parent.parent.joinpath(".env")


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_DIR), env_file_encoding="utf-8", env_nested_delimiter="__"
    )

    is_development: bool = Field(alias="is_development", default=False)
    rate_limiter_times: int = Field(100, alias="rate_limiter_times")
    rate_limiter_seconds: int = Field(1, alias="rate_limiter_seconds")
    logging: LoggingSettings
    postgres: PostgresSettings
    redis: RedisSettings
    service: ServiceSettings
    auth: AuthSettings
    jaeger: JaegerSettings


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()
