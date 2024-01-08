import datetime

from pydantic.fields import (
    Field,
)
from pydantic.main import (
    BaseModel,
)

from src.common import (
    schemas,
)


class _Author(schemas.UUIDSchemaMixin):
    name: str = Field(..., description="Name of the author")
    last_name: str | None = Field(None, description="Last Name of the author")


class _Category(schemas.UUIDSchemaMixin):
    name: str = Field(..., description="Category")


class BaseBook(BaseModel):
    title: str = Field(..., description="The title of the book")
    description: str | None = Field(None, description="The description of the book")
    language: str | None = Field(
        None, pattern=r"^[a-z]{2}$", description="The language of the book (ISO 639-1 code)"
    )
    publication_date: datetime.date | None = Field(
        None, description="Publication date of the book (YYYY-MM-DD)"
    )
    isbn: str | None = Field(
        None, pattern=r"^\d{10}|\d{13}$", description="The ISBN of the book (10 or 13 digits)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Example Book Title",
                "description": "A brief description of the book",
                "language": "en",
                "publication_date": "2021-01-01",
                "isbn": "1234567890123",
            }
        }


class CreateBook(BaseBook):
    pass


class UpdateBook(BaseBook):
    title: str | None = Field(None, description="The title of the book")


class Book(BaseBook, schemas.UUIDSchemaMixin, schemas.TimestampSchemaMixin):
    class Config:
        from_attributes = True


class BookDetails(BaseBook, schemas.UUIDSchemaMixin, schemas.TimestampSchemaMixin):
    authors: list[_Author] = Field([], description="Book authors")
    categories: list[_Category] = Field([], description="Book categories")
