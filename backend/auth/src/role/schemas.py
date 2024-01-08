from pydantic.fields import Field
from pydantic.main import BaseModel

from src.common import schemas


class BaseRole(BaseModel):
    name: str = Field(..., description="Name of the role")


class UpdateRole(BaseRole):
    name: str | None = Field(None, description="Name of the role")


class Role(BaseRole, schemas.UUIDSchemaMixin, schemas.TimestampSchemaMixin):
    pass


class RoleDetails(BaseRole, schemas.UUIDSchemaMixin, schemas.TimestampSchemaMixin):
    pass
