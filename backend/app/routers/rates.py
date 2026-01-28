from fastapi import APIRouter

router = APIRouter(prefix="/rates", tags=["Rates"])

@router.get("/{currency}/{date_from}/{date_to}")
async def get_historical_rates(currency: str, date_from: str, date_to: str):
    return {"message": f"Rates for {currency} from {date_from} to {date_to}"}