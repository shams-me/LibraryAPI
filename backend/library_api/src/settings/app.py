from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings

from src.settings.auth import AuthSettings
from src.settings.author import AuthorSettings
from src.settings.books import BooksSettings
from src.settings.category import CategorySettings
from src.settings.db import ElasticSettings, RedisSettings, PostgresSettings
from src.settings.jaeger import JaegerSettings
from src.settings.logging import LoggingSettings
from src.settings.service import ServiceSettings

ENV_DIR = Path(__file__).resolve().parent.parent.parent.joinpath(".env")


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_DIR), env_file_encoding="utf-8", env_nested_delimiter="__", extra="ignore"
    )

    is_development: bool = Field(alias="IS_DEVELOPMENT", default=False)
    rate_limiter_times: int = Field(10, alias="rate_limiter_times")
    rate_limiter_seconds: int = Field(10, alias="rate_limiter_seconds")

    postgres: PostgresSettings
    logging: LoggingSettings
    elastic: ElasticSettings
    redis: RedisSettings
    service: ServiceSettings
    auth: AuthSettings
    jaeger: JaegerSettings
    category: CategorySettings
    books: BooksSettings
    author: AuthorSettings


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()
