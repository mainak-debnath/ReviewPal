from __future__ import annotations

from dataclasses import replace

from checkout.models import Order, OrderStatus


class OrderRepository:
    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}

    async def save(self, order: Order) -> Order:
        self._orders[order.order_id] = replace(order)
        return self._orders[order.order_id]

    async def get(self, order_id: str) -> Order | None:
        order = self._orders.get(order_id)
        if order is None:
            return None
        return replace(order)

    async def update_status(self, order_id: str, status: OrderStatus) -> None:
        order = self._orders[order_id]
        self._orders[order_id] = replace(order, status=status)
