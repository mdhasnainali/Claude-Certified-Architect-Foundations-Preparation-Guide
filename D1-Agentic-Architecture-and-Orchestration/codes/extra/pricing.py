# Demo input for 1_6_decomposition.py — a tiny shop, split across 3 files.
"""Order maths. All money here is in dollars."""


def subtotal(lines: list[tuple[str, int]], prices: dict[str, float]) -> float:
    """Sum of price * qty for each (item, qty) line."""
    return sum(prices[item] * qty for item, qty in lines)


def apply_discount(total: float, percent: float) -> float:
    """percent: 10 means 10% off."""
    return total * (1 - percent / 100)


def add_fees(total: float, fees: list[float] = []) -> float:
    """Add the fixed $0.50 handling fee."""
    fees.append(0.50)
    return total + sum(fees)
