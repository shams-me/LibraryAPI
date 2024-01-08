import typing as tp
from enum import (
    Enum,
)

import structlog
from pydantic import (
    BaseModel,
    Field,
)

LoggerProcessors = (
    tp.Iterable[
        tp.Callable[
            [tp.Any, str, tp.MutableMapping[str, tp.Any]],
            tp.Mapping[str, tp.Any] | str | bytes | bytearray | tuple[tp.Any, ...],
        ]
    ]
    | None  # noqa: W503
)


class LoggerLevelType(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class LoggingSettings(BaseModel):
    class Config:
        use_enum_values = True

    fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    default_handlers: list[str] = ["console"]
    level: LoggerLevelType = Field(
        alias="logging_level",
        default=LoggerLevelType.DEBUG.value,
    )

    @property
    def config(
        self,
    ) -> dict[str, tp.Any,]:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "verbose": {"format": self.fmt},
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(levelprefix)s %(message)s",
                    "use_colors": None,
                },
                "access": {
                    "()": "uvicorn.logging.AccessFormatter",
                    "fmt": "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",  # noqa: E501
                },
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "verbose",
                },
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "": {
                    "handlers": self.default_handlers,
                    "level": "INFO",
                },
                "uvicorn.error": {
                    "level": "INFO",
                },
                "uvicorn.access": {
                    "handlers": ["access"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
            "root": {
                "level": self.level,
                "formatter": "verbose",
                "handlers": self.default_handlers,
            },
        }


def configure_logger(
    enable_async_logger: bool = False,
) -> None:
    """Configure structlog logger.

    Args:
        enable_async_logger: Enable async logger. Default: False.

    Returns:
        None.

    Note:
        Async logger should be called within async context.
    """
    shared_processors: LoggerProcessors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ExtraAdder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    logger_wrapper = (
        structlog.stdlib.AsyncBoundLogger if enable_async_logger else structlog.stdlib.BoundLogger
    )

    structlog.configure(
        processors=shared_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=logger_wrapper,
        cache_logger_on_first_use=True,
    )
