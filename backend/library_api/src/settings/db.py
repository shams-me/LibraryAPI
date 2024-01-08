from typing import Literal

from pydantic import BaseModel, Field, PostgresDsn, RedisDsn, AnyUrl


class PostgresSettings(BaseModel):
    dbname: str = Field(alias="postgres_db")
    user: str = Field(alias="postgres_user")
    password: str = Field(alias="postgres_password")
    host: str = Field(alias="postgres_host")
    port: int = Field(alias="postgres_port")
    scheme: str = "postgresql+asyncpg"

    @property
    def dsn(self) -> str:
        return str(
            PostgresDsn.build(
                scheme=self.scheme,
                username=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                path=self.dbname,
            )
        )


class ElasticSettings(BaseModel):
    host: str = Field("localhost", alias="elastic_host")
    port: int = Field(9200, alias="elastic_port")

    max_docs_to_fetch_at_one_time: Literal[10_000] = 10_000

    @property
    def dsn(self) -> str:
        return str(AnyUrl.build(scheme="http", host=self.host, port=self.port))


class RedisSettings(BaseModel):
    host: str = Field("localhost", alias="redis_host")
    port: int = Field(6379, alias="redis_port")

    @property
    def dsn(self) -> str:
        return str(RedisDsn.build(scheme="redis", host=self.host, port=self.port))
