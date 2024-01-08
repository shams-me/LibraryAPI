import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import Field, BaseModel
from src.common import schemas as common_schemas
from src.users import schemas as users_schemas
from typing_extensions import Self


class Status(StrEnum):
    VALID: str = "valid"
    INVALID: str = "invalid"


class StatusDetail(StrEnum):
    VALID: str = "Provided access token is valid"
    INVALID: str = "Provided access token is invalid"


class AccessToken(BaseModel):
    access_token: str = Field(pattern=r"^(?:[\w-]*\.){2}[\w-]*$")


class AccessTokenInfo(BaseModel):
    status: Status
    detail: StatusDetail
    provided_access_token: str


class RefreshToken(BaseModel):
    refresh_token: str = Field(pattern=r"^(?:[\w-]*\.){2}[\w-]*$")


class JWTCredentials(
    RefreshToken,
    AccessToken,
):
    ...


class JWTUserIdentity(BaseModel):
    id: str
    permissions: dict[str, list[str]]
    role: str

    @classmethod
    def from_user(cls, user: users_schemas.User) -> Self:
        return cls(id=str(user.id), permissions=user.permissions, role=user.role)


class JWTIdentity(BaseModel):
    user: JWTUserIdentity
    access_jti: str
    refresh_jti: str

    @classmethod
    def from_user_identity(cls, user: JWTUserIdentity) -> Self:
        return cls(user=user, access_jti=str(uuid.uuid4()), refresh_jti=str(uuid.uuid4()))


class JWTDecoded(BaseModel):
    user: JWTUserIdentity
    access_jti: str
    refresh_jti: str
    type: str
    exp: datetime
    iat: datetime
