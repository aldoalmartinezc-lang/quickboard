from fastapi import FastAPI

from .api import router as api_router
from .db import init_db
from .settings import Settings
from .web import router as web_router

settings = Settings()


def create_app(database_url: str | None = None) -> FastAPI:
    if database_url is not None:
        from .db import configure_engine

        configure_engine(database_url)
    init_db()
    app = FastAPI(title=settings.app_name, version=settings.version)
    app.include_router(api_router)
    app.include_router(web_router)
    return app


app = create_app()
