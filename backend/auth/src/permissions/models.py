from enum import StrEnum, auto

from sqlalchemy import Enum, UniqueConstraint
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common import models
from src.common.database import Base


class PermissionType(StrEnum):
    READ = auto()
    CREATE = auto()
    DELETE = auto()
    UPDATE = auto()
    BLOCKED = auto()


class Permission(models.UUIDSchemaMixin, models.TimestampSchemaMixin, Base):
    __tablename__ = "permissions"

    src: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[PermissionType] = mapped_column(Enum(PermissionType), default=PermissionType.READ)

    role = relationship("Role", secondary="role_permissions", back_populates="permissions", uselist=False)

    __table_args__ = (UniqueConstraint(src, type, name="unique_src_type"),)

    def __repr__(self) -> str:
        return f"<Permission {self.src}>"
