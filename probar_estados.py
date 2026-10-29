from decimal import Decimal
from cargar_csv import load_fixture
from app.domain import Money, OrderItem


def intentar(etiqueta, accion):
    try:
        accion()
        print(etiqueta, "-> OK")
    except Exception as e:
        print(etiqueta, "-> RECHAZADO:", type(e).__name__, "-", e)


o = load_fixture()

intentar("O003 confirmar (cliente inactivo)", o["O003"].confirm)
intentar("O007 confirmar (vacío)", o["O007"].confirm)
intentar("O008 confirmar (20 unidades)", o["O008"].confirm)
intentar("O009 agregar 2 (pasaría de 20)",
         lambda: o["O009"].add_item(OrderItem("SKU003", 2, Money(Decimal("120.00")))))
print("O009 unidades:", o["O009"].units)

o["O012"].confirm()
intentar("O012 enviar sin guía", lambda: o["O012"].ship(""))
print("O012:", o["O012"].status.value, [e.name for e in o["O012"].events])

o["O013"].confirm()
intentar("O013 confirmar otra vez", o["O013"].confirm)
print("O013 eventos:", len(o["O013"].events))

o["O014"].confirm()
o["O014"].ship("GUIA1")
intentar("O014 cancelar desde SHIPPED", lambda: o["O014"].cancel("motivo"))
print("O014:", o["O014"].status.value, "eventos:", len(o["O014"].events))

o["O015"].confirm()
o["O015"].ship("GUIA2")
o["O015"].return_order()
print("O015:", o["O015"].status.value)

o["O016"].confirm()
o["O016"].ship("GUIA3")
o["O016"].deliver()
print("O016:", o["O016"].status.value)