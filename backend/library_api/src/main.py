import logging
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse, Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_limiter import FastAPILimiter
from fastapi_pagination import add_pagination
from opentelemetry import trace
from redis import asyncio as aioredis

from src.authors.api.v1 import router as author_router
from src.books.api.v1 import router as book_router
from src.categories.api.v1 import router as category_router
from src.common import database
from src.common.utils import ESHandler
from src.settings.app import get_app_settings
from src.tracer.config import configure_tracer

settings = get_app_settings()
logging.config.dictConfig(settings.logging.config)


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.redis = aioredis.from_url(settings.redis.dsn, encoding="utf-8")
    database.es_handler = ESHandler(client=AsyncElasticsearch(settings.elastic.dsn))
    FastAPICache.init(RedisBackend(database.redis), prefix="fastapi-cache")
    await FastAPILimiter.init(database.redis)
    database.init_database(settings)
    yield
    await database.redis.close()


app = FastAPI(
    lifespan=lifespan,
    title=settings.service.name,
    description=settings.service.description,
    docs_url="/library/api/openapi",
    openapi_url="/library/api/openapi.json",
    default_response_class=ORJSONResponse,
    version="0.1.0",
)


@app.get("/ping")
def pong() -> dict[str, str]:
    return {"ping": "pong!"}


@app.middleware("http")
async def check_request_id(request: Request, call_next: Callable[[Request], Awaitable[Response]]):
    if not settings.is_development:
        request_id = request.headers.get("X-Request-Id")
        if not request_id:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "X-Request-Id is required"},
            )
    return await call_next(request)


@app.middleware("http")
async def setup_request_id_for_jaeger(request: Request, call_next: Callable[[Request], Awaitable[Response]]):
    request_id = request.headers.get("X-Request-Id")
    if settings.jaeger.enabled and request_id is not None:
        tracer = trace.get_tracer(__name__)
        span = tracer.start_span("request")
        span.set_attribute(
            "http.request_id",
            request_id,
        )
        span.end()
    return await call_next(request)


app.include_router(category_router.router, prefix="/library/api/v1/categories", tags=["Category"])
app.include_router(author_router.router, prefix="/library/api/v1/authors", tags=["Author"])
app.include_router(book_router.router, prefix="/library/api/v1/books", tags=["Book"])

add_pagination(app)

if settings.jaeger.enabled:
    configure_tracer(app)

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.service.host,
        port=settings.service.port,
        log_config=settings.logging.config,
        reload=True,
    )
