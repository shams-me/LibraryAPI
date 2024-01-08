from pydantic import Field, BaseModel


class AuthSettings(BaseModel):
    url: str = Field(alias="auth_url")
    jwt_encoding_algorithm: str = Field(alias="auth_jwt_encoding_algorithm", default="HS256")
    jwt_secret_key: str = Field(alias="auth_jwt_secret_key")
    request_timeout_sec: int = Field(alias="auth_request_timeout_sec", default=5)
