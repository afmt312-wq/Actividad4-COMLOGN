from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum


class DomainException(Exception): pass
class InvalidOrderData(DomainException): pass
class InvalidOrderTransition(DomainException): pass
class OrderItemLimitExceeded(DomainException): pass


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "MXN"

    def __post_init__(self):
        if not self.amount.is_finite() or self.amount < 0:
            raise InvalidOrderData("Monto inválido")


@dataclass(frozen=True)
class Customer:
    id: str
    is_vip: bool = False
    active: bool = True


@dataclass(frozen=True)
class OrderItem:
    sku: str
    quantity: int
    unit_price: Money

    def __post_init__(self):
        if not self.sku.strip() or self.quantity <= 0:
            raise InvalidOrderData("Artículo inválido")

    @property
    def subtotal(self):
        return Money(self.unit_price.amount * self.quantity)


class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"


@dataclass(frozen=True)
class DomainEvent:
    name: str
    order_id: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Order:
    customer: Customer
    id: str
    has_promotion: bool = False
    status: OrderStatus = OrderStatus.DRAFT
    items: list = field(default_factory=list)
    events: list = field(default_factory=list)

    @property
    def units(self):
        return sum(i.quantity for i in self.items)

    @property
    def total(self):
        return Money(sum((x.subtotal.amount for x in self.items), Decimal("0")))

    def add_item(self, item):
        if self.status != OrderStatus.DRAFT:
            raise InvalidOrderTransition("Solo DRAFT admite artículos")
        if self.units + item.quantity > 20:
            raise OrderItemLimitExceeded("Máximo 20 unidades")
        self.items.append(item)

    def _emit(self, name):
        self.events.append(DomainEvent(name, self.id))

    def confirm(self):
        if self.status != OrderStatus.DRAFT:
            raise InvalidOrderTransition("Solo se confirma desde DRAFT")
        if not self.items or not self.customer.active:
            raise InvalidOrderData("Requiere artículos y cliente activo")
        self.status = OrderStatus.CONFIRMED
        self._emit("OrderConfirmed")

    def ship(self, tracking_number):
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidOrderTransition("Solo se envía desde CONFIRMED")
        if not tracking_number or not tracking_number.strip():
            raise InvalidOrderData("Se requiere número de guía")
        self.status = OrderStatus.SHIPPED
        self._emit("OrderShipped")

    def cancel(self, reason):
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidOrderTransition("Solo se cancela desde CONFIRMED")
        if not reason or not reason.strip():
            raise InvalidOrderData("Se requiere motivo")
        self.status = OrderStatus.CANCELLED
        self._emit("OrderCancelled")

    def deliver(self):
        if self.status != OrderStatus.SHIPPED:
            raise InvalidOrderTransition("Solo se entrega desde SHIPPED")
        self.status = OrderStatus.DELIVERED
        self._emit("OrderDelivered")

    def return_order(self):
        if self.status != OrderStatus.SHIPPED:
            raise InvalidOrderTransition("Solo se devuelve desde SHIPPED")
        self.status = OrderStatus.RETURNED
        self._emit("OrderReturned")