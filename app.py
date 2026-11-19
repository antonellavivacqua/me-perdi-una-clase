import argparse
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import datos
from validacion import validar_curso, validar_fecha, validar_publicacion

RECURSOS = {"/api/clases": True, "/api/pedidos": False}
STATIC = Path(__file__).with_name("static")
ARCHIVOS = {
    "/": ("index.html", "text/html"),
    "/static/style.css": ("style.css", "text/css"),
    "/static/app.js": ("app.js", "text/javascript"),
}


class Aplicacion(BaseHTTPRequestHandler):
    def enviar(self, estado, contenido, tipo):
        self.send_response(estado)
        self.send_header("Content-Type", f"{tipo}; charset=utf-8")
        self.send_header("Content-Length", str(len(contenido)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(contenido)

    def responder(self, estado, objeto):
        self.enviar(
            estado,
            json.dumps(objeto, ensure_ascii=False).encode(),
            "application/json",
        )

    def do_GET(self):
        url = urlsplit(self.path)

        if url.path in ARCHIVOS:
            nombre, tipo = ARCHIVOS[url.path]
            self.enviar(200, (STATIC / nombre).read_bytes(), tipo)
            return

        if url.path not in RECURSOS:
            self.responder(404, {"error": "Ruta inexistente."})
            return

        try:
            parametros = parse_qs(url.query)
            curso = validar_curso(parametros.get("curso", [""])[0])
            fecha = parametros.get("fecha", [""])[0]

            if fecha:
                validar_fecha(fecha)

            registros = datos.listar(
                self.server.ruta_db, curso, fecha, RECURSOS[url.path]
            )
            self.responder(200, registros)
        except ValueError as error:
            self.responder(400, {"error": str(error)})
        except sqlite3.Error:
            self.responder(
                503, {"error": "La base de datos no está disponible. Reintentá."}
            )

    def do_POST(self):
        ruta = urlsplit(self.path).path

        if ruta not in RECURSOS:
            self.responder(404, {"error": "Ruta inexistente."})
            return

        try:
            longitud = int(self.headers.get("Content-Length", "0"))
            if not 0 < longitud <= 65536:
                raise ValueError("El cuerpo debe tener entre 1 y 65536 bytes.")

            try:
                cuerpo = json.loads(self.rfile.read(longitud))
            except (UnicodeError, json.JSONDecodeError):
                raise ValueError("El cuerpo de la solicitud debe ser JSON válido.") from None

            publicado = RECURSOS[ruta]
            entrada = validar_publicacion(cuerpo, publicado)
            self.responder(201, datos.guardar(self.server.ruta_db, entrada, publicado))
        except datos.Conflicto as error:
            self.responder(409, {"error": str(error)})
        except ValueError as error:
            self.responder(400, {"error": str(error)})
        except sqlite3.Error:
            self.responder(
                503, {"error": "La base de datos no está disponible. Reintentá."}
            )


def crear_servidor(puerto=8000, ruta_db=datos.RUTA_DB, demo=False):
    datos.inicializar(ruta_db, demo)
    servidor = ThreadingHTTPServer(("0.0.0.0", puerto), Aplicacion)
    servidor.ruta_db = ruta_db
    return servidor


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Me perdí una clase")
    parser.add_argument("--puerto", type=int, default=8000)
    parser.add_argument(
        "--demo", action="store_true", help="Carga ejemplos ficticios una vez por base."
    )
    opciones = parser.parse_args()

    with crear_servidor(opciones.puerto, demo=opciones.demo) as servidor:
        print(f"Servidor iniciado en el puerto {servidor.server_port}", flush=True)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass