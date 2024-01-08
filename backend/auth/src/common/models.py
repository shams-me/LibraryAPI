import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID as PUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class UUIDSchemaMixin:
    id: Mapped[uuid.UUID] = mapped_column(PUUID(), primary_key=True, default=uuid.uuid4)


class TimestampSchemaMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
