from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.role.repository import IRoleRepository, PostgresRoleRepository
from src.common.database import get_db


async def get_role_repository(db_session: Annotated[AsyncSession, Depends(get_db)]) -> IRoleRepository:
    return PostgresRoleRepository(db_session)
