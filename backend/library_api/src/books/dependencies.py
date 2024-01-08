from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.books.params import BookRequestParams
from src.books.repository import ESBookRepository
from src.books.repository import IBookRepository, PostgresBookRepository
from src.books.schemas import Book

from src.common.database import get_db
from src.common.database import get_elastic_handler
from src.common.utils import ESHandler, models_to_schemas
from src.settings.app import get_app_settings

settings = get_app_settings()


@lru_cache()
def get_book_repo(es_handler: ESHandler = Depends(get_elastic_handler)) -> ESBookRepository:
    return ESBookRepository(es_handler, settings.books.elastic_index, schema=Book)


async def get_searched_books(
    request_params: BookRequestParams = Depends(BookRequestParams),
    service: ESBookRepository = Depends(get_book_repo),
):
    book_models = await service.find_by_query(request_params.to_es_params())
    return models_to_schemas(book_models, Book)


async def get_book_repository(
    db_session: Annotated[AsyncSession, Depends(get_db)],
) -> IBookRepository:
    return PostgresBookRepository(db_session)
