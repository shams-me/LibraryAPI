from datetime import (
    datetime,
)
from typing import (
    Generic,
    TypeVar,
    cast,
)
from uuid import (
    UUID,
)

from pydantic import (
    BaseModel,
    Field,
)

ESDocType = TypeVar(
    "ESDocType",
    bound=BaseModel,
)
SQLRowType = TypeVar(
    "SQLRowType",
    bound="BasicSQLRowDataInt",
)


class BasicSQLRowDataInt(BaseModel):
    def transform_to_es_doc(
        self,
    ) -> BaseModel:
        raise NotImplementedError


class ContainerMixin(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class ESAuthorDoc(BaseModel):
    id: UUID
    name: str
    last_name: str


class ESBookDoc(BaseModel):
    id: UUID
    title: str
    description: str
    language: str
    isbn: str
    publication_date: datetime
    authors: list[ESAuthorDoc]
    categories: list[str]
    created_at: datetime
    modified_at: datetime


class ESCategoryDoc(BaseModel):
    id: UUID
    name: str


class Author(BaseModel):
    author_id: UUID = Field(alias="id")
    name: str


class Category(BaseModel):
    category_id: UUID = Field(alias="id")
    name: str


class BookRow(BasicSQLRowDataInt):
    book_id: UUID = Field(alias="id")
    title: str
    description: str
    language: str
    isbn: str
    publication_date: datetime
    created_at: datetime
    modified_at: datetime
    authors: list[Author | None]
    categories: list[Category | None]

    def transform_to_es_doc(
        self,
    ) -> ESBookDoc:
        return ESBookDoc(
            id=self.book_id,
            title=self.title,
            description=self.description,
            language=self.language,
            isbn=self.isbn,
            publication_date=self.publication_date,
            authors=self.authors,
            categories=self.categories,
        )


class AuthorRow(BasicSQLRowDataInt):
    author_id: UUID = Field(alias="id")
    name: str

    def transform_to_es_doc(
        self,
    ) -> ESAuthorDoc:
        return ESAuthorDoc(
            id=self.author_id,
            name=self.name,
        )


class CategoryRow(BasicSQLRowDataInt):
    category_id: UUID = Field(alias="id")
    name: str

    def transform_to_es_doc(
        self,
    ) -> ESCategoryDoc:
        return ESCategoryDoc(
            id=self.category_id,
            name=self.name,
        )


class ESContainer(
    ContainerMixin,
    Generic[ESDocType],
):
    bulk: list[ESDocType]

    def to_actions(
        self,
        index: str,
    ) -> list[dict]:
        actions = []
        for doc in self.bulk:
            doc_data = doc.model_dump(mode="json")
            actions.append(
                {
                    "_id": doc_data["id"],
                    "_index": index,
                    "_source": doc_data,
                }
            )
        return actions


class SQLContainer(
    ContainerMixin,
    Generic[
        SQLRowType,
        ESDocType,
    ],
):
    batch: list[SQLRowType]

    def transform(
        self,
    ) -> ESContainer[ESDocType]:
        es_docs = [item.transform_to_es_doc() for item in self.batch]
        return ESContainer[ESDocType](
            bulk=cast(
                list[ESDocType],
                es_docs,
            )
        )
