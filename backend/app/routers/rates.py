# backend/app/routers/rates.py
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.rate import ExchangeRate
from app.models.currency import Currency
from app.schemas.rate import RateRead

router = APIRouter(prefix="/rates", tags=["Rates"])

@router.get("/{currency_code}/{date_from}/{date_to}", response_model=List[RateRead])
async def get_historical_rates(
    currency_code: str,
    date_from: date,
    date_to: date,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve historical exchange rates for a specific currency and date range.
    Uses SQL JOIN to filter by currency code and maps the result to RateRead schema.
    """
    if date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date."
        )

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
    rates = result.mappings().all()

    if not rates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No rates found for {currency_code.upper()} in the specified range."
        )

    return rates