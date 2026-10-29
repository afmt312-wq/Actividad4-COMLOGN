import pytest
from fastapi.testclient import TestClient

from app.api import app, reset_orders

client = TestClient(app)


@pytest.fixture(autouse=True)
def recargar_datos():
    reset_orders()


def test_pedido_inexistente_404():
    assert client.get("/orders/O999").status_code == 404


def test_confirmar_pedido_ok_200():
    r = client.post("/orders/O001/confirm")
    assert r.status_code == 200
    assert r.json()["status"] == "CONFIRMED"
    assert r.json()["events"] == ["OrderConfirmed"]


def test_confirmar_dos_veces_409():
    client.post("/orders/O013/confirm")
    assert client.post("/orders/O013/confirm").status_code == 409


def test_confirmar_pedido_vacio_422():
    assert client.post("/orders/O007/confirm").status_code == 422
