import logging
from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Any,
)
from uuid import (
    UUID,
)

from asyncpg import (
    UniqueViolationError,
)
from sqlalchemy import (
    delete,
    select,
    update,
)
from sqlalchemy.exc import (
    IntegrityError,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from permissions.exceptions import (
    PermissionNameExistsError,
)
from src.permissions import (
    models as permissions_models,
)
from src.permissions import (
    schemas as permissions_schemas,
)

logger = logging.getLogger("root")


class PermissionRepository(ABC):
    @abstractmethod
    async def get(self, permission_id: UUID) -> permissions_schemas.Permission | None:
        ...

    @abstractmethod
    async def get_by_src(self, src: str) -> permissions_schemas.Permission | None:
        ...

    @abstractmethod
    async def get_all(self) -> list[permissions_schemas.Permission]:
        ...

    @abstractmethod
    async def update(
        self, permission_id: UUID, src: str | None = None, type: str | None = None
    ) -> permissions_schemas.Permission:
        ...

    @abstractmethod
    async def create(self, src: str, type: str) -> permissions_schemas.Permission:
        ...

    @abstractmethod
    async def create_bulk(self, names: list[str], type: str) -> list[permissions_schemas.Permission]:
        ...

    @abstractmethod
    async def filter_by(self, **kwargs: Any) -> list[permissions_schemas.Permission]:
        ...

    @abstractmethod
    async def remove(self, permission_id: UUID) -> None:
        ...


class PostgresPermissionRepository(PermissionRepository):
    def __init__(self, async_session: AsyncSession) -> None:
        self.async_session = async_session

    async def get(self, permission_id: UUID) -> permissions_schemas.Permission | None:
        stmt = select(permissions_models.Permission).where(permissions_models.Permission.id == permission_id)
        result = await self.async_session.execute(stmt)
        permission = result.scalar()

        if permission is None:
            return None

        return permissions_schemas.Permission.model_validate(permission)

    async def get_by_src(self, src: str) -> permissions_schemas.Permission | None:
        stmt = select(permissions_models.Permission).where(permissions_models.Permission.src == src)
        result = await self.async_session.execute(stmt)
        permission = result.scalar()

        if permission is None:
            return None

        return permissions_schemas.Permission.model_validate(permission)

    async def get_all(self) -> list[permissions_schemas.Permission]:
        stmt = select(permissions_models.Permission)
        result = await self.async_session.execute(stmt)
        permissions = result.scalars()

        schemas = [permissions_schemas.Permission.model_validate(permission) for permission in permissions]

        return schemas

    async def update(
        self, permission_id: UUID, src: str | None = None, type: str | None = None
    ) -> permissions_schemas.Permission:
        mapping = zip(("src", "type"), (src, type))
        values_to_update = {k: v for k, v in mapping if v is not None}
        stmt = (
            update(permissions_models.Permission)
            .where(permissions_models.Permission.id == permission_id)
            .values(**values_to_update)
        )
        await self.async_session.execute(stmt)

        return await self.get(permission_id)  # type: ignore

    async def create(self, src: str, type: str) -> permissions_schemas.Permission:
        try:
            permission = permissions_models.Permission(
                src=src,
                type=type,
            )
            self.async_session.add(permission)
            await self.async_session.commit()

            return await self.get(permission.id)  # type: ignore

        except UniqueViolationError as e:
            await self.async_session.rollback()
            logger.error(
                "UniqueViolationError: While adding permission with src[%s] and type[%s]: %s",
                src,
                type,
                e,
            )
            raise PermissionNameExistsError from e

        except IntegrityError as e:
            await self.async_session.rollback()
            logger.error(
                "IntegrityError: While adding permission with src[%s] and type[%s]: %s",
                src,
                type,
                e,
            )
            raise PermissionNameExistsError from e

    async def create_bulk(self, names: list[str], type: str) -> list[permissions_schemas.Permission]:
        permissions = [
            permissions_models.Permission(
                name=name,
                type=type,
            )
            for name in names
        ]

        self.async_session.add_all(permissions)
        await self.async_session.commit()

        return [permissions_schemas.Permission.model_validate(permission) for permission in permissions]

    async def filter_by(self, **kwargs: Any) -> list[permissions_schemas.Permission]:
        stmt = select(permissions_models.Permission).filter_by(**kwargs)
        result = await self.async_session.execute(stmt)
        permissions = result.scalars().all()

        return [permissions_schemas.Permission.model_validate(permission) for permission in permissions]

    async def remove(self, permission_id: UUID) -> None:
        stmt = delete(permissions_models.Permission).where(
            permissions_models.Permission.id == str(permission_id)
        )
        await self.async_session.execute(stmt)
        await self.async_session.commit()
