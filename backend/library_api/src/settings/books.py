from pydantic import Field
from pydantic_settings import BaseSettings


class BooksSettings(BaseSettings):
    elastic_index: str = Field(alias="elastic_index")
    cache_expire_in_seconds: int = Field(alias="cache_expire_in_seconds", default=300)
