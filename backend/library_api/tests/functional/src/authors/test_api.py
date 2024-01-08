from http import HTTPStatus

import pytest
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession


from src.authors.models import Author

from src.authors.repository import PostgresAuthorRepository


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


async def test_get_author(
    client: AsyncClient,
    test_author: Author,
    mock_jwt_token: str,
):
    response = await client.get(
        f"/authors/{test_author.id}",
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    assert data["id"] == str(test_author.id)
    assert data["name"] == test_author.name


async def test_get_all_authors(
    client: AsyncClient,
    test_author: Author,
    mock_jwt_token: str,
):
    response = await client.get(
        "/authors",
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(cat["id"] == str(test_author.id) for cat in data["items"])


async def test_update_author(
    client: AsyncClient,
    test_author: Author,
    mock_jwt_token: str,
):
    updated_data = {
        "name": "Updated Author",
        "last_name": "Updated author last_name",
    }
    response = await client.put(
        f"/authors/{test_author.id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["id"] == str(test_author.id)
    assert data["name"] == updated_data["name"]
    assert data["last_name"] == updated_data["last_name"]


async def test_delete_author(
    client: AsyncClient,
    test_author: Author,
    mock_jwt_token: str,
):
    delete_response = await client.delete(
        f"/authors/{test_author.id}",
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    assert delete_response.status_code == HTTPStatus.NO_CONTENT

    get_response = await client.get(
        f"/authors/{test_author.id}",
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    assert get_response.status_code == HTTPStatus.NOT_FOUND
