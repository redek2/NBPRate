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
    Retrieve historical exchange rates with Smart Gap Detection.
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
        result = await session.execute(statement)
        return result.mappings().all()

    # 1. Pierwsza próba odczytu
    rates = await fetch_from_db()

    # 2. Analiza czy musimy dociągnąć dane (Smart Gap Detection)
    should_fetch_nbp = False

    if not rates:
        # Przypadek 1: Baza jest pusta dla tego zakresu
        should_fetch_nbp = True
    else:
        # Przypadek 2: Mamy "jakieś" dane, ale sprawdzamy czy nie są dziurawe
        # Sprawdzamy granice. Jeśli pierwszy znaleziony dzień jest dużo później niż date_from
        # LUB ostatni znaleziony dzień jest dużo wcześniej niż date_to, to znaczy że brakuje danych.
        # Dajemy 7 dni marginesu na weekendy/święta.
        
        first_db_date = rates[0]['date']
        last_db_date = rates[-1]['date']
        
        margin = timedelta(days=7) # Bezpieczny margines (święta + weekendy)

        # Czy brakuje początku?
        if first_db_date > (date_from + margin):
            should_fetch_nbp = True
        
        # Czy brakuje końca? (Sprawdzamy tylko jeśli date_to nie jest w przyszłości)
        if date_to <= date.today() and last_db_date < (date_to - margin):
            should_fetch_nbp = True

    # 3. Jeśli wykryto braki, pobieramy z NBP
    if should_fetch_nbp:
        service = RatesService(session)
        try:
            # fetch_and_sync używa Twojego nbp_client, który ma już podział na paczki 90-dniowe
            await service.fetch_and_sync(date_from, date_to)
        except Exception as e:
            # Logujemy błąd, ale jeśli w bazie coś było, to ostatecznie to zwrócimy
            # (lepiej zwrócić niepełne dane niż błąd 500)
            print(f"Warning: NBP Sync failed: {e}")
            if not rates:
                 raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Failed to fetch data from NBP: {str(e)}"
                )
        
        # 4. Ponowna próba odczytu z bazy po synchronizacji
        rates = await fetch_from_db()

    # Finalne sprawdzenie
    if not rates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No rates found for {currency_code.upper()}."
        )

    return rates