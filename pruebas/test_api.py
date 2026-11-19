import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app import crear_servidor

CURSO = "6° Computación"
FECHA = "2026-11-18"


class PruebasAPI(unittest.TestCase):
    def setUp(self):
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        self.ruta = Path(carpeta.name) / "test.sqlite3"
        self.iniciar()

    def iniciar(self):
        self.servidor = crear_servidor(0, self.ruta)
        self.hilo = threading.Thread(target=self.servidor.serve_forever)
        self.hilo.start()
        self.addCleanup(self.detener_actual)

    def detener_actual(self):
        if self.servidor is not None:
            self.servidor.shutdown()
            self.servidor.server_close()
            self.hilo.join()
            self.servidor = None

    def api(self, recurso, cuerpo=None, **filtros):
        url = f"http://127.0.0.1:{self.servidor.server_port}/api/{recurso}"
        if cuerpo is None:
            url += "?" + urlencode({"curso": CURSO, **filtros})
            solicitud = Request(url)
        else:
            solicitud = Request(url, json.dumps(cuerpo).encode(), {"Content-Type": "application/json"})
        try:
            respuesta = urlopen(solicitud, timeout=5)
        except HTTPError as error:
            respuesta = error
        with respuesta:
            return respuesta.status, json.load(respuesta)

    def test_pedir_y_publicar_resuelve_pedido(self):
        pedido = {"curso": CURSO, "fecha": FECHA, "materia": "Base de Datos"}
        estado, pendiente = self.api("pedidos", pedido)
        self.assertEqual(estado, 201)
        self.assertEqual(self.api("pedidos", fecha=FECHA), (200, [pendiente]))
        self.assertEqual(self.api("pedidos", {**pedido, "materia": " BASE  de datos "})[0], 409)
        estado, clase = self.api("clases", {**pedido, "materia": "base de datos", "tema": "JOIN"})
        self.assertEqual(estado, 201)
        self.assertEqual(clase["id"], pendiente["id"])
        self.assertEqual(self.api("pedidos"), (200, []))
        self.assertEqual(self.api("clases", fecha=FECHA), (200, [clase]))
        self.assertEqual(self.api("pedidos", pedido)[0], 409)
        self.assertEqual(self.api("clases", {**pedido, "tema": "SQL"})[0], 409)

    def test_validaciones_y_filtros(self):
        clase = {"curso": CURSO, "fecha": FECHA, "materia": "Redes", "tema": "DHCP"}
        for cambios in ({"fecha": "2026-02-30"}, {"curso": "9°"}, {"tema": " "}, {"apuntes": 2}):
            with self.subTest(cambios=cambios):
                self.assertEqual(self.api("clases", {**clase, **cambios})[0], 400)
        self.assertEqual(self.api("clases", clase)[0], 201)
        self.assertEqual(self.api("clases", curso="4° Computación"), (200, []))
        self.assertEqual(self.api("clases", fecha="2026-11-17"), (200, []))
        self.assertEqual(self.api("clases", fecha="ayer")[0], 400)

    def test_persistencia_y_pedidos_simultaneos(self):
        pedido = {"curso": CURSO, "fecha": FECHA, "materia": "Redes"}
        with ThreadPoolExecutor(2) as grupo:
            resultados = list(grupo.map(lambda _: self.api("pedidos", pedido)[0], range(2)))
        self.assertEqual(sorted(resultados), [201, 409])
        self.detener_actual()
        self.iniciar()
        estado, pendientes = self.api("pedidos")
        self.assertEqual(estado, 200)
        self.assertEqual(len(pendientes), 1)
        self.assertEqual(pendientes[0]["materia"], "Redes")
