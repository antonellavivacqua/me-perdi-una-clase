# Me perdí una clase

Proyecto para Prácticas Profesionalizantes. Un alumno que faltó puede consultar qué se vio en su curso, pedir un resumen y leer el aporte de un compañero. La aplicación web consume una API REST propia y guarda los datos en SQLite.

## Cómo abrirla

1. Descomprimí el ZIP y abrí una terminal dentro de la carpeta `me-perdi-una-clase`.
2. Con Python 3.10 o posterior, ejecutá `py app.py --demo` en Windows, o `python3 app.py --demo` en macOS o Linux.
3. Entrá a [http://127.0.0.1:8000](http://127.0.0.1:8000) en tu navegador. Dejá abierta la terminal mientras usás la app.

La primera ejecución con `--demo` carga ejemplos ficticios. Python incluye las dependencias y crea el archivo `clases.sqlite3` junto al código. Podés detener el servidor con Ctrl+C. Si el puerto 8000 está ocupado, agregá `--puerto 8080` y cambiá el puerto en el navegador.

## Guion de demo

1. En **6° Computación**, abrí la página y mostrá el resumen de Redes y su tarea.
2. Filtrá por la fecha que figura en el pedido de **Desarrollo de Sistemas**. Mostrá que esa materia está pendiente.
3. Seleccioná **Responder al pedido**. Completá el tema con «DFD de nivel 1» y agregá la tarea «Descomponer el proceso de préstamo». Publicá el resumen.
4. Mostrá que aparece el resumen y que el pedido se resuelve. Actualizá la página para comprobar que se guardó.
5. En otra pestaña, abrí [la respuesta JSON de la API para 6° Computación](http://127.0.0.1:8000/api/clases?curso=6%C2%B0%20Computaci%C3%B3n) y buscá el resumen que acabás de publicar.

Podés repetir el flujo con **Pedir un resumen**, otra materia y cualquier fecha válida. Para probar la API automáticamente, ejecutá `py -m unittest discover -s pruebas` en Windows o `python3 -m unittest discover -s pruebas` en macOS o Linux.

## Archivos

| Archivo | Función |
|---|---|
| `SPEC.md` | Alcance, reglas, contrato de la API y criterios de aceptación |
| `BITACORA.md` | Decisiones, agentes, refactoring y verificaciones |
| `app.py` | Servidor web y rutas HTTP |
| `validacion.py` | Reglas para comprobar y normalizar las entradas |
| `datos.py` | Consultas, transacciones y datos ficticios |
| `static/` | Interfaz web |
| `pruebas/test_api.py` | Pruebas de integración con HTTP y una base temporal |

La versión de entrega está pensada como demo local sin cuentas. Los dos roles del guion se pueden representar desde el mismo navegador.
