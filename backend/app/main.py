from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import text
from app.database import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    try:
        async with engine.begin() as conn:
            # Proste zapytanie sprawdzające czy baza żyje
            await conn.execute(text("SELECT 1"))
        print("✅ Połączenie z bazą danych nawiązane!")
    except Exception as e:
        print(f"❌ Błąd połączenia z bazą: {e}")
        # W produkcji tutaj moglibyśmy rzucić wyjątek, aby kontener się zrestartował
    
    yield
    # --- Shutdown ---
    await engine.dispose()

app = FastAPI(title="NBPRate API", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello NBPRate"}