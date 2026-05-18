# QuickBoard

QuickBoard es un MVP de kanban personal con:

- Boards: crear, listar, renombrar y eliminar
- Lists: crear dentro de un board, renombrar, mover y eliminar
- Cards: crear, mover entre listas, completar, etiquetar y eliminar
- Search: búsqueda por texto en título o descripción
- Health endpoint en `/health`
- UI mínima servida en `/`

## Stack

- Python 3.11
- FastAPI
- SQLModel + SQLite
- pytest + httpx
- Ruff
- GitHub Actions
- Docker y Railway

## Desarrollo local

```bash
python -m pip install -e '.[dev]'
uvicorn quickboard.main:app --reload
```

Abrir:

- UI: http://127.0.0.1:8000/
- Health: http://127.0.0.1:8000/health

## Tests y lint

```bash
ruff check .
pytest -q
```

## Docker

```bash
docker compose up --build
```

## Variables de entorno

- `QUICKBOARD_DATABASE_URL`: URL de SQLite u otro backend compatible
- `QUICKBOARD_APP_NAME`: nombre visible de la app
- `QUICKBOARD_VERSION`: versión reportada en `/health`

## Release

Versión actual: `0.1.0`
