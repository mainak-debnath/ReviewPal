from __future__ import annotations

from decimal import Decimal

from checkout.models import PaymentError, PaymentReceipt


class PaymentGateway:
    async def capture_payment(
        self,
        *,
        customer_id: str,
        amount: Decimal,
        reference: str,
    ) -> PaymentReceipt:
        if amount <= Decimal("0"):
            raise PaymentError("Payment amount must be greater than zero.")

        if not customer_id:
            raise PaymentError("Customer id is required for payment capture.")

        return PaymentReceipt(payment_id=f"pay_{reference}", amount=amount)
