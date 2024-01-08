from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from fastapi_limiter.depends import RateLimiter
from fastapi_pagination import Page

from src.authors import schemas
from src.authors.dependencies import get_author_repository
from src.authors.repository import IAuthorRepository
from src.common.dependencies import check_permission
from src.common.enums import ServiceInternalSrc, ServiceInternalActions
from src.common.schemas import JwtClaims
from src.settings.app import get_app_settings

settings = get_app_settings()
author_settings = get_app_settings().author

router = APIRouter()


@router.post(
    path="",
    status_code=HTTPStatus.CREATED,
    response_model=schemas.Author,
    summary="Create a new author",
    description="Endpoint to create a new author in the system. Requires author details as input.",
    response_description="The author has been created successfully.",
)
async def create_author(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    author: schemas.BaseAuthor,
    service: Annotated[IAuthorRepository, Depends(get_author_repository)],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.authors,
                ServiceInternalActions.create,
            )
        ),
    ],
) -> schemas.Author:
    return await service.insert(**author.model_dump(exclude_none=True))


@router.get(
    path="",
    status_code=HTTPStatus.OK,
    response_model=Page[schemas.Author],
    summary="Retrieve all authors",
    description="Fetch a list of all authors available in the system. The results are cached to enhance performance.",
    response_description="A list of authors is returned. Empty list if no authors are available.",
)
@cache(
    expire=author_settings.cache_expire_in_seconds,
    namespace="authors",
)
async def get_authors(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    service: Annotated[IAuthorRepository, Depends(get_author_repository)],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.authors,
                ServiceInternalActions.read,
            )
        ),
    ],
) -> Page[schemas.Author]:
    return await service.all()


@router.get(
    path="/{author_id:uuid}",
    status_code=HTTPStatus.OK,
    response_model=schemas.AuthorDetails | None,
    summary="Get author details",
    description="Retrieve the details of a specific author using its unique ID. The result is cached for efficient subsequent retrievals.",
    response_description="Details of the specified author or null if it does not exist.",
)
@cache(
    expire=author_settings.cache_expire_in_seconds,
    namespace="author_details",
)
async def get_author(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    author_id: UUID,
    service: Annotated[IAuthorRepository, Depends(get_author_repository)],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.authors,
                ServiceInternalActions.read,
            )
        ),
    ],
) -> schemas.AuthorDetails | None:
    return await service.get(author_id)


@router.put(
    path="/{author_id:uuid}",
    status_code=HTTPStatus.OK,
    response_model=schemas.Author,
    summary="Update a author",
    description="Updates the details of an existing author using its unique ID. Allows modification of specified fields within the author record.",
    response_description="The updated author details or null if the author does not exist or the update failed.",
)
async def update_author(
    author_id: UUID,
    author: schemas.UpdateAuthor,
    service: Annotated[IAuthorRepository, Depends(get_author_repository)],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.authors,
                ServiceInternalActions.update,
            )
        ),
    ],
) -> schemas.Author:
    return await service.update(author_id, **author.model_dump(exclude_none=True))


@router.delete(
    path="/{author_id:uuid}",
    status_code=HTTPStatus.NO_CONTENT,
    response_model=None,
    summary="Delete a author",
    description="Remove a author from the system using its unique identifier. This action cannot be undone.",
    response_description="The author has been deleted successfully.",
)
async def delete_author(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    author_id: UUID,
    service: Annotated[IAuthorRepository, Depends(get_author_repository)],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.authors,
                ServiceInternalActions.delete,
            )
        ),
    ],
) -> None:
    return await service.delete(author_id)
