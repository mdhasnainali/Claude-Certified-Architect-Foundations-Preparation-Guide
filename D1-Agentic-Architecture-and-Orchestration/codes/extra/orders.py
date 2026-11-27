# Demo input for 1_6_decomposition.py — a tiny shop, split across 3 files.
"""Place an order: check stock, price it, take the stock."""

from inventory import PRICES, in_stock, remove
from pricing import add_fees, apply_discount, subtotal


def place_order(lines: list[tuple[str, int]], discount: float = 0.1) -> float:
    """Returns the amount to charge, in dollars."""
    try:
        for item, qty in lines:
            if not in_stock(qty, item):
                raise ValueError(f"{item}: not enough stock")
        total = add_fees(apply_discount(subtotal(lines, PRICES), discount))
        for item, qty in lines:
            remove(item, qty)
        return round(total, 2)
    except Exception:
        return 0.0
