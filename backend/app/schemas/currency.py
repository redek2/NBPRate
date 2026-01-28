from sqlmodel import SQLModel

class CurrencyRead(SQLModel):
    id: int
    code: str
    name: str