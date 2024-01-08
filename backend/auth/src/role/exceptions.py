from src.common.exceptions import ResourceNotFound


class RoleNotFound(ResourceNotFound):
    resource_name: str = "Role"
