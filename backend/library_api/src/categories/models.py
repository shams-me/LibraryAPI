from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common import models
from src.common.database import Base


class Category(models.UUIDSchemaMixin, models.TimestampSchemaMixin, Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String, default="")

    books = relationship("Book", secondary="books_categories", back_populates="categories")
