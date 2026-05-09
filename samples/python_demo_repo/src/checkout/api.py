from __future__ import annotations

from checkout.inventory import InventoryGateway
from checkout.payments import PaymentGateway
from checkout.pricing import PricingService
from checkout.repositories import OrderRepository
from checkout.service import CheckoutService


def build_checkout_service() -> CheckoutService:
    return CheckoutService(
        order_repository=OrderRepository(),
        pricing_service=PricingService(),
        inventory_gateway=InventoryGateway(),
        payment_gateway=PaymentGateway(),
    )
