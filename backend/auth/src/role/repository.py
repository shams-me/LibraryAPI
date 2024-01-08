import abc
from abc import ABC
from typing import TypeVar, Generic
from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import Executable

from src.role.exceptions import RoleNotFound
from src.role.models import Role
from src.common.database import Base

TModel = TypeVar("TModel", bound=Base)


class IRoleRepository(abc.ABC, Generic[TModel]):
    @abc.abstractmethod
    async def insert(self, name: str) -> TModel | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, role_id: UUID) -> TModel | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def all(self) -> list[TModel]:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, role_id: UUID):
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, role_id: UUID, name: str) -> TModel:
        raise NotImplementedError


class PostgresRoleRepository(
    IRoleRepository[Role],
    ABC,
):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(self, name: str) -> Role:
        role = Role(name=name)
        self.session.add(role)
        await self.session.commit()
        return role

    async def get(self, role_id: UUID) -> Role | None:
        role = await self.session.get(Role, role_id)

        if role:
            return role  # type: ignore

        raise RoleNotFound(role_id)

    async def all(self) -> list[Role | None]:
        stmt = select(Role)
        return await self.__scalars(stmt)

    async def delete(self, role_id: UUID) -> None:
        stmt = delete(Role).where(Role.id == role_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update(self, role_id: UUID, name: str) -> Role:
        stmt = update(Role).where(Role.id == role_id).values(name=name)
        await self.session.execute(stmt)
        await self.session.commit()

        return await self.get(role_id)

    async def __scalars(self, statement: Executable) -> list[Role | None]:
        result = await self.session.scalars(statement)
        return list(result.all())
