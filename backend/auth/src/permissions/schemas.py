import enum

from pydantic import BaseModel, Field

from src.common import schemas as common_schemas


class PermissionType(enum.StrEnum):
    READ = "READ"
    CREATE = "CREATE"
    DELETE = "DELETE"
    UPDATE = "UPDATE"
    BLOCKED = "BLOCKED"


class PermissionCreate(BaseModel):
    src: str = Field(min_length=3)
    type: PermissionType = Field(PermissionType.READ)


class PermissionUpdate(BaseModel):
    src: str | None = Field(None, min_length=3)
    type: PermissionType | None = Field(None)


class Permission(
    common_schemas.UUIDSchemaMixin,
    common_schemas.TimestampSchemaMixin,
):
    src: str
    type: str = PermissionType.READ

    class Config:
        from_attributes = True
