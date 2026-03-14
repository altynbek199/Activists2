from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api.handlers import user_router, event_router
from api.login_handlers import login_router
from api.actions.chat import sio, Message
from api.chat_handler import chat_router
from contextlib import asynccontextmanager
from pymongo import AsyncMongoClient
from beanie import init_beanie
from socketio import ASGIApp
from settings import settings
import logging
from prometheus_fastapi_instrumentator import Instrumentator
import sentry_sdk
from services.health import health_router

sentry_sdk.init(
    dsn=settings.SENTRY_URL,
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

# Logger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s" 
)

logger = logging.getLogger(__name__)

# Lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = None
    print("Initialization MongoDB...")
    try:

        client = AsyncMongoClient(f"mongodb://{settings.MONGO_ROOT_USER}:{settings.MONGO_ROOT_PASS}@mongodb:27017/{settings.MONGO_DB}?authSource=admin")
        await init_beanie(database=client[settings.MONGO_DB], document_models=[Message])
        yield
    finally:
        print("Close MongoDB...")
        if client:
            await client.close()

# creating fastapi app

def create_fastapi_app():
    app = FastAPI(title="MNU", lifespan=lifespan)

    instrumentator = Instrumentator().instrument(app).expose(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    main_api_router = APIRouter()

    main_api_router.include_router(user_router, prefix="/user", tags=["user"])
    main_api_router.include_router(login_router, prefix="/login", tags=["login"])
    main_api_router.include_router(event_router, prefix="/event", tags=["event"])
    main_api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
    main_api_router.include_router(health_router, prefix="/ping", tags=["ping"])

    app.include_router(main_api_router)

    return app


app_fastapi = create_fastapi_app()

asgi_app = ASGIApp(sio, other_asgi_app=app_fastapi)

if __name__ == '__main__':
    uvicorn.run(
        app="main:asgi_app",
        host="0.0.0.0",
        port=8080,
        )