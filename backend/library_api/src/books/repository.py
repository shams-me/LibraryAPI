from __future__ import annotations

import abc
import datetime
import logging
from abc import ABC
from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from asyncpg import UniqueViolationError
from fastapi_pagination import Page
from fastapi_pagination.ext.async_sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.base import Executable

from src.authors.models import Author  # noqa: F401
from src.books import schemas
from src.books.exceptions import (
    BookCategoryExists,
    BookAuthorExists,
    BookCategoryBadRequest,
    BookAuthorBadRequest,
    BookNotFound,
)
from src.books.models import Book, BookCategory, BookAuthors
from src.common.database import Base
from src.common.utils import ESHandler
from src.settings.app import get_app_settings

logger = logging.getLogger("root")
TModel = TypeVar("TModel", bound=Base)
TSchema = TypeVar("TSchema", bound=BaseModel)

settings = get_app_settings()


class ESBookRepository:
    def __init__(self, es_handler: ESHandler, index: str, schema: Type[TSchema]) -> None:
        self.es_handler = es_handler
        self.index = index
        self.schema = schema

    async def find_by_id(self, primary_key: Any) -> TSchema | None:
        if item := await self.es_handler.get_by_id(
            self.index,
            str(primary_key),
        ):
            return self.schema(**item)
        return None

    async def find_by_query(self, query: dict[str, Any]) -> list[TSchema]:
        raw_entities = await self.es_handler.get(
            self.index,
            query,
        )
        if not raw_entities:
            return []
        return [self.schema(**entity) for entity in raw_entities]


class IBookRepository(
    abc.ABC,
    Generic[TModel],
):
    @abc.abstractmethod
    async def insert(
        self,
        title: str,
        description: str | None = None,
        language: str | None = None,
        isbn: str | None = None,
        publication_date: datetime.datetime | None = None,
    ) -> TModel | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, book_id: UUID) -> TModel | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def all(self) -> Page[TSchema]:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, book_id: UUID):
        raise NotImplementedError

    @abc.abstractmethod
    async def update(
        self,
        book_id: UUID,
        title: str | None = None,
        description: str | None = None,
        language: str | None = None,
        isbn: str | None = None,
        publication_date: datetime.datetime | None = None,
    ) -> TModel | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def add_category(self, book_id: UUID, category_id: UUID) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def remove_category(self, book_id: UUID, category_id: UUID) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def add_author(self, book_id: UUID, author_id: UUID) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def remove_author(self, book_id: UUID, author_id: UUID) -> None:
        raise NotImplementedError


class PostgresBookRepository(
    IBookRepository[Book],
    ABC,
):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(
        self,
        title: str,
        description: str | None = None,
        language: str | None = None,
        isbn: str | None = None,
        publication_date: datetime.datetime | None = None,
    ) -> Book:
        mapping = zip(
            ("title", "description", "language", "isbn", "publication_date"),
            (title, description, language, isbn, publication_date),
        )
        values_to_insert = {k: v for k, v in mapping if v is not None}

        book = Book(**values_to_insert)
        self.session.add(book)
        await self.session.commit()
        return book

    async def get(self, book_id: UUID) -> Book | None:
        stmt = (
            select(Book)
            .where(Book.id == book_id)
            .options(
                joinedload(Book.authors),
                joinedload(Book.categories),
            )
        )
        book = await self.session.scalar(stmt)

        if book:
            return book

        raise BookNotFound(book_id)

    async def all(self) -> Page[schemas.Book]:
        stmt = select(Book)

        def transformer(
            items: list[schemas.Book],
        ) -> list[schemas.Book]:
            return [schemas.Book.model_validate(record) for record in items]

        return await paginate(self.session, stmt, transformer=transformer)  # type: ignore

    async def delete(self, book_id: UUID) -> None:
        stmt = delete(Book).where(Book.id == book_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update(
        self,
        book_id: UUID,
        title: str | None = None,
        description: str | None = None,
        language: str | None = None,
        isbn: str | None = None,
        publication_date: datetime.datetime | None = None,
    ) -> Book:
        mapping = zip(
            ("title", "description", "language", "isbn", "publication_date"),
            (title, description, language, isbn, publication_date),
        )
        values_to_update = {k: v for k, v in mapping if v is not None}

        stmt = update(Book).where(Book.id == book_id).values(**values_to_update)
        await self.session.execute(stmt)
        await self.session.commit()

        return await self.get(book_id)

    async def add_category(self, book_id: UUID, category_id: UUID) -> None:
        try:
            obj = BookCategory(
                book_id=book_id,
                category_id=category_id,
            )
            self.session.add(obj)
            await self.session.commit()
        except UniqueViolationError as e:
            await self.session.rollback()
            logger.error(
                "UniqueViolationError: While adding category[%s] to book[%s]: %s",
                category_id,
                book_id,
                e,
            )
            raise BookCategoryExists from e
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(
                "IntegrityError: While adding category[%s] to book[%s]: %s",
                category_id,
                book_id,
                e,
            )
            raise BookCategoryBadRequest from e

    async def remove_category(self, book_id: UUID, category_id: UUID) -> None:
        stmt = delete(BookCategory).where(
            BookCategory.category_id == category_id, BookCategory.book_id == book_id
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def add_author(self, book_id: UUID, author_id: UUID) -> None:
        try:
            obj = BookAuthors(book_id=book_id, author_id=author_id)
            self.session.add(obj)
            await self.session.commit()
        except UniqueViolationError as e:
            await self.session.rollback()
            logger.error(
                "UniqueViolationError: While adding author[%s] to book[%s]: %s", author_id, book_id, e
            )
            raise BookAuthorExists from e
        except IntegrityError as e:
            await self.session.rollback()
            logger.error("IntegrityError: While adding author[%s] to book[%s]: %s", author_id, book_id, e)
            raise BookAuthorBadRequest from e

    async def remove_author(self, book_id: UUID, author_id: UUID) -> None:
        stmt = delete(BookAuthors).where(BookAuthors.author_id == author_id, BookAuthors.book_id == book_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def __scalars(self, statement: Executable) -> list[Book | None]:
        result = await self.session.scalars(statement)
        return list(result.all())
