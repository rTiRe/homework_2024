import pytest
from httpx import AsyncClient
from fastapi import status
from conftest import assert_content


@pytest.mark.asyncio(scope="session")
async def test_root(
    async_client: AsyncClient,
    test_status_code: int = status.HTTP_200_OK,
    test_content_type: str = 'text/html; charset=utf-8',
    test_content: list | None = None,
) -> None:
    response = await async_client.get('/')
    assert response.status_code == test_status_code
    assert test_content_type == response.headers['content-type']
    if test_content is not None:
        assert_content(response, test_content)
