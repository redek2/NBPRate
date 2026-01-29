# backend/app/schemas/rate.py
from datetime import date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator

class RateRead(BaseModel):
    """
    Schema for reading exchange rates (Output).
    """
    date: date
    value: Decimal
    currency_code: str

class FetchRatesRequest(BaseModel):
    """
    Schema for triggering data synchronization (Input).
    """
    start_date: date
    end_date: date
    currency_codes: Optional[List[str]] = Field(
        default=None, 
        description="List of currency codes to filter (e.g. ['USD', 'EUR']). Currently fetches all due to NBP Table A strategy."
    )

    @model_validator(mode='after')
    def check_date_range(self) -> 'FetchRatesRequest':
        if self.start_date > self.end_date:
            raise ValueError('Start date cannot be after end date')
        return self

class FetchRatesResponse(BaseModel):
    """
    Schema for synchronization result (Output).
    """
    success: bool
    message: str
    days_processed: int