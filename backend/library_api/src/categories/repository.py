import abc
from abc import ABC
from typing import TypeVar, Generic
from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import Executable

from src.authors.models import Author  # noqa: F401
from src.books.models import Book  # noqa: F401
from src.categories.exceptions import CategoryNotFound
from src.categories.models import Category
from src.common.database import Base

TModel = TypeVar("TModel", bound=Base)


class ICategoryRepository(
    abc.ABC,
    Generic[TModel],
):
    @abc.abstractmethod
    async def insert(self, name: str, description: str | None = None) -> TModel | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, category_id: UUID) -> TModel | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def all(self) -> list[TModel]:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, category_id: UUID):
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, category_id: UUID, name: str, description: str) -> TModel:
        raise NotImplementedError


class PostgresCategoryRepository(
    ICategoryRepository[Category],
    ABC,
):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(
        self,
        name: str,
        description: str | None = None,
    ) -> Category:
        category = Category(name=name, description=description)
        self.session.add(category)
        await self.session.commit()
        return category

    async def get(self, category_id: UUID) -> Category | None:
        category = await self.session.get(
            Category,
            category_id,
        )

        if category:
            return category  # type: ignore

        raise CategoryNotFound(category_id)

    async def all(self) -> list[Category | None]:
        stmt = select(Category)
        return await self.__scalars(stmt)

    async def delete(self, category_id: UUID) -> None:
        stmt = delete(Category).where(Category.id == category_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update(
        self, category_id: UUID, name: str | None = None, description: str | None = None
    ) -> Category:
        mapping = zip(("name", "description"), (name, description))
        values_to_update = {k: v for k, v in mapping if v is not None}

        stmt = update(Category).where(Category.id == category_id).values(**values_to_update)
        await self.session.execute(stmt)
        await self.session.commit()

        return await self.get(category_id)

    async def __scalars(self, statement: Executable) -> list[Category | None]:
        result = await self.session.scalars(statement)
        return list(result.all())
