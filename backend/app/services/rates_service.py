# backend/app/services/rates_service.py
from datetime import date
from typing import List, Optional, Dict, Any

from sqlalchemy.dialects.postgresql import insert
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.currency import Currency
from app.models.rate import ExchangeRate
from app.schemas.nbp import NBPTable
from app.services.nbp_client import NBPClient


class RatesService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.client = NBPClient()

    async def fetch_and_sync(self, start_date: date, end_date: date) -> int:
        tables: List[NBPTable] = await self.client.fetch_rates(start_date, end_date)
        
        if not tables:
            return 0

        await self._upsert_currencies(tables)

        await self._upsert_rates(tables)

        await self.session.commit()
        return len(tables)

    async def get_last_ingested_date(self) -> Optional[date]:
        statement = select(func.max(ExchangeRate.date))
        result = await self.session.execute(statement)
        return result.scalar()

    async def _upsert_currencies(self, tables: List[NBPTable]) -> None:
        unique_currencies: Dict[str, str] = {}
        for table in tables:
            for rate in table.rates:
                if rate.code not in unique_currencies:
                    unique_currencies[rate.code] = rate.currency

        if not unique_currencies:
            return

        values = [{"code": code, "name": name} for code, name in unique_currencies.items()]
        stmt = insert(Currency).values(values)
        stmt = stmt.on_conflict_do_nothing(index_elements=["code"])
        await self.session.execute(stmt)

    async def _upsert_rates(self, tables: List[NBPTable]) -> None:
        # A. Pobieramy mapę {kod_waluty: id_waluty} z bazy
        # Musimy to zrobić, bo upsert_currencies mógł dodać nowe ID
        all_codes = {rate.code for table in tables for rate in table.rates}
        
        statement = select(Currency.code, Currency.id).where(Currency.code.in_(all_codes))
        result = await self.session.execute(statement)
        # Tworzymy słownik np. {'USD': 1, 'EUR': 2}
        currency_map = {row[0]: row[1] for row in result.all()}

        # B. Budujemy payload używając currency_id
        rates_payload: List[Dict[str, Any]] = []

        for table in tables:
            for rate in table.rates:
                if rate.code in currency_map:
                    rates_payload.append({
                        "date": table.effective_date,
                        "value": rate.mid,
                        "currency_id": currency_map[rate.code]  # <--- Używamy ID zamiast kodu
                    })

        if not rates_payload:
            return

        # C. Insert z konfliktem na (date, currency_id)
        stmt = insert(ExchangeRate).values(rates_payload)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=["date", "currency_id"]  # <--- Zgodnie z modelem
        )
        await self.session.execute(stmt)