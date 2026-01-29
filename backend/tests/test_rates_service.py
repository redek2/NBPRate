import pytest
import respx
from httpx import Response
from datetime import date
from sqlmodel import select, func

from app.services.rates_service import RatesService
from app.models.rate import ExchangeRate
from app.models.currency import Currency

@pytest.mark.asyncio
async def test_fetch_and_sync_integration(db_session):
    """
    Testuje pełny przepływ: Pobranie (Mock) -> Transformacja -> Zapis do DB (Real).
    Sprawdza, czy dane faktycznie lądują w bazie.
    """
    service = RatesService(db_session)
    start = date(2025, 1, 1)
    end = date(2025, 1, 2)

    # 1. Mockujemy odpowiedź NBP
    mock_data = [{
        "table": "A", "no": "001/A/NBP/2025", "effectiveDate": "2025-01-01",
        "rates": [{"currency": "Test Dollar", "code": "TST", "mid": 3.50}]
    }]
    
    async with respx.mock(base_url="http://api.nbp.pl") as respx_mock:
        respx_mock.get(url__regex=r".*").mock(return_value=Response(200, json=mock_data))

        # 2. Uruchamiamy serwis
        processed = await service.fetch_and_sync(start, end)

    # 3. Weryfikacja (Assertions)
    assert processed == 1, "Powinien przetworzyć 1 tabelę"

    # Sprawdzamy czy waluta trafiła do bazy
    curr_stmt = select(Currency).where(Currency.code == "TST")
    currency = (await db_session.execute(curr_stmt)).scalar_one_or_none()
    assert currency is not None
    assert currency.name == "Test Dollar"

    # Sprawdzamy czy kurs trafił do bazy
    rate_stmt = select(ExchangeRate).join(Currency).where(Currency.code == "TST")
    rate = (await db_session.execute(rate_stmt)).scalar_one_or_none()
    assert rate is not None
    assert rate.value == 3.50