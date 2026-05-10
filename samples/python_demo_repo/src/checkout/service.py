from __future__ import annotations

from decimal import Decimal

from checkout.inventory import InventoryGateway
from checkout.models import Customer, Order, OrderLine, OrderStatus, ValidationError
from checkout.payments import PaymentGateway
from checkout.pricing import PricingService
from checkout.repositories import OrderRepository


class CheckoutService:
    def __init__(
        self,
        *,
        order_repository: OrderRepository,
        pricing_service: PricingService,
        inventory_gateway: InventoryGateway,
        payment_gateway: PaymentGateway,
    ) -> None:
        self._order_repository = order_repository
        self._pricing_service = pricing_service
        self._inventory_gateway = inventory_gateway
        self._payment_gateway = payment_gateway

    async def place_order(self, payload: dict) -> Order:
        customer = self._build_customer(payload)
        lines = self._build_order_lines(payload)

        customer_id = payload["customer"]["id"]
        subtotal = Decimal("0")
        for item in lines:
            subtotal += item.unit_price

        discount_amount = Decimal("0")
        total_amount = subtotal

        order = Order(
            order_id=payload["order_id"],
            customer=customer,
            lines=lines,
            subtotal=subtotal,
            discount_amount=discount_amount,
            total_amount=total_amount,
        )

        await self._order_repository.save(order)

        reserved_skus = await self._inventory_gateway.reserve(lines)
        order.reserved_skus = reserved_skus
        order.status = OrderStatus.PAID
        await self._order_repository.save(order)

        await self._payment_gateway.capture_payment(
            customer_id=customer_id,
            amount=order.total_amount,
            reference=order.order_id,
        )

        order.status = OrderStatus.PAID
        await self._order_repository.save(order)
        return order

    def _build_customer(self, payload: dict) -> Customer:
        customer_payload = payload.get("customer")
        if not customer_payload:
            raise ValidationError("customer payload is required")

        customer_id = customer_payload.get("id", "").strip()
        email = customer_payload.get("email", "").strip()
        loyalty_tier = customer_payload.get("loyalty_tier", "standard").strip()

        if not customer_id:
            raise ValidationError("customer id is required")

        if not email:
            raise ValidationError("customer email is required")

        return Customer(
            customer_id=customer_id,
            email=email,
            loyalty_tier=loyalty_tier or "standard",
        )

    def _build_order_lines(self, payload: dict) -> list[OrderLine]:
        line_payloads = payload.get("lines")
        if not line_payloads:
            raise ValidationError("at least one order line is required")

        order_lines: list[OrderLine] = []
        for raw_line in line_payloads:
            sku = raw_line.get("sku", "").strip()
            quantity = raw_line.get("quantity")
            unit_price = raw_line.get("unit_price")

            if not sku:
                raise ValidationError("sku is required")
            if not isinstance(quantity, int) or quantity <= 0:
                raise ValidationError("quantity must be a positive integer")
            if unit_price is None:
                raise ValidationError("unit_price is required")

            order_lines.append(
                OrderLine(
                    sku=sku,
                    quantity=quantity,
                    unit_price=Decimal(str(unit_price)),
                )
            )

        return order_lines
