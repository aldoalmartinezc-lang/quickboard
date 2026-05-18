# QuickBoard Dependency Map

## Capas
- `settings.py`: configuración base de la app.
- `db.py`: crea el engine y abre sesiones de SQLite.
- `models.py`: define el esquema persistente con SQLModel.
- `schemas.py`: define los payloads de entrada y salida.
- `crud.py`: encapsula acceso a datos.
- `services.py`: contiene reglas de negocio.
- `api.py`: monta routers y expone endpoints REST.
- `web.py`: sirve la UI HTML/JS mínima.
- `main.py`: crea la instancia FastAPI y registra la app.

## Grafo de dependencias
- `main.py` -> `settings.py`, `api.py`, `web.py`, `db.py`
- `api.py` -> `crud.py`, `schemas.py`, `services.py`
- `web.py` -> `api.py` o fetch directo contra la API
- `services.py` -> `crud.py`, `models.py`, `schemas.py`
- `crud.py` -> `db.py`, `models.py`
- `db.py` -> `settings.py`, `models.py`
- `schemas.py` -> sin dependencias de runtime
- `models.py` -> sin dependencias internas de la app

## Dependencias transversales
- `tests/` -> `main.py`, `db.py`, `models.py`, `schemas.py`, `services.py`, `api.py`
- `Dockerfile` / `docker-compose.yml` -> `main.py`, `pyproject.toml`
- `.github/workflows/ci.yml` -> `pyproject.toml`, `tests/`
- `Procfile` / `railway.json` -> `main.py`

## Orden recomendado de implementación
1. `models.py`
2. `schemas.py`
3. `db.py`
4. `crud.py`
5. `services.py`
6. `api.py`
7. `web.py`
8. `main.py`
9. `tests/`
10. `CI` / `Docker` / `deploy`
