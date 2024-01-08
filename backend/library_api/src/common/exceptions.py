from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException


class AppBaseError(Exception):
    pass


class ResourceNotFound(HTTPException):
    resource_name = "Resource"

    def __init__(self, resource_id: UUID) -> None:
        super().__init__(HTTPStatus.NOT_FOUND, f"{self.resource_name} {resource_id} was not found")


class ResourceConflict(HTTPException):
    resource_name = "Resource"

    def __init__(self) -> None:
        super().__init__(HTTPStatus.CONFLICT, f"{self.resource_name} already exists.")


class BadRequest(HTTPException):
    source = "Source"
    relation = "Relation"

    def __init__(self) -> None:
        super().__init__(
            HTTPStatus.CONFLICT, f"Provided {self.source} id or {self.relation} id not found in database."
        )


class ElasticsearchRepositoryError(AppBaseError):
    pass


class AuthIsUnavailableError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            HTTPStatus.SERVICE_UNAVAILABLE, "Authorization service is unavailable. Please try again later."
        )
