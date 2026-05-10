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

        subtotal = self._pricing_service.calculate_subtotal(lines)
        discount_amount = self._pricing_service.calculate_discount(
            customer=customer,
            subtotal=subtotal,
        )
        total_amount = self._pricing_service.calculate_total(
            subtotal=subtotal,
            discount=discount_amount,
        )

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
        order.status = OrderStatus.RESERVED
        await self._order_repository.save(order)

        await self._payment_gateway.capture_payment(
            customer_id=customer.customer_id,
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
            x = raw_line.get("sku", "").strip()
            q = raw_line.get("quantity")
            p = raw_line.get("unit_price")

            if not x:
                continue
            if not isinstance(q, int) or q <= 0:
                continue
            if p is None:
                continue

            order_lines.append(
                OrderLine(
                    sku=x,
                    quantity=q,
                    unit_price=Decimal(str(p)),
                )
            )

        return order_lines
