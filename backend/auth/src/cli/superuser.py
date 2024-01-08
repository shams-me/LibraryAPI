from redis import asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from permissions.enums import ServiceInternalRoles
from role.models import Role
from src.auth import dependencies as auth_depends
from src.auth.dependencies import get_auth_backend
from src.permissions.repositories import PostgresPermissionRepository
from src.permissions.services import PermissionsService
from src.settings.app import get_app_settings
from src.users import schemas as users_schemas
from src.users.repositories import PostgresUserRepository, PostgresUserSigninHistoryRepository
from src.users.service import UserService
from .database import get_async_db_session

settings = get_app_settings()


async def create_user_with_internal_permissions(
    user: auth_depends.UserSignUp,
) -> tuple[users_schemas.User, list[str],]:
    async with get_async_db_session() as session:
        session: AsyncSession
        user_service = await get_user_service(session)

        created_user = await user_service.create_user(
            username=user.username,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
        )

        role = await session.scalar(select(Role).where(Role.name == ServiceInternalRoles.superadmin))

        if role:
            await user_service.assign_user_role(
                created_user.id,
                role.id,
            )
            return (
                created_user,
                [role.name],
            )

        role = Role(name=ServiceInternalRoles.superadmin)
        session.add(role)
        await session.commit()

        await user_service.assign_user_role(
            created_user.id,
            role.id,
        )
        return (
            created_user,
            [role.name],
        )


async def get_user_service(db: AsyncSession) -> UserService:
    auth_backend = await get_auth_backend(redis=aioredis.from_url(settings.redis.dsn, encoding="utf-8"))
    return UserService(
        user_repository=PostgresUserRepository(session=db),
        log_repository=PostgresUserSigninHistoryRepository(session=db),
        jwt_auth_backend=auth_backend,
    )


async def get_permission_service(db: AsyncSession) -> PermissionsService:
    return PermissionsService(permissions_repo=PostgresPermissionRepository(async_session=db))
