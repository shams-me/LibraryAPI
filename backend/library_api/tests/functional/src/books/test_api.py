from http import HTTPStatus

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.authors.models import Author
from src.authors.repository import PostgresAuthorRepository
from src.books.models import Book
from src.books.repository import PostgresBookRepository
from src.categories.models import Category
from src.categories.repository import PostgresCategoryRepository


@pytest.fixture
async def test_book(
    db_session: AsyncSession,
) -> Book:
    repo = PostgresBookRepository(db_session)
    book_data = {
        "title": "Test Book",
        "description": "Test Description",
        "isbn": "21312312312313",
    }
    return await repo.insert(**book_data)


@pytest.fixture
async def test_author(
    db_session: AsyncSession,
) -> Author:
    repo = PostgresAuthorRepository(db_session)
    author_name = "test_author"
    last_name = "last name"
    return await repo.insert(
        name=author_name,
        last_name=last_name,
    )


@pytest.fixture
async def test_category(
    db_session: AsyncSession,
) -> Category:
    repo = PostgresCategoryRepository(db_session)
    category_name = "test_category"
    category_description = "A test category"
    return await repo.insert(
        name=category_name,
        description=category_description,
    )


async def test_create_book(
    client: AsyncClient,
    mock_jwt_token: str,
):
    book_data = {
        "title": "New Book",
        "description": "New book description",
        "isbn": "21312312312313",
    }
    response = await client.post(
        "/books",
        json=book_data,
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["title"] == book_data["title"]
    assert data["description"] == book_data["description"]


async def test_get_all_books(
    client: AsyncClient,
    test_book: Book,
    mock_jwt_token: str,
):
    response = await client.get(
        "/books",
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["total"] >= 1
    assert any(book["id"] == str(test_book.id) for book in data["items"])


async def test_get_book(
    client: AsyncClient,
    test_book: Book,
    mock_jwt_token: str,
):
    response = await client.get(
        f"/books/{test_book.id}",
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["id"] == str(test_book.id)
    assert data["title"] == test_book.title


async def test_update_book(
    client: AsyncClient,
    test_book: Book,
    mock_jwt_token: str,
):
    updated_data = {
        "title": "Updated Book",
        "description": "Updated description",
    }
    response = await client.put(
        f"/books/{test_book.id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["id"] == str(test_book.id)
    assert data["title"] == updated_data["title"]
    assert data["description"] == updated_data["description"]


async def test_delete_book(
    client: AsyncClient,
    test_book: Book,
    mock_jwt_token: str,
):
    delete_response = await client.delete(
        f"/books/{test_book.id}",
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    assert delete_response.status_code == HTTPStatus.NO_CONTENT

    get_response = await client.get(
        f"/books/{test_book.id}",
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    assert get_response.status_code == HTTPStatus.NOT_FOUND


async def test_add_author_to_book(
    client: AsyncClient,
    test_book: Book,
    test_author: Author,
    mock_jwt_token: str,
):
    response = await client.post(
        f"/books/{test_book.id}/author",
        params={"author_id": str(test_author.id)},
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    assert response.status_code == HTTPStatus.CREATED

    # Fetch the book and check if the author was added
    book_response = await client.get(
        f"/books/{test_book.id}",
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    book_data = book_response.json()
    assert any(author["id"] == str(test_author.id) for author in book_data["authors"])


async def test_remove_author_from_book(
    client: AsyncClient,
    test_book: Book,
    test_author: Author,
    mock_jwt_token: str,
):
    # Add the author to the book first
    await client.post(
        f"/books/{test_book.id}/author",
        params={"author_id": str(test_author.id)},
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )

    # Now remove the author
    delete_response = await client.delete(
        f"/books/{test_book.id}/author",
        params={"author_id": str(test_author.id)},
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    assert delete_response.status_code == HTTPStatus.NO_CONTENT

    # Fetch the book and check if the author was removed
    book_response = await client.get(
        f"/books/{test_book.id}",
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    book_data = book_response.json()
    assert all(author["id"] != str(test_author.id) for author in book_data["authors"])
