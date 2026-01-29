import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import engine, get_session
from app.main import app

# 1. FIX: Reset Engine
# Czyści połączenia bazy danych przed i po każdym teście.
# Zapobiega błędowi "attached to a different loop".
@pytest_asyncio.fixture(autouse=True)
async def reset_engine():
    await engine.dispose()
    yield
    await engine.dispose()

# 2. Session Fixture
# Tworzy sesję wewnątrz transakcji. Po teście robi ROLLBACK,
# dzięki czemu baza pozostaje czysta (nie zostają w niej śmieci testowe).
@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    connection = await engine.connect()
    transaction = await connection.begin()
    
    session_factory = sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with session_factory() as session:
        yield session
        
    await transaction.rollback()
    await connection.close()

# 3. Client Fixture
# Nadpisuje (override) "get_session" w aplikacji.
# Dzięki temu endpointy API używają tej samej sesji co testy!
@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_session] = lambda: db_session
    
    # ASGITransport pozwala testować aplikację bez stawiania serwera sieciowego
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
        
    app.dependency_overrides.clear()