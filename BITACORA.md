# Bitácora de desarrollo · Me perdí una clase

**Materia** · Prácticas Profesionalizantes  
**Fecha de trabajo** · 18 de noviembre de 2026

## 1. Definición del problema y alcance

La idea elegida fue recuperar lo que se vio el día que un alumno faltó. El recorrido quedó definido en tres acciones: consultar por curso y fecha, pedir un resumen y responder con tema, tarea y apuntes de texto. Se eligieron ejemplos de 4°, 5° y 6° de Computación para la demo.

## 2. Spec y trabajo con agentes

Se usaron dos agentes con tareas concretas. El contrato de la API sirvió como punto de coordinación.

| Agente | Tarea | Entregable |
|---|---|---|
| Especificación | Definió los flujos, entradas y resultados observables | `SPEC.md` |
| Interfaz | Implementó los filtros, listas, formularios y respuesta a pedidos | `static/index.html`, `static/style.css`, `static/app.js` |
| Coordinación e integración | Implementó el servidor y la persistencia, alineó los límites de formularios con la API y ejecutó las pruebas | `app.py`, `datos.py`, `validacion.py`, `pruebas/test_api.py` |

Se eligió Python con SQLite y un servidor HTTP de la biblioteca estándar para que la demo se pueda abrir con Python instalado y sin descargar paquetes.

## 3. Implementación

La interfaz pide listas JSON y envía formularios mediante `fetch`. Cada registro se identifica por curso, fecha y materia normalizada. Si alguien responde un pedido, la API agrega el tema, la tarea y los apuntes al mismo registro en una transacción. Entonces el registro aparece en resúmenes y sale de pendientes. La restricción única de SQLite y la transacción evitan que dos pedidos simultáneos creen duplicados.

## 4. Refactoring realizado

La primera versión tenía las funciones de validación dentro de `app.py`, junto al manejo de solicitudes HTTP. Se extrajeron a `validacion.py` para leer y cambiar las reglas de curso, fecha y texto en un módulo propio. Las rutas siguen traduciendo los resultados a respuestas HTTP. Las tres pruebas de integración pasaron antes y después de mover las funciones.

## 5. Verificación

- Las pruebas de integración verificaron creación y resolución del pedido, detección de duplicados con cambios de espacios y mayúsculas, validación de entradas, filtros, solicitudes simultáneas y persistencia tras reiniciar.
- El archivo JavaScript pasó el control de sintaxis.
- Se verificó por HTTP que el servidor entrega la página, la hoja de estilos, el JavaScript y los ejemplos ficticios. Quedó pendiente recorrer la interfaz en un navegador porque Chromium no pudo iniciarse en el entorno de pruebas.
