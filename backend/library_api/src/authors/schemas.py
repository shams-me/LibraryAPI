from pydantic.fields import Field
from pydantic.main import BaseModel

from src.common import schemas


class BaseAuthor(BaseModel):
    name: str = Field(..., description="Name of the author")
    last_name: str | None = Field(None, description="Last Name of the author")
    biography: str | None = Field(None, description="biography of the author")


class UpdateAuthor(BaseAuthor):
    name: str | None = Field(None, description="Name of the author")


class Author(BaseAuthor, schemas.UUIDSchemaMixin, schemas.TimestampSchemaMixin):
    class Config:
        from_attributes = True


class AuthorDetails(BaseAuthor, schemas.UUIDSchemaMixin, schemas.TimestampSchemaMixin):
    class Config:
        from_attributes = True
