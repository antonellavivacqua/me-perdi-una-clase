# Especificación de «Me perdí una clase»

## Problema y usuarios

Cuando un alumno falta, necesita recuperar qué se vio y qué quedó de tarea. Esa información puede estar repartida entre apuntes y mensajes de varios compañeros. La app reúne los resúmenes por curso y fecha, y muestra qué clases siguen esperando un aporte.

La demo representa tres cursos de Computación de una escuela técnica: 4°, 5° y 6°. Los datos de ejemplo son ficticios. La aplicación se ejecuta localmente y todos los alumnos de la demo usan las mismas funciones de consulta y publicación, sin iniciar sesión.

## Flujos principales

1. **Consultar.** El alumno selecciona su curso y, opcionalmente, una fecha. Ve los resúmenes y los pedidos pendientes que coinciden con esos filtros. Cada resumen muestra fecha, materia, tema, tarea y apuntes cuando están disponibles.
2. **Pedir un resumen.** Si la clase que busca todavía no aparece, el alumno indica el curso, la fecha y la materia. Su pedido queda visible en la lista de pendientes.
3. **Compartir un resumen.** Un compañero carga el curso, la fecha, la materia y el tema que dieron. Puede agregar la tarea y sus apuntes como texto. Si existe un pedido para esa clase, queda resuelto al guardar el resumen y sale de la lista de pendientes.

## Contrato de la API

El frontend consume una API REST propia implementada con `http.server` de la biblioteca estándar de Python. SQLite guarda clases y pedidos a través de `sqlite3` entre ejecuciones.

| Método y ruta | Entrada | Resultado |
|---|---|---|
| `GET /api/clases` | Filtro obligatorio `curso` y opcional `fecha` en la consulta. | `200` con una lista JSON de resúmenes. |
| `GET /api/pedidos` | Filtro obligatorio `curso` y opcional `fecha` en la consulta. | `200` con una lista JSON de pedidos pendientes. |
| `POST /api/clases` | JSON con `curso`, `fecha`, `materia`, `tema` y, opcionalmente, `tarea` y `apuntes`. | `201` con el resumen guardado. Resuelve el pedido coincidente si existe. |
| `POST /api/pedidos` | JSON con `curso`, `fecha` y `materia`. | `201` con el pedido guardado. |

### Datos y reglas

- `curso` admite `4° Computación`, `5° Computación` y `6° Computación`.
- `fecha` usa el formato `AAAA-MM-DD` y debe ser una fecha válida del calendario. Si se omite el filtro de fecha, se muestran las fechas disponibles para el curso consultado.
- `materia` es texto libre no vacío. La app normaliza los espacios y compara sin distinguir mayúsculas al identificar una clase. Por ejemplo, «Redes» y « redes » representan la misma materia.
- `tema` es texto obligatorio. `tarea` y `apuntes` se pueden omitir.
- La identidad de una clase se define por curso, fecha y materia normalizada. La API devuelve `409` al duplicar un resumen o un pedido pendiente y al pedir un resumen que ya existe.
- Una entrada inválida devuelve `400`. Los errores de la API tienen formato JSON `{"error": "mensaje"}`.

## Criterios de aceptación

| Caso | Resultado observable |
|---|---|
| Consultar 6° Computación para un día con un resumen de Redes | La app muestra el tema, la tarea y los apuntes cargados para ese día. |
| Cambiar de fecha o curso | La lista se actualiza con las coincidencias de los filtros. Si no hay resultados, la app muestra un estado vacío. |
| Crear un pedido para una clase sin resumen | La API devuelve `201` y el pedido aparece al consultar los pendientes. |
| Repetir el pedido cambiando mayúsculas y espacios de la materia | La API devuelve `409` y sigue visible un solo pedido. |
| Compartir el resumen solicitado | La API devuelve `201`, el resumen se puede consultar y el pedido deja de figurar como pendiente. |
| Pedir una clase con resumen publicado | La API devuelve `409` y no crea un pedido. |
| Enviar una fecha como `2026-02-30` | La API devuelve `400` y no guarda el dato. |
| Reiniciar el servidor | Los resúmenes y pedidos guardados siguen disponibles en SQLite. |
