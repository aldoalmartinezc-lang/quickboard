set dotenv-load := false

venv := ".venv"
python := venv + "/bin/python"
pytest := venv + "/bin/pytest"
ruff := venv + "/bin/ruff"
uvicorn := venv + "/bin/uvicorn"

# Muestra esta ayuda
default:
    @just --list

# Instala dependencias de desarrollo
install:
    uv pip install -e '.[dev]' --python {{python}}

# Ejecuta todos los tests
test:
    {{pytest}} -q

# Ejecuta tests con verbose y para al primer fallo
test-x:
    {{pytest}} -x -v

# Lint con ruff
lint:
    {{ruff}} check .

# Formatea y corrige lo que pueda ruff
fix:
    {{ruff}} check --fix .
    {{ruff}} format .

# Levanta el servidor en modo recarga
dev:
    {{uvicorn}} quickboard.main:app --reload

# Corre lint + tests (CI local)
ci: lint test
