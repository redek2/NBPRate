# backend/app/routers/currencies.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.currency import Currency
from app.schemas.currency import CurrencyRead
from app.schemas.rate import FetchRatesRequest, FetchRatesResponse
from app.services.rates_service import RatesService

router = APIRouter(prefix="/currencies", tags=["Currencies"])

@router.get("/", response_model=List[CurrencyRead])
async def get_currencies(session: AsyncSession = Depends(get_session)):
    """
    Fetch all currencies available in the database.
    Returns a list sorted alphabetically by currency code.
    """
    # Enforce alphabetical sorting for UI consistency
    statement = select(Currency).order_by(Currency.code)
    result = await session.execute(statement)
    return result.scalars().all()

@router.post("/fetch", response_model=FetchRatesResponse, status_code=status.HTTP_200_OK)
async def fetch_currencies(
    request: FetchRatesRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Trigger synchronization of currency rates from NBP API.
    
    - Validates date range.
    - Uses RatesService to fetch and upsert data safely.
    - Handles external API errors gracefully.
    """
    service = RatesService(session)

    try:
        # Delegate business logic to the service layer
        days_synced = await service.fetch_and_sync(request.start_date, request.end_date)
        
        return FetchRatesResponse(
            success=True,
            message=f"Synchronization completed. Processed {days_synced} days of data.",
            days_processed=days_synced
        )

    except ValueError as e:
        # Validation errors (e.g. start_date > end_date)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        # External service failures (NBP API down/timeout)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"External NBP service unavailable: {str(e)}"
        )
    except Exception as e:
        # Unforeseen server errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )