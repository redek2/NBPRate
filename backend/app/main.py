import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlmodel import text
from app.database import engine
from app.routers import currencies, rates

# 1. Central Logging Configuration
# Ensures consistent log format across all modules (services, routers)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.
    Checks database connectivity on startup.
    """
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully.")
    except Exception as e:
        logger.critical(f"Database connection failed: {e}")
        # In a real scenario, we might want to stop the app here
    
    yield
    
    await engine.dispose()
    logger.info("Database connection closed.")

app = FastAPI(title="NBPRate API", lifespan=lifespan)

# 2. Global Exception Handler
# Catches any unhandled exceptions to prevent stack traces from leaking to the client.
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the full stack trace internally for debugging
    logger.error(f"Global Exception: {exc}", exc_info=True)
    
    # Return a safe, generic error message to the client
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Please contact support."}
    )

# 3. Router Registration
app.include_router(currencies.router)
app.include_router(rates.router)

@app.get("/")
async def root():
    return {"message": "Hello NBPRate API"}