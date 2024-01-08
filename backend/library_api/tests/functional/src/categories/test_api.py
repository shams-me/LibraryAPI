from http import HTTPStatus


import pytest
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession


from src.categories.models import Category

from src.categories.repository import PostgresCategoryRepository


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


async def test_get_category(
    client: AsyncClient,
    test_category: Category,
    mock_jwt_token: str,
):
    response = await client.get(
        f"/categories/{test_category.id}",
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["id"] == str(test_category.id)
    assert data["name"] == test_category.name


async def test_get_all_categories(
    client: AsyncClient,
    test_category: Category,
    mock_jwt_token: str,
):
    response = await client.get(
        "/categories",
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(cat["id"] == str(test_category.id) for cat in data)


async def test_update_category(
    client: AsyncClient,
    test_category: Category,
    mock_jwt_token: str,
):
    updated_data = {
        "name": "Updated Category",
        "description": "Updated category description",
    }
    response = await client.put(
        f"/categories/{test_category.id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["id"] == str(test_category.id)
    assert data["name"] == updated_data["name"]
    assert data["description"] == updated_data["description"]


async def test_delete_category(
    client: AsyncClient,
    test_category: Category,
    mock_jwt_token: str,
):
    delete_response = await client.delete(
        f"/categories/{test_category.id}",
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    assert delete_response.status_code == HTTPStatus.NO_CONTENT

    get_response = await client.get(
        f"/categories/{test_category.id}",
        headers={"Authorization": f"Bearer {mock_jwt_token}"},
    )
    assert get_response.status_code == HTTPStatus.NOT_FOUND
