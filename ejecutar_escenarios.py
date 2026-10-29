"""Ejecuta los escenarios E01 a E15 y muestra el resultado de cada uno.
Recarga los datos (load_fixture) antes de cada caso."""
from decimal import Decimal

from app.domain import Money, OrderItem
from app.specifications import discount_rate
from cargar_csv import load_fixture


def eventos(o):
    return ", ".join(e.name for e in o.events) or "sin evento"


def descuento(pid):
    o = load_fixture()[pid]
    return f"{int(discount_rate(o) * 100)}%"


def intenta(accion):
    try:
        accion()
        return None
    except Exception as e:
        return f"{type(e).__name__}: {e}"


def caso(cid, pid, inicial, operacion, f):
    o = load_fixture()[pid]
    resultado = f(o)
    print(f"{cid} | {pid} | {inicial} | {operacion} | {resultado} | "
          f"estado final {o.status.value} | {eventos(o)}")


def e_desc(o):
    return f"Descuento {int(discount_rate(o) * 100)}%"


def e_conf(o):
    err = intenta(o.confirm)
    return f"RECHAZADO ({err})" if err else "Confirmado"


def e_add(o):
    err = intenta(lambda: o.add_item(
        OrderItem("SKU003", 2, Money(Decimal("120.00")))))
    return (f"RECHAZADO ({err}); unidades = {o.units}" if err else "Agregado")


def e_conf_envio_sin_guia(o):
    o.confirm()
    err = intenta(lambda: o.ship(""))
    return f"Confirmó; envío RECHAZADO ({err})"


def e_conf_doble(o):
    o.confirm()
    err = intenta(o.confirm)
    return f"2a confirmación RECHAZADA ({err})"


def e_cancel_shipped(o):
    o.confirm()
    o.ship("GUIA1")
    err = intenta(lambda: o.cancel("motivo"))
    return f"Cancelar RECHAZADO ({err})"


def e_devolver(o):
    o.confirm(); o.ship("GUIA2"); o.return_order()
    return "Confirmar, enviar y devolver OK"


def e_entregar(o):
    o.confirm(); o.ship("GUIA3"); o.deliver()
    return "Confirmar, enviar y entregar OK"


caso("E01", "O001", "DRAFT", "evaluar descuento", e_desc)
caso("E02", "O002", "DRAFT", "evaluar descuento", e_desc)
caso("E03", "O003", "DRAFT", "confirmar", e_conf)
caso("E04", "O005", "DRAFT", "evaluar descuento", e_desc)
caso("E05", "O006", "DRAFT", "evaluar descuento", e_desc)
caso("E06", "O007", "DRAFT", "confirmar", e_conf)
caso("E07", "O008", "DRAFT", "confirmar", e_conf)
caso("E08", "O009", "DRAFT", "agregar SKU003 x2", e_add)
caso("E09", "O010", "DRAFT", "evaluar descuento", e_desc)
caso("E10", "O011", "DRAFT", "evaluar descuento", e_desc)
caso("E11", "O012", "DRAFT", "confirmar y enviar sin guía", e_conf_envio_sin_guia)
caso("E12", "O013", "DRAFT", "confirmar dos veces", e_conf_doble)
caso("E13", "O014", "DRAFT", "confirmar, enviar y cancelar", e_cancel_shipped)
caso("E14", "O015", "DRAFT", "confirmar, enviar y devolver", e_devolver)
caso("E15", "O016", "DRAFT", "confirmar, enviar y entregar", e_entregar)
