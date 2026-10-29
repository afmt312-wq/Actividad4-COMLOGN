from decimal import Decimal

import pytest

from app.domain import (InvalidOrderData, InvalidOrderTransition,
                        Money, OrderItem, OrderItemLimitExceeded,
                        OrderStatus)
from app.specifications import discount_rate
from cargar_csv import load_fixture


@pytest.fixture
def orders():
    # Se recarga antes de cada prueba para que no se contaminen entre sí.
    return load_fixture()


def test_money_negativo_se_rechaza():
    with pytest.raises(InvalidOrderData):
        Money(Decimal("-1.00"))


def test_21_unidades_se_rechaza_y_no_cambia_items(orders):
    o = orders["O009"]  # tiene 19 unidades
    with pytest.raises(OrderItemLimitExceeded):
        o.add_item(OrderItem("SKU003", 2, Money(Decimal("120.00"))))
    assert o.units == 19


def test_cliente_inactivo_no_confirma(orders):
    o = orders["O003"]
    with pytest.raises(InvalidOrderData):
        o.confirm()
    assert o.status == OrderStatus.DRAFT
    assert o.events == []


def test_pedido_vacio_no_confirma(orders):
    o = orders["O007"]
    with pytest.raises(InvalidOrderData):
        o.confirm()
    assert o.status == OrderStatus.DRAFT
    assert o.events == []


def test_descuento_vip_10_por_ciento(orders):
    assert discount_rate(orders["O001"]) == Decimal("0.10")


def test_promocion_activa_bloquea_descuento(orders):
    assert discount_rate(orders["O005"]) == Decimal("0")


def test_envio_sin_guia_se_rechaza(orders):
    o = orders["O012"]
    o.confirm()
    with pytest.raises(InvalidOrderData):
        o.ship("")
    assert o.status == OrderStatus.CONFIRMED
    assert len(o.events) == 1


def test_confirmacion_doble_no_agrega_evento(orders):
    o = orders["O013"]
    o.confirm()
    with pytest.raises(InvalidOrderTransition):
        o.confirm()
    assert len(o.events) == 1


def test_cancelar_desde_shipped_se_rechaza(orders):
    o = orders["O014"]
    o.confirm()
    o.ship("GUIA1")
    with pytest.raises(InvalidOrderTransition):
        o.cancel("motivo")
    assert o.status == OrderStatus.SHIPPED
    assert len(o.events) == 2
