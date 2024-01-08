from typing import Callable, Coroutine

from fastapi import Depends

from src.auth.dependencies import handle_access_token
from src.auth.jwt import schemas as jwt_schemas
from src.permissions.enums import (
    ServiceInternalRoles,
    ServiceInternalActions,
    ServiceInternalPermission,
    ServiceInternalSrc,
)
from src.permissions.exceptions import PermissionNotGrantedError, PermissionUserBlocked

CheckPermissionsType = Callable[[jwt_schemas.JWTDecoded], Coroutine[None, None, jwt_schemas.JWTDecoded]]


def check_permission(
    src: ServiceInternalSrc,
    action: ServiceInternalActions,
) -> CheckPermissionsType:
    async def _check_permission(
        access_token: jwt_schemas.JWTDecoded = Depends(handle_access_token),
    ) -> jwt_schemas.JWTDecoded:
        if access_token.user.role == ServiceInternalRoles.superadmin:
            return access_token

        permissions = access_token.user.permissions.get(src, [])

        if ServiceInternalPermission.blocked in permissions:
            raise PermissionUserBlocked

        if action.upper() not in permissions:
            raise PermissionNotGrantedError

        return access_token

    return _check_permission
