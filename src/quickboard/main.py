from fastapi import FastAPI

from .settings import Settings

settings = Settings()
app = FastAPI(title=settings.app_name, version=settings.version)


@app.get('/health')
def health() -> dict[str, str]:
    return {"status": "ok", "version": settings.version}


@app.get('/')
def root() -> str:
    return "<html><body><h1>QuickBoard</h1></body></html>"
