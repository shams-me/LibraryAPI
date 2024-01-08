from sqlalchemy import ForeignKey, String, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common import models
from src.common.database import Base


class User(models.UUIDSchemaMixin, models.TimestampSchemaMixin, Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    membership: Mapped[bool] = mapped_column(Boolean, default=False)

    role = relationship("Role", secondary="user_roles", uselist=False, cascade="all, delete", lazy="selectin")
    permissions = relationship("Permission", secondary="users_permissions", cascade="all, delete")
    user_history = relationship("UserSigninHistory", back_populates="user", cascade="all, delete")

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class UserSigninHistory(models.UUIDSchemaMixin, models.TimestampSchemaMixin, Base):
    __tablename__ = "user_login_history"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user_agent: Mapped[str] = mapped_column(String(255))
    ip_address: Mapped[INET] = mapped_column(INET())

    user: Mapped[User] = relationship(back_populates="user_history")


class UserPermissions(models.UUIDSchemaMixin, models.TimestampSchemaMixin, Base):
    __tablename__ = "users_permissions"

    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permissions.id"), primary_key=True)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    __table_args__ = (UniqueConstraint(permission_id, user_id, name="unique_together_permission_id_user_id"),)


class UserRole(models.UUIDSchemaMixin, models.TimestampSchemaMixin, Base):
    __tablename__ = "user_roles"

    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    __table_args__ =( UniqueConstraint(role_id, user_id, name="unique_together_role_id_user_id"),)
