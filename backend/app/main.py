from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import text
from app.database import engine
from app.routers import currencies, rates

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("Połączenie z bazą danych nawiązane!")
    except Exception as e:
        print(f"Błąd połączenia z bazą: {e}")
    
    yield
    await engine.dispose()

app = FastAPI(title="NBPRate API", lifespan=lifespan)

app.include_router(currencies.router)
app.include_router(rates.router)

@app.get("/")
async def root():
    return {"message": "Hello NBPRate"}