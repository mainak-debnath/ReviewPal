from __future__ import annotations

from checkout.models import InventoryError, OrderLine


class InventoryGateway:
    def __init__(self) -> None:
        self._available = {
            "SKU-CHAIR": 8,
            "SKU-DESK": 4,
            "SKU-LAMP": 10,
        }

    async def reserve(self, lines: list[OrderLine]) -> list[str]:
        reserved_skus: list[str] = []

        for line in lines:
            available_units = self._available.get(line.sku, 0)
            if available_units < line.quantity:
                raise InventoryError(
                    f"Not enough stock for {line.sku}; requested={line.quantity}"
                )

        for line in lines:
            self._available[line.sku] -= line.quantity
            reserved_skus.append(line.sku)

        return reserved_skus
