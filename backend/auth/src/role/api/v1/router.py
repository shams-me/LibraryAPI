from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter

from role.dependencies import get_role_repository
from src.auth.jwt import schemas as jwt_schemas
from src.common.dependencies import check_permission
from src.permissions import enums as permission_enums
from src.role import schemas as roles_schemas
from src.role.repository import IRoleRepository
from src.settings.app import get_app_settings

settings = get_app_settings()

router = APIRouter()


@router.post(
    path="/",
    response_model=roles_schemas.Role,
    summary="",
    description="",
    response_description="",
)
async def create_role(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    create_role: roles_schemas.BaseRole,
    service: Annotated[IRoleRepository, Depends(get_role_repository)],
    access_token: Annotated[
        jwt_schemas.JWTDecoded,
        Depends(
            check_permission(
                permission_enums.ServiceInternalSrc.roles,
                permission_enums.ServiceInternalPermission.create,
            )
        ),
    ],
) -> roles_schemas.Role:
    return await service.insert(name=create_role.name)


@router.delete(
    path="/{role_id:uuid}",
    response_model=roles_schemas.Role,
    summary="",
    description="",
    response_description="",
)
async def delete_role(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    role_id: UUID,
    service: Annotated[IRoleRepository, Depends(get_role_repository)],
    access_token: Annotated[
        jwt_schemas.JWTDecoded,
        Depends(
            check_permission(
                permission_enums.ServiceInternalSrc.roles,
                permission_enums.ServiceInternalPermission.delete,
            )
        ),
    ],
) -> roles_schemas.Role:
    return await service.delete(role_id)


@router.put(
    path="/{role_id:uuid}",
    response_model=roles_schemas.Role,
    summary="",
    description="",
    response_description="",
)
async def update_role(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    role_id: UUID,
    role_update: roles_schemas.UpdateRole,
    service: Annotated[IRoleRepository, Depends(get_role_repository)],
    access_token: Annotated[
        jwt_schemas.JWTDecoded,
        Depends(
            check_permission(
                permission_enums.ServiceInternalSrc.roles,
                permission_enums.ServiceInternalPermission.update,
            )
        ),
    ],
) -> roles_schemas.Role:
    return await service.update(role_id, name=role_update.name)


@router.get(
    path="/",
    response_model=list[roles_schemas.Role],
    summary="",
    description="",
    response_description="",
)
async def get_roles(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    service: Annotated[IRoleRepository, Depends(get_role_repository)],
    access_token: Annotated[
        jwt_schemas.JWTDecoded,
        Depends(
            check_permission(
                permission_enums.ServiceInternalSrc.roles,
                permission_enums.ServiceInternalPermission.read,
            )
        ),
    ],
) -> list[roles_schemas.Role]:
    return await service.all()
