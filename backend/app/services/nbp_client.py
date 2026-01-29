import httpx
import logging
import asyncio
from datetime import date, timedelta
from typing import List, Optional
from app.schemas.nbp import NBPTable

# Configure logger
logger = logging.getLogger(__name__)

class NBPClient:
    """
    Async client for NBP Web API (https://api.nbp.pl).
    Handles rate limits, sliding window requests, and error mapping.
    """
    BASE_URL = "http://api.nbp.pl/api/exchangerates/tables/a/"
    MAX_DAYS_WINDOW = 90  # Safe margin below NBP's 93-day limit

    async def fetch_rates(self, start_date: date, end_date: date) -> List[NBPTable]:
        """
        Public method to fetch rates for any date range.
        Automatically handles the 93-day limit by splitting requests.
        """
        all_tables: List[NBPTable] = []
        current_start = start_date

        async with httpx.AsyncClient(timeout=10.0) as client:
            while current_start <= end_date:
                # Calculate window end (max 90 days or requested end_date)
                current_end = min(current_start + timedelta(days=self.MAX_DAYS_WINDOW), end_date)
                
                logger.info(f"Fetching NBP data batch: {current_start} to {current_end}")
                
                batch_tables = await self._fetch_batch(client, current_start, current_end)
                all_tables.extend(batch_tables)

                # Move to next window
                current_start = current_end + timedelta(days=1)

        return all_tables

    async def _fetch_batch(self, client: httpx.AsyncClient, start: date, end: date) -> List[NBPTable]:
        """
        Internal method to fetch a single valid time window with retry logic.
        """
        url = f"{self.BASE_URL}{start.isoformat()}/{end.isoformat()}/"
        retries = 3
        
        for attempt in range(retries):
            try:
                response = await client.get(url, headers={"Accept": "application/json"})

                # Handle 404 (No data/Holiday) gracefully
                if response.status_code == 404:
                    logger.warning(f"No data found for range {start} - {end} (likely holidays). NBP 404.")
                    return []

                # Handle Rate Limits
                if response.status_code == 429:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limit hit (429). Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue

                # Raise for other 4xx/5xx errors
                response.raise_for_status()

                # Parse and Validate
                data = response.json()
                return [NBPTable(**item) for item in data]

            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500:
                    logger.error(f"NBP Server Error {e.response.status_code}. Attempt {attempt+1}/{retries}")
                else:
                    # Critical client errors (e.g., 400 Bad Request) - do not retry
                    logger.error(f"Critical API Error: {e}")
                    raise e
            except httpx.RequestError as e:
                logger.error(f"Network Error: {e}. Attempt {attempt+1}/{retries}")

            # Wait before retry if not last attempt
            if attempt < retries - 1:
                await asyncio.sleep(1)

        # If we exhausted retries
        logger.error(f"Failed to fetch data after {retries} attempts for range {start}-{end}")
        raise RuntimeError("NBP API unavailable")