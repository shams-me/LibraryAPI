import asyncio
from time import (
    time,
)
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    cast,
)
from unittest import (
    mock,
)
from uuid import (
    uuid4,
)

import pytest_asyncio
from fastapi_cache import (
    FastAPICache,
)
from fastapi_cache.backends.redis import (
    RedisBackend,
)
from fastapi_limiter import (
    FastAPILimiter,
)
from httpx import (
    AsyncClient,
)
from jose import (
    jwt,
)
from redis import (
    asyncio as aioredis,
)
from sqlalchemy import (
    Engine,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import (
    sessionmaker,
)

from src.common.database import (
    Base,
    get_db,
)
from src.common.schemas import (
    JwtClaims,
    JwtUserSchema,
)
from src.main import (
    app,
)
from src.settings.app import (
    get_app_settings,
)

settings = get_app_settings()

GetRequestType = Callable[[str, dict[str, Any]], Awaitable[tuple[dict, int]]]


@pytest_asyncio.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def postgres_engine():
    engine = create_async_engine(
        settings.postgres.dsn,
        echo=settings.service.debug,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(
    postgres_engine: Engine,
):
    async_session = cast(
        sessionmaker,
        sessionmaker(
            cast(
                Engine,
                postgres_engine,
            ),
            class_=AsyncSession,
            expire_on_commit=False,
        ),
    )

    async def override_get_db() -> AsyncGenerator[
        None,
        AsyncSession,
    ]:
        async with async_session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    async with async_session() as db:
        yield db


@pytest_asyncio.fixture(scope="function")
async def client():
    base_url = f"http://{settings.service.host}:{settings.service.port}/api/v1"
    async with AsyncClient(
        app=app,
        base_url=base_url,
    ) as client:
        yield client


@pytest_asyncio.fixture(
    scope="session",
    autouse=True,
)
async def setup_fastapi_limiter():
    _redis = aioredis.from_url(
        settings.redis.dsn,
        encoding="utf-8",
    )
    await FastAPILimiter.init(_redis)
    FastAPICache.init(
        RedisBackend(_redis),
        prefix="fastapi-cache",
    )
    yield


@pytest_asyncio.fixture(
    scope="session",
    autouse=True,
)
async def mock_jwt():
    jwt_user = JwtUserSchema(
        id=str(uuid4()),
        role="superadmin",
        permissions={
            "books": [
                "READ",
                "CREATE",
                "UPDATE",
                "DELETE",
            ]
        },
    )
    jwt_claim = JwtClaims(
        user=jwt_user,
        iat=int(time()),
        access_jti="test",
        refresh_jti="test",
        type="access",
        exp=int(time()) + 600,
    )

    with mock.patch("src.common.authorization.decode_token") as mock_jwt:
        mock_jwt.return_value = jwt_claim
        yield jwt_claim


@pytest_asyncio.fixture(
    scope="session",
    autouse=True,
)
async def mock_jwt_token(
    mock_jwt,
):
    encoded_jwt = jwt.encode(
        mock_jwt.model_dump(),
        settings.auth.jwt_secret_key,
        algorithm=settings.auth.jwt_encoding_algorithm,
    )
    yield encoded_jwt
