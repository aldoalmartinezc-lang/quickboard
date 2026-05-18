# QuickBoard Product Brief

## Problema que resuelve
QuickBoard resuelve la necesidad de llevar un tablero kanban personal sin depender de herramientas externas, cuentas obligatorias o servicios centralizados. Está pensado para desarrolladores que quieren registrar y mover su trabajo desde la terminal o cualquier cliente HTTP, con una experiencia mínima, local y predecible.

## Personas y casos de uso
1. **Desarrollador individual**: quiere organizar tareas personales en un tablero simple y consultarlo desde la terminal.
2. **Usuario técnico con scripts**: quiere automatizar altas, movimientos y búsquedas de cards mediante requests HTTP.
3. **Usuario que prefiere una UI mínima**: quiere ver y operar el tablero en una página web simple servida por el propio servidor.

## User stories
- Como desarrollador individual quiero crear tableros para separar contextos de trabajo para organizar mis tareas personales.
- Como desarrollador individual quiero listar, renombrar y eliminar tableros para mantener mis espacios de trabajo actualizados.
- Como usuario de un tablero quiero crear listas dentro de un tablero para representar estados como Todo, Doing y Done.
- Como usuario de un tablero quiero crear cards dentro de listas para registrar tareas concretas.
- Como usuario de un tablero quiero mover cards entre listas para reflejar su progreso.
- Como usuario de un tablero quiero completar cards para marcar trabajo terminado.
- Como usuario de un tablero quiero eliminar cards para limpiar elementos obsoletos.
- Como usuario de un tablero quiero asignar etiquetas libres a las cards para clasificar y filtrar el trabajo.
- Como usuario de un tablero quiero buscar cards por texto en título o descripción para encontrar trabajo rápidamente.
- Como usuario de un tablero quiero usar una interfaz web mínima servida por el mismo servidor para operar sin depender de herramientas externas.
- Como usuario de un tablero quiero consultar el estado del servicio en un endpoint de health para verificar que la API está viva y conocer su versión.

## Límites explícitos del MVP
- No incluye autenticación ni cuentas de usuario, porque el producto está definido para una sola instancia personal y sin fricción.
- No incluye sincronización multiusuario ni colaboración en tiempo real, porque el alcance se limita a uso individual.
- No incluye base de datos externa ni servicios gestionados, porque el MVP debe funcionar con SQLite local.
- No incluye permisos, roles, auditoría ni activity feed, porque no son necesarios para el uso personal inicial.
- No incluye notificaciones, recordatorios ni automatizaciones, porque el foco es CRUD y búsqueda.
- No incluye vistas complejas, arrastrar-y-soltar ni personalización avanzada de UI, porque la interfaz web debe ser ultra-simple.
- No incluye adjuntos, comentarios, subtareas, fechas límite ni estimaciones, porque complican el modelo sin validar el core value.

## Métricas de éxito del MVP
- Todos los endpoints definidos para boards, lists, cards, tags, search y health responden correctamente con tests de integración verdes.
- `pytest` pasa sin fallos en el repositorio.
- `ruff check .` pasa sin errores.
- `docker compose up` levanta el servicio localmente y `GET /health` responde con `200`.
- La interfaz web en `/` carga y permite operar contra la API sin errores de consola bloqueantes.
- El repo público contiene CI verde en GitHub Actions para test y lint.

## Supuestos técnicos asumidos
- La aplicación corre como una sola instancia local sobre FastAPI y SQLite.
- SQLModel se usa como capa ORM ligera sobre SQLite.
- La API puede exponer rutas REST simples y predecibles sin requerir un framework adicional.
- La UI web mínima puede estar implementada con HTML y JavaScript embebido servido por FastAPI.
- El MVP puede usar migraciones simples o inicialización automática del esquema al arrancar.
- La prioridad es trazabilidad y simplicidad operativa, no extensibilidad a gran escala.
