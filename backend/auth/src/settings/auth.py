from pydantic import BaseModel, Field


class AuthSettings(BaseModel):
    secret_key: str = Field(alias="secret_key")
    jwt_encoding_algorithm: str = Field(alias="auth_jwt_encoding_algorithm", default="HS256")
    jwt_secret_key: str = Field(alias="auth_jwt_secret_key")

    access_token_expires_secs: int = Field(alias="auth_access_token_expires_secs")
    refresh_token_expires_secs: int = Field(alias="auth_refresh_token_expires_secs")
