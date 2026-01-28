from typing import List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

# Import warunkowy zapobiega Circular Import przy definiowaniu typów
if TYPE_CHECKING:
    from .rate import ExchangeRate

class Currency(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True, max_length=3)
    name: str
    rates: List["ExchangeRate"] = Relationship(back_populates="currency")