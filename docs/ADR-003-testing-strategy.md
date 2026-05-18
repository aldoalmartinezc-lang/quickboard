# ADR-003: Testing Strategy

## Estado
Aceptado

## Contexto
QuickBoard debe llegar al MVP con endpoints CRUD funcionales, SQLite local, UI mínima y CI verde. Para un equipo de una sola persona, el objetivo principal de los tests es bloquear regresiones reales en la API y la persistencia.

## Decisión
Priorizar tests de integración con `pytest` y cliente HTTP asíncrono de `httpx` contra una base SQLite aislada por test o por sesión de test.

Cobertura esperada:
- CRUD de boards, lists y cards.
- Movimiento de cards entre listas.
- Completar y eliminar cards.
- Asignación y lectura de tags.
- Búsqueda por texto.
- Health endpoint.
- UI mínima responde y referencia la API.

Los tests unitarios se reservarán para helpers puros si aparecen, pero no serán la estrategia principal.

## Consecuencias
- Se verifica el comportamiento real del sistema completo, no solo funciones aisladas.
- Se reduce el riesgo de mocks que oculten fallos de integración entre FastAPI, SQLModel y SQLite.
- Los tests son un poco más lentos que un set puramente unitario, pero siguen siendo suficientemente rápidos para CI y desarrollo local.
- El diseño incentiva implementación sencilla y observable.

## Alternativas consideradas
- **Unit tests + mocks**: más rápidos para lógica aislada, pero dejan sin validar la interacción real con la base y la API.
- **Solo unit tests**: insuficientes para un MVP API-first.
- **E2E únicamente**: demasiado frágil y lento para la base de regresión diaria.

## Confianza
media-alta
