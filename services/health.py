from fastapi import FastAPI, APIRouter

health_router = APIRouter()

@health_router.get("/ping")
async def ping() -> dict:
    return {"success": True}

