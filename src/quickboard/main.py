from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from .api import router as api_router
from .db import init_db
from .schemas import ErrorResponse
from .settings import Settings
from .web import router as web_router

settings = Settings()


def create_app(database_url: str | None = None) -> FastAPI:
    if database_url is not None:
        from .db import configure_engine

        configure_engine(database_url)
    init_db()
    app = FastAPI(title=settings.app_name, version=settings.version)

    @app.exception_handler(RequestValidationError)
    def validation_exception_handler(request, exc: RequestValidationError):
        """Return structured JSON for request validation errors."""
        errors = []
        for err in exc.errors():
            loc = ".".join(str(x) for x in err.get("loc", []))
            errors.append({"field": loc, "message": err.get("msg", ""), "type": err.get("type", "")})
        return _validation_error_response(422, errors)

    @app.exception_handler(Exception)
    def generic_exception_handler(request, exc: Exception):
        """Catch-all for unhandled exceptions — return structured JSON."""
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    app.include_router(api_router)
    app.include_router(web_router)
    return app


def _validation_error_response(status_code: int, errors: list[dict]) -> "JSONResponse":
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=status_code,
        content={"detail": "Validation error", "errors": errors},
    )


app = create_app()