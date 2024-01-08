from abc import ABC, abstractmethod
from typing import Annotated, Any, cast
from uuid import UUID

from fastapi import Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import delete, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from permissions.enums import ServiceInternalRoles
from src.common.database import get_db
from src.permissions import models as permissions_models
from src.role import models as role_models
from src.users import models as users_models
from src.users import schemas as users_schemas
from src.users.utils import hash_password, verify_password


class UserSignInHistoryRepository(ABC):
    @abstractmethod
    async def get_user_signin_history(self, user_id) -> Page[users_schemas.UserLoginRecord]:
        ...

    @abstractmethod
    async def create_record(
        self, user_id: UUID, user_agent: str, ip_address: str
    ) -> users_schemas.UserLoginRecord:
        ...


class UserRepository(ABC):
    @abstractmethod
    async def get(self, user_id: UUID) -> users_schemas.User | None:
        ...

    @abstractmethod
    async def get_by_ids(self, ids: list[UUID]) -> list[users_schemas.User]:
        ...

    @abstractmethod
    async def filter_by(self, **kwargs: Any) -> list[users_schemas.User]:
        ...

    @abstractmethod
    async def update(
        self,
        user_id: UUID,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> users_schemas.User:
        ...

    @abstractmethod
    async def create(
        self, username: str, first_name: str, last_name: str, password: str, email: str | None
    ) -> users_schemas.User:
        ...

    @abstractmethod
    async def change_password(self, user_id: UUID, new_password: str) -> users_schemas.User:
        ...

    @abstractmethod
    async def check_password(self, user_id: UUID, password: str) -> bool:
        ...

    @abstractmethod
    async def assign_role(self, user_id: UUID, role_id: UUID) -> users_schemas.User:
        ...

    @abstractmethod
    async def assign_permission(self, user_id: UUID, permission_id: UUID) -> users_schemas.User:
        ...

    @abstractmethod
    async def assign_bulk_permissions(self, user_id: UUID, permission_ids: list[UUID]) -> users_schemas.User:
        ...

    @abstractmethod
    async def revoke_permission(self, user_id: UUID, permission_id: UUID) -> users_schemas.User:
        ...

    @abstractmethod
    async def revoke_role(self, user_id: UUID, role_id: UUID) -> users_schemas.User:
        ...

    @abstractmethod
    async def delete_user(self, user_id: UUID) -> None:
        ...


class PostgresUserSigninHistoryRepository(UserSignInHistoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_signin_history(self, user_id) -> Page[users_schemas.UserLoginRecord]:
        stmt = select(users_models.UserSigninHistory).where(users_models.UserSigninHistory.user_id == user_id)

        def transformer(
            items: list[users_models.UserSigninHistory],
        ) -> list[users_schemas.UserLoginRecord]:
            return [users_schemas.UserLoginRecord.model_validate(record) for record in items]

        return await paginate(self.session, stmt, transformer=transformer)  # type: ignore

    async def create_record(
        self, user_id: UUID, user_agent: str, ip_address: str
    ) -> users_schemas.UserLoginRecord:
        record = users_models.UserSigninHistory(user_id=user_id, user_agent=user_agent, ip_address=ip_address)

        self.session.add(record)
        await self.session.commit()

        return users_schemas.UserLoginRecord.model_validate(record)


class PostgresUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, user_id: UUID) -> users_schemas.User | None:
        user = await self.session.get(
            users_models.User,
            user_id,
        )

        if user is None:
            return None

        permissions = await self.__get_permissions(user.id)

        user_schema = users_schemas.User(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.name if user.role else ServiceInternalRoles.guest,
            permissions=permissions,
        )

        return user_schema

    async def get_by_ids(self, ids: list[UUID]) -> list[users_schemas.User]:
        stmt = (
            select(users_models.User)
            .options(
                joinedload(users_models.User.permissions).joinedload(users_models.UserPermissions.permission)
            )
            .where(users_models.User.id.in_(ids))
        )
        result = await self.session.execute(stmt)
        users = result.unique().scalars().all()

        return [
            users_schemas.User(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                permissions=[user_permission.Permission.src for user_permission in user.permissions],
            )
            for user in users
        ]

    async def filter_by(self, **kwargs: Any) -> list[users_schemas.User]:
        stmt = select(users_models.User).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        users = result.unique().scalars().all()

        return [
            users_schemas.User(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role.name if user.role else ServiceInternalRoles.guest,
                permissions=await self.__get_permissions(user.id),
            )
            for user in users
        ]

    async def update(
        self,
        user_id: UUID,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> users_schemas.User:
        mapping = zip(("username", "first_name", "last_name"), (username, first_name, last_name))
        values_to_update = {k: v for k, v in mapping if v is not None}

        stmt = update(users_models.User).where(users_models.User.id == user_id).values(**values_to_update)
        await self.session.execute(stmt)

        return cast(
            users_schemas.User,
            await self.get(user_id),
        )

    async def create(
        self, username: str, first_name: str, last_name: str, password: str, email: str | None = None
    ) -> users_schemas.User:
        user = users_models.User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=hash_password(password),
        )
        self.session.add(user)
        await self.session.commit()

        return cast(users_schemas.User, await self.get(user.id))

    async def change_password(self, user_id: UUID, new_password: str) -> users_schemas.User:
        stmt = (
            update(users_models.User)
            .where(users_models.User.id == user_id)
            .values(password=hash_password(new_password))
        )
        await self.session.execute(stmt)
        await self.session.commit()

        return cast(
            users_schemas.User,
            await self.get(user_id),
        )

    async def check_password(self, user_id: UUID, password: str) -> bool:
        stmt = select(users_models.User.password).where(users_models.User.id == user_id)
        result = await self.session.execute(stmt)

        password_row = result.first()
        if password_row is None:
            raise ValueError(f"there is not User with {user_id=}")

        current_password = password_row[0]
        return verify_password(password, current_password)

    async def assign_permission(self, user_id: UUID, permission_id: UUID) -> users_schemas.User:
        user_permission = users_models.UserPermissions(
            user_id=user_id,
            permission_id=permission_id,
        )
        self.session.add(user_permission)
        await self.session.commit()

        return cast(users_schemas.User, await self.get(user_id))

    async def assign_bulk_permissions(self, user_id: UUID, permission_ids: list[UUID]) -> users_schemas.User:
        users_permissions = [
            users_models.UserPermissions(user_id=user_id, permission_id=permission_id)
            for permission_id in permission_ids
        ]

        self.session.add_all(users_permissions)
        await self.session.commit()

        return cast(
            users_schemas.User,
            await self.get(user_id),
        )

    async def revoke_permission(self, user_id: UUID, permission_id: UUID) -> users_schemas.User:
        stmt = (
            delete(users_models.UserPermissions)
            .where(users_models.UserPermissions.user_id == user_id)
            .where(users_models.UserPermissions.permission_id == permission_id)
        )
        await self.session.execute(stmt)

        return cast(
            users_schemas.User,
            await self.get(user_id),
        )

    async def revoke_role(self, user_id: UUID, role_id: UUID) -> users_schemas.User:
        stmt = (
            delete(users_models.UserRole)
            .where(users_models.UserRole.user_id == user_id)
            .where(users_models.UserRole.role_id == role_id)
        )
        await self.session.execute(stmt)

        return cast(
            users_schemas.User,
            await self.get(user_id),
        )

    async def assign_role(self, user_id: UUID, role_id: UUID) -> users_schemas.User:
        user_permission = users_models.UserRole(
            user_id=user_id,
            role_id=role_id,
        )
        self.session.add(user_permission)
        await self.session.commit()

        return cast(users_schemas.User, await self.get(user_id))

    async def delete_user(self, user_id: UUID) -> None:
        stmt = delete(users_models.User).where(users_models.User.id == user_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def __get_permissions(
        self, user_id: UUID
    ) -> dict[str, list[str],] | None:
        # Part 1: Direct permissions assigned to users
        direct_permissions_subquery = (
            select(
                users_models.User.username,
                permissions_models.Permission.src,
                func.array_agg(func.distinct(permissions_models.Permission.type)).label("types"),
            )
            .join(
                users_models.UserPermissions,
                users_models.User.id == users_models.UserPermissions.user_id,
            )
            .join(
                permissions_models.Permission,
                users_models.UserPermissions.permission_id == permissions_models.Permission.id,
            )
            .where(users_models.User.id == user_id)
            .group_by(
                users_models.User.username,
                permissions_models.Permission.src,
            )
            .subquery()
        )

        # Part 2: Permissions assigned through roles
        role_permissions_subquery = (
            select(
                users_models.User.username,
                permissions_models.Permission.src,
                func.array_agg(func.distinct(permissions_models.Permission.type)).label("types"),
            )
            .join(
                users_models.UserRole,
                users_models.User.id == users_models.UserRole.user_id,
            )
            .join(
                role_models.Role,
                users_models.UserRole.role_id == role_models.Role.id,
            )
            .join(
                role_models.RolePermissions,
                role_models.Role.id == role_models.RolePermissions.role_id,
            )
            .join(
                permissions_models.Permission,
                role_models.RolePermissions.permission_id == permissions_models.Permission.id,
            )
            .where(users_models.User.id == user_id)
            .group_by(
                users_models.User.username,
                permissions_models.Permission.src,
            )
            .subquery()
        )

        # Combining both queries
        final_query = select(
            direct_permissions_subquery.c.username,
            direct_permissions_subquery.c.src,
            direct_permissions_subquery.c.types,
        ).union(
            select(
                role_permissions_subquery.c.username,
                role_permissions_subquery.c.src,
                role_permissions_subquery.c.types,
            )
        )

        result = await self.session.execute(final_query)
        rows = result.fetchall()

        return {row.src: row.types for row in rows}


async def get_user_repository(db_session: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    return PostgresUserRepository(db_session)


async def get_user_sign_in_history_repository(
    db_session: Annotated[AsyncSession, Depends(get_db)]
) -> UserSignInHistoryRepository:
    return PostgresUserSigninHistoryRepository(db_session)
