from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

def create_fastapi_app():
    app = FastAPI(title="MNU")

    app.add_middleware(
        CORSMiddleware,
        allow_origin=["*"]
    )

    main_api_router = APIRouter()


    app.include_router(main_api_router)

    return app


app = create_fastapi_app()


if __name__ == '__main__':
    uvicorn.run(
        app="main:app",
        reload=True
    )