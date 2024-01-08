from pydantic import Field
from pydantic_settings import BaseSettings


class CategorySettings(BaseSettings):
    cache_expire_in_seconds: int = Field(alias="cache_expire_in_seconds", default=300)
