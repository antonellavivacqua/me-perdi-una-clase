from datetime import date

from datos import CURSOS


def validar_curso(curso):
    if curso not in CURSOS:
        raise ValueError("Elegí un curso válido.")
    return curso


def validar_fecha(fecha):
    try:
        if date.fromisoformat(fecha).isoformat() == fecha:
            return fecha
    except (TypeError, ValueError):
        pass
    raise ValueError("Ingresá una fecha válida en formato AAAA-MM-DD.")


def validar_texto(cuerpo, campo, limite, requerido=True):
    valor = cuerpo.get(campo, "")
    if not isinstance(valor, str):
        raise ValueError(f"El campo {campo} debe ser texto.")
    valor = " ".join(valor.split()) if campo == "materia" else valor.strip()
    if (requerido and not valor) or len(valor) > limite:
        raise ValueError(f"Revisá el campo {campo}. Admite hasta {limite} caracteres.")
    return valor


def validar_publicacion(cuerpo, publicado):
    if not isinstance(cuerpo, dict):
        raise ValueError("Enviá un objeto JSON.")
    entrada = {
        "curso": validar_curso(cuerpo.get("curso")),
        "fecha": validar_fecha(cuerpo.get("fecha")),
        "materia": validar_texto(cuerpo, "materia", 80),
    }
    if publicado:
        entrada.update(
            tema=validar_texto(cuerpo, "tema", 160),
            tarea=validar_texto(cuerpo, "tarea", 1000, False),
            apuntes=validar_texto(cuerpo, "apuntes", 4000, False),
        )
    return entrada


