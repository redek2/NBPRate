from decimal import Decimal
from datetime import date
from typing import List
from pydantic import BaseModel, Field

class NBPRate(BaseModel):

    # Represents a single currency rate entry from the NBP API.
    currency: str
    code: str
    mid: Decimal

class NBPTable(BaseModel):

    # Represents a full exchange rate table (Type A) for a specific date.
    table: str
    no: str
    effective_date: date = Field(alias="effectiveDate")
    rates: List[NBPRate]