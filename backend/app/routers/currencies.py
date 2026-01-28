from fastapi import APIRouter

router = APIRouter(prefix="/currencies", tags=["Currencies"])

@router.get("/")
async def list_currencies():
    return {"message": "List of currencies placeholder"}

@router.post("/fetch")
async def fetch_currencies():
    return {"message": "Fetch trigger placeholder"}