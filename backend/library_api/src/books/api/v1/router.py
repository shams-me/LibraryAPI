from http import HTTPStatus
from typing import Annotated
from uuid import UUID


from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from fastapi_limiter.depends import RateLimiter
from fastapi_pagination import Page

from src.books import schemas
from src.books.dependencies import get_searched_books, get_book_repository
from src.books.repository import IBookRepository
from src.common.dependencies import check_permission
from src.common.enums import ServiceInternalSrc, ServiceInternalActions
from src.common.schemas import JwtClaims
from src.settings.app import get_app_settings

settings = get_app_settings()
book_settings = settings.books

router = APIRouter()


@router.post(
    path="",
    status_code=HTTPStatus.CREATED,
    response_model=None,
    summary="Create a new book",
    description="Endpoint to create a new book in the system. Requires book details as input.",
    response_description="The book has been created successfully.",
)
async def create_book(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    book: schemas.CreateBook,
    service: Annotated[IBookRepository, Depends(get_book_repository)],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.books,
                ServiceInternalActions.create,
            )
        ),
    ],
) -> None:
    return await service.insert(**book.model_dump(exclude_none=True))


@router.get(
    path="",
    status_code=HTTPStatus.OK,
    response_model=Page[schemas.Book],
    summary="Retrieve all books",
    description="Fetch a list of all books available in the system. The results are cached to enhance performance.",
    response_description="A list of books is returned. Empty list if no books are available.",
)
async def get_books(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    service: Annotated[IBookRepository, Depends(get_book_repository)],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.books,
                ServiceInternalActions.read,
            )
        ),
    ],
) -> Page[schemas.Book]:
    return await service.all()


@router.get(
    path="/search",
    status_code=HTTPStatus.OK,
    response_model=None,
    summary="Search book",
    description="Search book",
    response_description="",
)
@cache(expire=book_settings.cache_expire_in_seconds, namespace="searched_books")
async def search_book(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    books: list[schemas.Book] = Depends(get_searched_books),
) -> list[schemas.Book]:
    return books


@router.get(
    path="/{book_id:uuid}",
    status_code=HTTPStatus.OK,
    response_model=schemas.BookDetails | None,
    summary="Get book details",
    description="Retrieve the details of a specific book using its unique ID. The result is cached for efficient subsequent retrievals.",
    response_description="Details of the specified book or null if it does not exist.",
)
@cache(expire=book_settings.cache_expire_in_seconds, namespace="book_details")
async def get_book(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    book_id: UUID,
    service: Annotated[
        IBookRepository,
        Depends(get_book_repository),
    ],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.books,
                ServiceInternalActions.read,
            )
        ),
    ],
) -> schemas.BookDetails | None:
    return await service.get(book_id)


@router.put(
    path="/{book_id:uuid}",
    status_code=HTTPStatus.OK,
    response_model=schemas.BookDetails | None,
    summary="Update book details",
    description="",
    response_description="",
)
async def update_book(
    book_id: UUID,
    book: schemas.UpdateBook,
    service: Annotated[IBookRepository, Depends(get_book_repository)],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.books,
                ServiceInternalActions.read,
            )
        ),
    ],
) -> schemas.BookDetails | None:
    return await service.update(book_id, **book.model_dump(exclude_none=True))


@router.delete(
    path="/{book_id:uuid}",
    status_code=HTTPStatus.NO_CONTENT,
    response_model=None,
    summary="Delete a book",
    description="Remove a book from the system using its unique identifier. This action cannot be undone.",
    response_description="The book has been deleted successfully.",
)
async def delete_book(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    book_id: UUID,
    service: Annotated[
        IBookRepository,
        Depends(get_book_repository),
    ],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.books,
                ServiceInternalActions.delete,
            )
        ),
    ],
) -> None:
    return await service.delete(book_id)


@router.post(
    path="/{book_id:uuid}/category",
    status_code=HTTPStatus.CREATED,
    response_model=None,
    summary="Add category to book",
    description="Add category to book",
    response_description="",
)
async def add_category_to_book(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    book_id: UUID,
    category_id: UUID,
    service: Annotated[IBookRepository, Depends(get_book_repository)],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.books_categories,
                ServiceInternalActions.create,
            )
        ),
    ],
) -> None:
    return await service.add_category(
        book_id,
        category_id,
    )


@router.delete(
    path="/{book_id:uuid}/category",
    status_code=HTTPStatus.NO_CONTENT,
    response_model=None,
    summary="Delete category from book",
    description="Delete category from book",
    response_description="",
)
async def remove_category_to_book(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    book_id: UUID,
    category_id: UUID,
    service: Annotated[
        IBookRepository,
        Depends(get_book_repository),
    ],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.books_categories,
                ServiceInternalActions.delete,
            )
        ),
    ],
) -> None:
    return await service.remove_category(
        book_id,
        category_id,
    )


@router.post(
    path="/{book_id:uuid}/author",
    status_code=HTTPStatus.CREATED,
    response_model=None,
    summary="Add author to book",
    description="Add author to book",
    response_description="",
)
async def add_author_to_book(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    book_id: UUID,
    author_id: UUID,
    service: Annotated[IBookRepository, Depends(get_book_repository)],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.books_authors,
                ServiceInternalActions.create,
            )
        ),
    ],
) -> None:
    return await service.add_author(
        book_id,
        author_id,
    )


@router.delete(
    path="/{book_id:uuid}/author",
    status_code=HTTPStatus.NO_CONTENT,
    response_model=None,
    summary="Delete author from book",
    description="Delete author from book",
    response_description="",
)
async def remove_author_to_book(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            )
        ),
    ],
    book_id: UUID,
    author_id: UUID,
    service: Annotated[IBookRepository, Depends(get_book_repository)],
    _: Annotated[
        JwtClaims | None,
        Depends(
            check_permission(
                ServiceInternalSrc.books_authors,
                ServiceInternalActions.delete,
            )
        ),
    ],
) -> None:
    return await service.remove_author(
        book_id,
        author_id,
    )
