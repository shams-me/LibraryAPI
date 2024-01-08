from typing import (
    Annotated,
)

from fastapi import (
    Depends,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from src.categories.repository import (
    ICategoryRepository,
    PostgresCategoryRepository,
)
from src.common.database import (
    get_db,
)


async def get_category_repository(
    db_session: Annotated[AsyncSession, Depends(get_db)],
) -> ICategoryRepository:
    return PostgresCategoryRepository(db_session)
