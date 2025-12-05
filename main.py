from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api.handlers import user_router, event_router
from api.login_handlers import login_router


def create_fastapi_app():
    app = FastAPI(title="MNU")

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

    app.include_router(main_api_router)

    return app


app = create_fastapi_app()


if __name__ == '__main__':
    uvicorn.run(
        app="main:app",
        reload=True
    )