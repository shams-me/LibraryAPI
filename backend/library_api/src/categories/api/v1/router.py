from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from fastapi_limiter.depends import RateLimiter

from src.categories import schemas
from src.categories.dependencies import get_category_repository
from src.categories.repository import ICategoryRepository
from src.common.dependencies import (
    check_permission,
)
from src.common.enums import ServiceInternalSrc, ServiceInternalActions
from src.common.schemas import JwtClaims
from src.settings.app import (
    get_app_settings,
)

settings = get_app_settings()
category_settings = get_app_settings().category

router = APIRouter()


@router.post(
    path="",
    status_code=HTTPStatus.CREATED,
    response_model=schemas.Category,
    summary="Create a new category",
    description="Endpoint to create a new category in the system. Requires category details as input.",
    response_description="The category has been created successfully.",
)
async def create_category(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    category: schemas.BaseCategory,
    service: Annotated[ICategoryRepository, Depends(get_category_repository)],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.categories,
                ServiceInternalActions.create,
            )
        ),
    ],
) -> schemas.Category:
    return await service.insert(**category.model_dump(exclude_none=True))


@router.get(
    path="",
    status_code=HTTPStatus.OK,
    response_model=list[schemas.CategoryDetails],
    summary="Retrieve all categories",
    description="Fetch a list of all categories available in the system. The results are cached to enhance performance.",
    response_description="A list of categories is returned. Empty list if no categories are available.",
)
@cache(expire=category_settings.cache_expire_in_seconds, namespace="categories")
async def get_categories(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    service: Annotated[ICategoryRepository, Depends(get_category_repository)],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.categories,
                ServiceInternalActions.read,
            )
        ),
    ],
) -> list[schemas.Category]:
    return await service.all()


@router.get(
    path="/{category_id:uuid}",
    status_code=HTTPStatus.OK,
    response_model=schemas.CategoryDetails | None,
    summary="Get category details",
    description="Retrieve the details of a specific category using its unique ID. The result is cached for efficient subsequent retrievals.",
    response_description="Details of the specified category or null if it does not exist.",
)
@cache(expire=category_settings.cache_expire_in_seconds, namespace="category_details")
async def get_category(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    category_id: UUID,
    service: Annotated[ICategoryRepository, Depends(get_category_repository)],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.categories,
                ServiceInternalActions.read,
            )
        ),
    ],
) -> schemas.CategoryDetails | None:
    return await service.get(category_id)


@router.put(
    path="/{category_id:uuid}",
    status_code=HTTPStatus.OK,
    response_model=schemas.Category,
    summary="Update a category",
    description="Updates the details of an existing category using its unique ID. Allows modification of specified fields within the category record.",
    response_description="The updated category details or null if the category does not exist or the update failed.",
)
async def update_category(
    category_id: UUID,
    category: schemas.UpdateCategory,
    service: Annotated[ICategoryRepository, Depends(get_category_repository)],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.categories,
                ServiceInternalActions.update,
            )
        ),
    ],
) -> schemas.Category:
    return await service.update(category_id, **category.model_dump(exclude_none=True))


@router.delete(
    path="/{category_id:uuid}",
    status_code=HTTPStatus.NO_CONTENT,
    response_model=None,
    summary="Delete a category",
    description="Remove a category from the system using its unique identifier. This action cannot be undone.",
    response_description="The category has been deleted successfully.",
)
async def delete_category(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    category_id: UUID,
    service: Annotated[ICategoryRepository, Depends(get_category_repository)],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.categories,
                ServiceInternalActions.delete,
            )
        ),
    ],
) -> None:
    return await service.delete(category_id)
