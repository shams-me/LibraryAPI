import datetime

from sqlalchemy import String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common import models
from src.common.database import Base


class Book(models.UUIDSchemaMixin, models.TimestampSchemaMixin, Base):
    __tablename__ = "books"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String, default="")
    language: Mapped[str] = mapped_column(String(2), default="en")
    isbn: Mapped[str] = mapped_column(String())
    publication_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)

    authors = relationship("Author", secondary="books_authors", back_populates="books")
    categories = relationship("Category", secondary="books_categories", back_populates="books")


class BookAuthors(
    models.UUIDSchemaMixin,
    models.TimestampSchemaMixin,
    Base,
):
    __tablename__ = "books_authors"

    book_id: Mapped[UUID] = mapped_column(
        ForeignKey("books.id", name="books_authors_book_id_fkey", ondelete="CASCADE"), primary_key=True
    )

    author_id: Mapped[UUID] = mapped_column(
        ForeignKey("authors.id", name="books_authors_author_id_fkey", ondelete="CASCADE"), primary_key=True
    )

    __table_args__ = UniqueConstraint(book_id, author_id, name="unique_book_id_author_id")


class BookCategory(
    models.UUIDSchemaMixin,
    models.TimestampSchemaMixin,
    Base,
):
    __tablename__ = "books_categories"

    book_id: Mapped[UUID] = mapped_column(
        ForeignKey("books.id", name="books_authors_book_id_fkey", ondelete="CASCADE"), primary_key=True
    )

    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id", name="books_categories_category_id_fkey", ondelete="CASCADE"),
        primary_key=True,
    )

    __table_args__ = UniqueConstraint(book_id, category_id, name="unique_book_id_category_id")
