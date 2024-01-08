from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.authors.repository import IAuthorRepository, PostgresAuthorRepository
from src.common.database import get_db


async def get_author_repository(db_session: Annotated[AsyncSession, Depends(get_db)]) -> IAuthorRepository:
    return PostgresAuthorRepository(db_session)
