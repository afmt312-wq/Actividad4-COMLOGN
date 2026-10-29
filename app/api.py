from decimal import Decimal

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.domain import InvalidOrderData, InvalidOrderTransition, OrderItemLimitExceeded
from app.specifications import discount_rate
from cargar_csv import load_fixture

app = FastAPI(title="TechStore API", version="1.0")

# Repositorio en memoria: no persiste cambios entre ejecuciones.
ORDERS = load_fixture()


def reset_orders():
    """Recarga los pedidos originales (útil para pruebas)."""
    ORDERS.clear()
    ORDERS.update(load_fixture())


class ShipRequest(BaseModel):
    tracking_number: str


class CancelRequest(BaseModel):
    reason: str


class OrderResponse(BaseModel):
    id: str
    customer_id: str
    status: str
    units: int
    total: Decimal
    discount_rate: Decimal
    events: list[str]


def to_response(order):
    return OrderResponse(
        id=order.id,
        customer_id=order.customer.id,
        status=order.status.value,
        units=order.units,
        total=order.total.amount,
        discount_rate=discount_rate(order),
        events=[e.name for e in order.events],
    )


def get_order(order_id: str):
    order = ORDERS.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Pedido {order_id} no encontrado")
    return order


@app.exception_handler(InvalidOrderTransition)
async def transition_handler(request, exc):
    return JSONResponse(status_code=409, content={"error": str(exc)})


@app.exception_handler(InvalidOrderData)
async def data_handler(request, exc):
    return JSONResponse(status_code=422, content={"error": str(exc)})


@app.exception_handler(OrderItemLimitExceeded)
async def limit_handler(request, exc):
    return JSONResponse(status_code=422, content={"error": str(exc)})


@app.get("/orders/{order_id}", response_model=OrderResponse)
def read_order(order_id: str):
    return to_response(get_order(order_id))


@app.post("/orders/{order_id}/confirm", response_model=OrderResponse)
def confirm_order(order_id: str):
    order = get_order(order_id)
    order.confirm()
    return to_response(order)


@app.post("/orders/{order_id}/ship", response_model=OrderResponse)
def ship_order(order_id: str, body: ShipRequest):
    order = get_order(order_id)
    order.ship(body.tracking_number)
    return to_response(order)


@app.post("/orders/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: str, body: CancelRequest):
    order = get_order(order_id)
    order.cancel(body.reason)
    return to_response(order)