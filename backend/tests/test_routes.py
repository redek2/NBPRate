import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_currencies(client: AsyncClient):
    response = await client.get("/currencies/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_rates_404(client: AsyncClient):
    # Pytamy o walutę, której na pewno nie ma
    response = await client.get("/rates/NONEXISTENT/2025-01-01/2025-01-02")
    assert response.status_code == 404
    assert "No rates found" in response.json()["detail"]