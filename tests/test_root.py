"""Root view tests."""

import pytest
from conftest import assert_content
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio(scope='session')
async def test_root(
    async_client: AsyncClient,
    test_status_code: int = status.HTTP_200_OK,
    test_content_type: str = 'text/html; charset=utf-8',
    test_content: list | None = None,
) -> None:
    """Index page render test.

    Args:
        async_client: AsyncClient - client
        test_status_code: int, optional - status code for check. Defaults to status.HTTP_200_OK.
        test_content_type: str, optional - content type check. Defaults 'text/html; charset=utf-8'.
        test_content: list | None, optional - content parts for check. Defaults to None.
    """
    response = await async_client.get('/')
    assert response.status_code == test_status_code
    assert test_content_type == response.headers['content-type']
    if test_content is not None:
        assert_content(response, test_content)
