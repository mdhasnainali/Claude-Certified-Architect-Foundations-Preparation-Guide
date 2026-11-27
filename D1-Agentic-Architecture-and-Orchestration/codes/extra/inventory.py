# Demo input for 1_6_decomposition.py — a tiny shop, split across 3 files.
"""Stock levels and prices. Prices are in cents."""

STOCK = {"apple": 10, "pear": 4}
PRICES = {"apple": 120, "pear": 90}  # cents


def in_stock(item: str, qty: int) -> bool:
    """True if we can sell `qty` of `item`."""
    return STOCK.get(item, 0) > qty


def remove(item: str, qty: int) -> None:
    """Take `qty` of `item` out of stock."""
    STOCK[item] -= qty
