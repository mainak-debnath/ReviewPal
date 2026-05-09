from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from checkout.models import Customer, OrderLine


class PricingService:
    def calculate_subtotal(self, lines: list[OrderLine]) -> Decimal:
        subtotal = Decimal("0")
        for line in lines:
            subtotal += line.unit_price * line.quantity
        return subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calculate_discount(
        self, *, customer: Customer, subtotal: Decimal
    ) -> Decimal:
        if customer.loyalty_tier == "gold":
            return (subtotal * Decimal("0.10")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        if customer.loyalty_tier == "silver":
            return (subtotal * Decimal("0.05")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        return Decimal("0")

    def calculate_total(self, *, subtotal: Decimal, discount: Decimal) -> Decimal:
        return (subtotal - discount).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
