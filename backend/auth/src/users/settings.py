from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from settings.app import ENV_DIR


class UserSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_DIR), env_file_encoding="utf-8", env_nested_delimiter="__", extra="ignore"
    )
    username_min_length: int = Field(env="USER_USERNAME_MIN_LENGTH", default=3)
    username_max_length: int = Field(env="USER_USERNAME_MAX_LENGTH", default=50)
    # Latin letters or numbers separated by standard delimiters
    username_pattern: str = r"^[a-zA-Z0-9]+(?:[ _.-][a-z0-9]+)*$"

    name_min_length: int = Field(env="NAME_MIN_LENGTH", default=1)
    name_max_length: int = Field(env="NAME_MIN_LENGTH", default=255)
    name_pattern: str = r"^[a-zA-Z ,.'-]+$"

    password_min_length: int = Field(env="USER_PASSWORD_MIN_LENGTH", default=8)
    password_max_length: int = Field(env="USER_PASSWORD_MAX_LENGTH", default=64)


@lru_cache(maxsize=1)
def get_users_settings() -> UserSettings:
    return UserSettings()
