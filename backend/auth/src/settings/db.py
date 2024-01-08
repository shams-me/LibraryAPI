from pydantic import BaseModel, Field, PostgresDsn, RedisDsn


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


class RedisSettings(BaseModel):
    host: str = Field(alias="redis_host")
    port: int = Field(alias="redis_port")

    @property
    def dsn(self) -> str:
        return str(
            RedisDsn.build(
                scheme="redis",
                host=self.host,
                port=self.port,
            )
        )
