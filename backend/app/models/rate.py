from datetime import date as dt_date
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint

if TYPE_CHECKING:
    from .currency import Currency

class ExchangeRate(SQLModel, table=True):
    __tablename__ = "exchange_rate"

    __table_args__ = (
        UniqueConstraint("date", "currency_id", name="unique_date_currency"),
    )

    id: int | None = Field(default=None, primary_key=True)
    date: dt_date = Field(index=True)
    value: Decimal = Field(default=0, max_digits=10, decimal_places=4)
    currency_id: int = Field(foreign_key="currency.id")
    currency: "Currency" = Relationship(back_populates="rates")