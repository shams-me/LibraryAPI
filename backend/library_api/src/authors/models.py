from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common import models
from src.common.database import Base


class Author(models.UUIDSchemaMixin, models.TimestampSchemaMixin, Base):
    __tablename__ = "authors"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), default="")
    biography: Mapped[str] = mapped_column(String, default="")

    books = relationship("Book", secondary="books_authors", back_populates="authors")
