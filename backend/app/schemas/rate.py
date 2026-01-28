from datetime import date
from decimal import Decimal
from sqlmodel import SQLModel

class ExchangeRateRead(SQLModel):
    id: int
    date: date
    value: Decimal
    currency_id: int