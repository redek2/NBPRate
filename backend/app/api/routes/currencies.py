from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.currency import Currency
from app.schemas.currency import CurrencyRead

router = APIRouter()

@router.get("/", response_model=list[CurrencyRead])
async def get_currencies(session: AsyncSession = Depends(get_session)):
    """
    Fetch all currencies from the database.
    The response is automatically validated against CurrencyRead schema.
    """
    result = await session.execute(select(Currency))
    currencies = result.scalars().all()
    return currencies