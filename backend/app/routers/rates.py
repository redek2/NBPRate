from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.rate import ExchangeRate
from app.models.currency import Currency
from app.schemas.rate import RateRead
from app.services.rates_service import RatesService

router = APIRouter(prefix="/rates", tags=["Rates"])

@router.get("/{currency_code}/{date_from}/{date_to}", response_model=List[RateRead])
async def get_historical_rates(
    currency_code: str,
    date_from: date,
    date_to: date,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve historical exchange rates with Advanced Gap Detection.
    """
    if date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date."
        )

    # Funkcja pomocnicza do pobierania z bazy
    async def fetch_from_db():
        statement = (
            select(
                ExchangeRate.date, 
                ExchangeRate.value, 
                Currency.code.label("currency_code")
            )
            .join(Currency)
            .where(Currency.code == currency_code.upper())
            .where(ExchangeRate.date >= date_from)
            .where(ExchangeRate.date <= date_to)
            .order_by(ExchangeRate.date)
        )
        # Używamy session.exec zamiast execute, aby uniknąć DeprecationWarning,
        # ale ponieważ robimy projekcję (wybrane kolumny), SQLModel zwraca Row, 
        # który działa podobnie do krotek. Pydantic obsłuży to poprawnie.
        result = await session.execute(statement)
        return result.mappings().all()

    # 1. Pierwsza próba odczytu
    rates = await fetch_from_db()

    should_fetch_nbp = False

    # 2. Advanced Gap Detection
    if not rates:
        should_fetch_nbp = True
    else:
        first_db_date = rates[0]['date']
        last_db_date = rates[-1]['date']
        margin = timedelta(days=7)

        if first_db_date > (date_from + margin):
            should_fetch_nbp = True
        elif date_to <= date.today() and last_db_date < (date_to - margin):
            should_fetch_nbp = True
        
        if not should_fetch_nbp:
            for i in range(len(rates) - 1):
                current_date = rates[i]['date']
                next_date = rates[i+1]['date']
                delta = next_date - current_date
                
                if delta.days > 4:
                    # Używamy logging zamiast print w produkcji (todo: zamienić na logger)
                    should_fetch_nbp = True
                    break

    # 3. Jeśli wykryto braki, pobieramy z NBP
    if should_fetch_nbp:
        service = RatesService(session)
        try:
            await service.fetch_and_sync(date_from, date_to)
        except Exception as e:
            # Logujemy błąd, ale nie przerywamy, jeśli mamy jakiekolwiek dane w cache
            print(f"Warning: NBP Sync failed: {e}")
        
        # Ponowne pobranie z bazy po synchronizacji
        rates = await fetch_from_db()

    # 4. Finalna weryfikacja i obsługa 404
    if not rates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No rates found for currency {currency_code} in range {date_from} - {date_to}"
        )

    return rates