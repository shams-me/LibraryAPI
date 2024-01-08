from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UUIDSchemaMixin(BaseModel):
    id: UUID


class TimestampSchemaMixin(BaseModel):
    created_at: datetime
    modified_at: datetime
