from functools import (
    lru_cache,
)
from pathlib import (
    Path,
)

from pydantic import (
    Field,
    BaseModel,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR.joinpath(".env")
ES_SCHEMAS_PATH = BASE_DIR.joinpath("configs/es_schemas")


class RedisSettings(BaseModel):
    host: str = Field(alias="redis_host")
    port: int = Field(alias="redis_port")

    prefix: str = Field(alias="redis_prefix")


class PGSettings(BaseModel):
    dbname: str = Field(alias="db_name")
    user: str = Field(alias="db_user")
    password: str = Field(alias="db_password")
    host: str = Field(alias="db_host")
    port: int = Field(alias="db_port")


class ESSettings(BaseModel):
    index: str = Field(alias="es_index")
    host: str = Field(alias="es_host")
    port: int = Field(alias="es_port")


class SystemSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )
    synhronization_time_sec: int = 10

    original_wait_for_sevice_time_sec: float = 0.1
    factor: int = 2
    max_value: float = 10

    db: PGSettings
    redis: RedisSettings
    es: ESSettings


@lru_cache(maxsize=1)
def get_app_settings() -> SystemSettings:
    return SystemSettings()
