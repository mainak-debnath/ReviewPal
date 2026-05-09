from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    RESERVED = "reserved"
    PAID = "paid"
    FAILED = "failed"


@dataclass(frozen=True)
class OrderLine:
    sku: str
    quantity: int
    unit_price: Decimal


@dataclass(frozen=True)
class Customer:
    customer_id: str
    email: str
    loyalty_tier: str = "standard"


@dataclass
class Order:
    order_id: str
    customer: Customer
    lines: list[OrderLine]
    subtotal: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    total_amount: Decimal = Decimal("0")
    status: OrderStatus = OrderStatus.PENDING
    reserved_skus: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PaymentReceipt:
    payment_id: str
    amount: Decimal


class CheckoutError(Exception):
    """Base checkout workflow error."""


class ValidationError(CheckoutError):
    """Raised when request data is not valid for checkout."""


class InventoryError(CheckoutError):
    """Raised when inventory reservation fails."""


class PaymentError(CheckoutError):
    """Raised when payment capture fails."""
