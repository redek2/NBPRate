import pytest
import respx
from httpx import Response
from datetime import date
from app.services.nbp_client import NBPClient

# Mock URL pattern for NBP API
NBP_URL_PATTERN = "http://api.nbp.pl/api/exchangerates/tables/a/*"

@pytest.mark.asyncio
async def test_fetch_rates_chunks_requests():
    """
    Scenario: User requests data for > 93 days (e.g., 100 days).
    Expected: Client should split this into 2 requests (90 + 10 days).
    """
    client = NBPClient()
    start_date = date(2023, 1, 1)
    end_date = date(2023, 4, 11) # 100 days total

    # Mock NBP response
    mock_response_data = [{
        "table": "A", "no": "001/A/NBP/2023", "effectiveDate": "2023-01-02",
        "rates": [{"currency": "USD", "code": "USD", "mid": 4.0}]
    }]

    async with respx.mock(base_url="http://api.nbp.pl") as respx_mock:
        # We expect calls matching the pattern
        route = respx_mock.get(url__regex=r"/api/exchangerates/tables/a/.*").mock(
            return_value=Response(200, json=mock_response_data)
        )

        results = await client.fetch_rates(start_date, end_date)

        # Assertions
        assert len(results) == 2  # 2 chunks * 1 item per mock response
        assert route.call_count == 2 # Verify 2 HTTP requests were made

@pytest.mark.asyncio
async def test_fetch_rates_handles_404():
    """
    Scenario: NBP returns 404 (e.g., weekend/holiday).
    Expected: Client returns empty list, does not crash.
    """
    client = NBPClient()
    start = date(2023, 1, 1)
    end = date(2023, 1, 2)

    async with respx.mock(base_url="http://api.nbp.pl") as respx_mock:
        respx_mock.get(url__regex=r".*").mock(return_value=Response(404))

        results = await client.fetch_rates(start, end)
        
        assert results == []

@pytest.mark.asyncio
async def test_fetch_rates_retry_logic():
    """
    Scenario: NBP fails with 500 first, then succeeds.
    Expected: Client retries and eventually returns data.
    """
    client = NBPClient()
    start = date(2023, 1, 1)
    end = date(2023, 1, 2)

    mock_data = [{
        "table": "A", "no": "001", "effectiveDate": "2023-01-01",
        "rates": []
    }]

    async with respx.mock(base_url="http://api.nbp.pl") as respx_mock:
        # First call: 500 Error
        route = respx_mock.get(url__regex=r".*").mock(side_effect=[
            Response(500),
            Response(200, json=mock_data)
        ])

        results = await client.fetch_rates(start, end)
        
        assert len(results) == 1
        assert route.call_count == 2 # 1 fail + 1 success