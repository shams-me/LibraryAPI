from sqlalchemy import (
    ForeignKey,
    String,
    UniqueConstraint,
    UUID,
)
from sqlalchemy.orm import (
    mapped_column,
    relationship,
    Mapped,
)

from src.common import (
    models,
)
from src.common.database import (
    Base,
)


class Role(models.UUIDSchemaMixin, models.TimestampSchemaMixin, Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String)
    permissions = relationship("Permission", secondary="role_permissions", back_populates="role")


class RolePermissions(models.UUIDSchemaMixin, Base):
    __tablename__ = "role_permissions"
    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))
    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"))

    __table_args__ = (UniqueConstraint(role_id, permission_id, name="unique_together_role_id_permission_id"),)
