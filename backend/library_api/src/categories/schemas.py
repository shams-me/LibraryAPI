from pydantic.fields import Field
from pydantic.main import BaseModel

from src.common import schemas


class BaseCategory(BaseModel):
    name: str = Field(..., description="Name of the category")
    description: str | None = Field(None, description="Description of the category")


class UpdateCategory(BaseCategory):
    name: str | None = Field(None, description="Name of the category")


class Category(BaseCategory, schemas.UUIDSchemaMixin, schemas.TimestampSchemaMixin):
    pass


class CategoryDetails(BaseCategory, schemas.UUIDSchemaMixin, schemas.TimestampSchemaMixin):
    pass
