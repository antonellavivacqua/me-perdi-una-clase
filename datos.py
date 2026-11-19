import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path

CURSOS = ("4° Computación", "5° Computación", "6° Computación")
RUTA_DB = Path(__file__).with_name("clases.sqlite3")


class Conflicto(ValueError):
    pass


@contextmanager
def conexion(ruta):
    db = sqlite3.connect(ruta)
    db.row_factory = sqlite3.Row
    try:
        with db:
            yield db
    finally:
        db.close()


def inicializar(ruta, demo=False):
    with conexion(ruta) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY,
                curso TEXT NOT NULL,
                fecha TEXT NOT NULL,
                materia TEXT NOT NULL,
                materia_clave TEXT NOT NULL,
                tema TEXT,
                tarea TEXT NOT NULL DEFAULT '',
                apuntes TEXT NOT NULL DEFAULT '',
                UNIQUE (curso, fecha, materia_clave)
            )
        """)
        db.execute("CREATE TABLE IF NOT EXISTS configuracion (clave TEXT PRIMARY KEY)")
        if demo:
            sembrado = db.execute("INSERT OR IGNORE INTO configuracion VALUES ('demo')")
            if sembrado.rowcount:
                hoy = date.today()
                ejemplos = [
                    (CURSOS[2], hoy, "Redes", "Asignación de direcciones con DHCP",
                     "Dibujar el intercambio DORA y explicar qué datos ofrece el servidor.",
                     "Discover busca servidores. Offer propone una IP. Request elige una oferta. ACK confirma la asignación."),
                    (CURSOS[2], hoy - timedelta(days=1), "Base de Datos",
                     "Consultas con JOIN", "Resolver las consultas 1 a 3 con INNER JOIN.",
                     "INNER JOIN devuelve filas con coincidencia en ambas tablas."),
                    (CURSOS[2], hoy, "Desarrollo de Sistemas", None, "", ""),
                    (CURSOS[1], hoy, "Programación", "Clases y objetos",
                     "Modelar un libro con atributos y métodos.", ""),
                ]
                db.executemany("""
                    INSERT OR IGNORE INTO registros
                        (curso, fecha, materia, tema, tarea, apuntes, materia_clave)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                """, [(*fila, fila[2].casefold()) for fila in ejemplos])


def listar(ruta, curso, fecha, publicado):
    condicion = "IS NOT NULL" if publicado else "IS NULL"
    columnas = "id, curso, fecha, materia, tema, tarea, apuntes" if publicado else "id, curso, fecha, materia"
    consulta = f"SELECT {columnas} FROM registros WHERE tema {condicion} AND curso = ?"
    parametros = [curso]
    if fecha:
        consulta += " AND fecha = ?"
        parametros.append(fecha)
    consulta += " ORDER BY fecha DESC, materia_clave"
    with conexion(ruta) as db:
        return [dict(fila) for fila in db.execute(consulta, parametros)]


def guardar(ruta, entrada, publicado):
    with conexion(ruta) as db:
        db.execute("BEGIN IMMEDIATE")
        clave = entrada["curso"], entrada["fecha"], entrada["materia"].casefold()
        anterior = db.execute("""
            SELECT id, tema FROM registros WHERE curso = ? AND fecha = ? AND materia_clave = ?
        """, clave).fetchone()
        if anterior and anterior["tema"] is not None:
            raise Conflicto("Ya hay un resumen de esa materia para ese día.")
        if anterior and not publicado:
            raise Conflicto("Ya hay un pedido para esa materia y ese día.")

        campos = entrada["materia"], entrada.get("tema"), entrada.get("tarea", ""), entrada.get("apuntes", "")
        if anterior:
            registro_id = anterior["id"]
            db.execute("""
                UPDATE registros SET materia = ?, tema = ?, tarea = ?, apuntes = ? WHERE id = ?
            """, (*campos, registro_id))
        else:
            registro_id = db.execute("""
                INSERT INTO registros (curso, fecha, materia_clave, materia, tema, tarea, apuntes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (*clave, *campos)).lastrowid
        return {"id": registro_id, **entrada}
