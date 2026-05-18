# ADR-001: Database Schema

## Estado
Aceptado

## Contexto
QuickBoard necesita persistir boards, lists, cards y tags en SQLite local. El MVP debe permitir crear elementos, mover cards entre listas y mantener un orden explícito dentro de cada lista sin introducir complejidad innecesaria.

## Decisión
Modelar el dominio con estas entidades:
- `Board`: contenedor raíz.
- `List`: pertenece a un `Board` y tiene un campo `position` para ordenar listas dentro del board.
- `Card`: pertenece a una `List`, tiene `title`, `description`, `completed_at` opcional y un campo `position` para ordenar cards dentro de la lista.
- `Tag`: etiqueta de texto libre con unicidad por nombre.
- `CardTag`: tabla de unión many-to-many entre cards y tags.

El orden de lists y cards será por enteros contiguos por defecto, reindexando la lista afectada cuando sea necesario. El movimiento de una card entre listas se hará en una transacción: se actualiza su `list_id`, se recalcula su `position` en el destino y se reordenan las cards afectadas en origen y destino.

## Consecuencias
- El esquema es simple de entender, serializar y testear.
- La reindexación hace que el MVP sea fácil de implementar en SQLite sin trucos de ordenamiento.
- El costo de mover cards es O(n) sobre las listas afectadas, lo cual es aceptable para una instancia personal.
- La unicidad de tags evita duplicados y simplifica búsquedas y asociación.

## Alternativas consideradas
- **Orden por intervalos/floats**: reduce reindexaciones pero complica la lógica de mantenimiento y testeo para el MVP.
- **Lista encadenada**: evita reordenar pero dificulta consultas y mantenimiento de relaciones.
- **Sin tabla `Tag`**: más simple, pero impide reutilizar etiquetas y buscar por ellas de forma consistente.

## Confianza
media-alta
