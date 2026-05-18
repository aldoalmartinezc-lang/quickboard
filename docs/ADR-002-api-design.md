# ADR-002: API Design

## Estado
Aceptado

## Contexto
QuickBoard será consumido desde terminal, clientes HTTP y una UI web mínima. El API debe ser fácil de recordar, consistente y suficientemente expresivo para CRUD, movimiento y búsqueda sin sobrecargar el dominio con rutas demasiado anidadas.

## Decisión
Usar un diseño híbrido:
- Rutas raíz para recursos principales:
  - `GET /boards`, `POST /boards`, `GET /boards/{board_id}`, `PATCH /boards/{board_id}`, `DELETE /boards/{board_id}`
  - `GET /lists/{list_id}`, `PATCH /lists/{list_id}`, `DELETE /lists/{list_id}`
  - `GET /cards/{card_id}`, `PATCH /cards/{card_id}`, `DELETE /cards/{card_id}`
- Rutas anidadas para crear y listar hijos dentro del contexto padre:
  - `GET /boards/{board_id}/lists`
  - `POST /boards/{board_id}/lists`
  - `GET /lists/{list_id}/cards`
  - `POST /lists/{list_id}/cards`
- Acciones específicas:
  - `POST /cards/{card_id}/move`
  - `POST /cards/{card_id}/complete`
  - `PUT /cards/{card_id}/tags`
- Búsqueda:
  - `GET /cards/search?q=...`
- Health:
  - `GET /health`
- UI web:
  - `GET /`

## Consecuencias
- La API mantiene semántica REST clara para recursos principales.
- El cliente puede trabajar con rutas cortas para CRUD directo y rutas anidadas cuando importa el contexto del padre.
- Las acciones no CRUD quedan explícitas en endpoints dedicados, lo que reduce ambigüedad para mover/completar cards.
- El número de rutas aumenta un poco, pero sigue siendo pequeño y predecible para el MVP.

## Alternativas consideradas
- **Solo rutas planas con filtros**: más uniformes, pero menos expresivas para crear hijos dentro de un contexto.
- **Solo rutas anidadas**: muy semánticas, pero verbosas para uso repetido desde terminal.
- **GraphQL**: innecesario para el alcance del MVP.

## Confianza
media
