import abc
from abc import ABC
from typing import TypeVar, Generic
from uuid import UUID

from fastapi_pagination import Page
from fastapi_pagination.ext.async_sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import Executable

from src.authors import schemas
from src.authors.exceptions import AuthorNotFound
from src.authors.models import Author
from src.books.models import Book  # noqa: F401
from src.common.database import Base

TModel = TypeVar("TModel", bound=Base)
TSchema = TypeVar("TSchema", bound=BaseModel)


class IAuthorRepository(abc.ABC, Generic[TModel]):
    @abc.abstractmethod
    async def insert(
        self, name: str, last_name: str | None = None, biography: str | None = None
    ) -> TModel | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, author_id: UUID) -> TModel | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def all(self) -> Page[TSchema]:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, author_id: UUID):
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, author_id: UUID, name: str, description: str) -> TModel:
        raise NotImplementedError


class PostgresAuthorRepository(
    IAuthorRepository[Author],
    ABC,
):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(
        self, name: str, last_name: str | None = None, biography: str | None = None
    ) -> TModel | None:
        author = Author(
            name=name,
            last_name=last_name,
            biography=biography,
        )
        self.session.add(author)
        await self.session.commit()
        return author

    async def get(self, author_id: UUID) -> Author | None:
        author = await self.session.get(
            Author,
            author_id,
        )

        if author:
            return author  # type: ignore

        raise AuthorNotFound(author_id)

    async def all(self) -> Page[schemas.Author]:
        stmt = select(Author)

        def transformer(
            items: list[schemas.Author],
        ) -> list[schemas.Author]:
            return [schemas.Author.model_validate(record) for record in items]

        return await paginate(self.session, stmt, transformer=transformer)  # type: ignore

    async def delete(self, author_id: UUID) -> None:
        stmt = delete(Author).where(Author.id == author_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update(
        self,
        author_id: UUID,
        name: str | None = None,
        last_name: str | None = None,
        biography: str | None = None,
    ) -> Author:
        mapping = zip(("name", "last_name", "biography"), (name, last_name, biography))
        values_to_update = {k: v for k, v in mapping if v is not None}

        stmt = update(Author).where(Author.id == author_id).values(**values_to_update)
        await self.session.execute(stmt)
        await self.session.commit()

        return await self.get(author_id)

    async def __scalars(self, statement: Executable) -> list[Author | None]:
        result = await self.session.scalars(statement)
        return list(result.all())
