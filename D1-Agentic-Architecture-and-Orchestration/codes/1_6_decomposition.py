# 1_6_decomposition.py — anthropic 2.14. Run: make run 1_6  (reviews extra/*.py)  or pass files: ... 1_6_decomposition.py a.py b.py
"""Prompt chaining: one big review split into small, focused calls.

Single pass = ONE call: all files + "find every bug". Attention spreads thin, so bugs get missed.
Chain = Step 1: one call PER FILE (local bugs) → Step 2: one call with ALL files (cross-file bugs only).

Analogy: inspecting a house. Single pass = one quick walk-through, looking at everything at once.
Chain = inspect each room alone (Step 1), then check only the pipes and wires BETWEEN rooms (Step 2).
Python view: Step 1 = unit tests, Step 2 = integration test.
"""

import pathlib
import sys

import anthropic

client = anthropic.Anthropic()


def ask_claude(prompt: str) -> str:
    """One API call: prompt in, text out. Every step of the chain uses this."""
    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


EXTRA_DIR = pathlib.Path(__file__).parent / "extra"
paths = [pathlib.Path(arg) for arg in sys.argv[1:]] or sorted(EXTRA_DIR.glob("*.py"))
# {"orders.py": "<source code>", ...}
sources = {path.name: path.read_text() for path in paths}

# Step 1 — N calls, one per file. The model sees ONE small file, so it reads it closely.
# Weak spot: it can't see the other files, so it can't catch bugs BETWEEN files.
per_file_reviews = {
    name: ask_claude(
        "Review ONLY this file for bugs. Max 5 findings: line, issue, fix.\n"
        + f"<file name='{name}'>\n{source}\n</file>"
    )
    for name, source in sources.items()
}
for name, review in per_file_reviews.items():
    print(f"=== {name}\n{review}\n")

# Step 2 — 1 call with ALL files. Told to skip local bugs (Step 1 did them),
# so its whole attention goes to the seams: what one file passes to another.
# It gets the raw files again, NOT Step 1's answers.
all_files = "\n".join(
    f"<file name='{name}'>\n{source}\n</file>" for name, source in sources.items()
)
print(
    "=== CROSS-FILE\n"
    + ask_claude(
        "These files were already reviewed one by one. Report ONLY cross-file problems: "
        + "data passed between files, mismatched function contracts, duplicated logic.\n"
        + all_files
    )
)


# ---------------------------------------------------------------------------
# Sample output (claude-haiku-5-5): make run 1_6
# ---------------------------------------------------------------------------
# === inventory.py
# **Findings for `inventory.py`:**
#
# 1. **Line 9, `in_stock`: off-by-one.** `>` returns False when `qty` equals the stock on hand, so the last units of an item can never be sold.
#    **Fix:** `return STOCK.get(item, 0) >= qty`
#
# 2. **Line 13, `remove`: no bounds check.** Removing more than is in stock drives `STOCK[item]` negative without any error.
#    **Fix:** Check first, then subtract:
#    ```python
#    available = STOCK.get(item, 0)
#    if qty <= 0 or qty > available:
#        raise ValueError(f"cannot remove {qty} of {item!r}; {available} in stock")
#    STOCK[item] = available - qty
#    ```
#
# 3. **Line 13, `remove`: unknown items raise a bare `KeyError`.** `in_stock` treats a missing item as 0 stock (line 9), but `remove` crashes on the same item, so the two functions disagree about unknown items. The fix in item 2 (using `.get`) resolves this.
#
# 4. **Lines 7–13: non-positive quantities are not rejected.** `in_stock(item, -5)` returns True, and `remove(item, -5)` increases stock. Negative or zero quantities should be rejected in both functions (the check in item 2 covers `remove`; add `qty <= 0` handling to `in_stock` too).
#
# 5. **Lines 7–13: check-then-act with shared mutable state.** `in_stock` and `remove` operate on the module-level dict `STOCK` with no locking. Two callers can both pass `in_stock` for the last unit and then both call `remove`, overdrawing stock. This is a race under concurrency; a `threading.Lock` around the check and the update, or a single atomic `try_remove` function, would address it.
#
# === orders.py
# **1. Lines 18-19: `except Exception: return 0.0` hides failures**
# A stock shortage (line 13), a bad price lookup, or a failed `remove()` all return `0.0`, the same value as a legitimately free order. The caller can't tell a failed order from a successful one, and the error is lost.
# *Fix:* Catch only the expected error, or let it propagate, e.g. `except ValueError as e: raise` or remove the `try` entirely. If a failure value is needed, return a result object or raise to the caller.
#
# **2. Lines 15-16: stock is removed without rollback**
# If `remove()` raises partway through the loop, earlier items are already deducted but the order is not placed. The `except` on line 18 then returns `0.0`, leaving inventory inconsistent.
# *Fix:* Validate all lines first, then remove stock. Or track removals and restore them on failure. Also consider holding a lock across the check and the removal, since `in_stock` (line 12) and `remove` (line 16) are separate calls and can race with another order.
#
# **3. Line 12 vs. line 16: argument order is inconsistent**
# `in_stock(qty, item)` takes quantity first, but `remove(item, qty)` takes item first. If both signatures are as their calls suggest, one of these calls is passing arguments in the wrong order, and this is easy to get wrong silently with two strings/ints.
# *Fix:* Check the signatures in `inventory.py`, then make both calls use the same order (e.g., `in_stock(item, qty)`).
#
# **4. Lines 11-12: quantities are not validated**
# Zero or negative `qty` values pass the stock check. A negative quantity could increase stock via `remove()` or produce a negative subtotal and a refund-like charge.
# *Fix:* Before line 11, add `if qty <= 0: raise ValueError(f"{item}: quantity must be positive")`.
#
# **5. Line 9 and the `discount` parameter: no range check**
# `discount` is not validated. A value above 1.0 or below 0 yields a negative or inflated price with no error.
# *Fix:* Add `if not 0 <= discount <= 1: raise ValueError("discount must be between 0 and 1")` at the start of the function.
#
# === pricing.py
# **1. `pricing.py`, `add_fees` signature (line 17):** Mutable default argument `fees: list[float] = []`. The same list object is shared across all calls, so fees accumulate between calls.
# **Fix:** `def add_fees(total: float, fees: list[float] | None = None) -> float:` and use `fees = fees or []` inside.
#
# **2. `pricing.py`, `add_fees` body (line 18):** `fees.append(0.50)` mutates the caller's list, and the $0.50 is re-added on every call. Even with a fresh list, the function changes its input. The docstring also says it adds the fixed fee, not that it sums a list.
# **Fix:** Don't mutate. Use `return total + 0.50 + sum(fees or [])`.
#
# **3. `pricing.py`, `subtotal` (line 9):** `prices[item]` raises a bare `KeyError` for an unknown item, with no indication of which item failed.
# **Fix:** Check membership and raise `ValueError(f"unknown item: {item}")`, or use `prices.get` with an explicit error.
#
# **4. `pricing.py`, `apply_discount` (line 14):** No validation on `percent`. Values above 100 produce negative totals, and negative values silently increase the price.
# **Fix:** `if not 0 <= percent <= 100: raise ValueError("percent must be between 0 and 100")`.
#
# **5. `pricing.py`, `subtotal` / `apply_discount` / `add_fees` returns:** Money is computed as binary floats and never rounded to cents, so results like `19.999999999` can reach the customer or cause mismatched totals.
# **Fix:** Round final amounts with `round(x, 2)`, or use `decimal.Decimal` for money throughout.
#
# === CROSS-FILE
# **1. Arguments swapped in the `in_stock` call (orders.py → inventory.py)**
# `orders.py` calls `in_stock(qty, item)`, but `inventory.in_stock` is defined as `in_stock(item: str, qty: int)`. `STOCK.get(qty, 0)` returns 0 for an int key, and `0 > item` raises `TypeError`. The bare `except Exception` in `place_order` swallows that, so every order returns `0.0` and no stock is removed. Fix: `in_stock(item, qty)`.
#
# **2. Units mismatch: cents vs. dollars (inventory.py → orders.py → pricing.py)**
# `inventory.py` says prices are in cents (`PRICES = {"apple": 120, ...}`). `pricing.py` says all money is in dollars. `orders.py` passes `PRICES` straight into `subtotal`, so the total is in cents, then `add_fees` adds the dollar fee `0.50` to it, and `place_order` returns it as "dollars". A 1-apple order would charge $120.50 instead of $1.20 + $0.50. Fix by converting `PRICES` to dollars at the boundary, or by making `subtotal` and `place_order` cents-aware throughout.
#
# **3. Discount contract mismatch (orders.py → pricing.py)**
# `pricing.apply_discount` documents `percent: 10 means 10% off`, but `orders.place_order` defaults `discount=0.1`. That gives 0.1% off, not 10%. Either the default should be `10`, or the caller's convention needs to be documented as a fraction and `apply_discount` changed to match.
#
# **4. Mutable default argument shared across calls (orders.py → pricing.py)**
# `add_fees(total, fees=[])` appends to the shared default list on every call. Each `place_order` call adds another `0.50` to the list, so the fee grows with every order processed (1st order: $0.50, 2nd: $1.00, and so on). Fix: `fees: list[float] | None = None`, or drop the parameter and add the constant fee directly.
#
# **5. Stock boundary mismatch (inventory.py ↔ its contract)**
# `in_stock` is documented as "True if we can sell `qty`", but it uses `>`, so selling exactly the remaining stock is refused (e.g., 10 apples in stock, `in_stock("apple", 10)` returns `False`). The check should be `>=`. Callers in `orders.py` rely on this function for the sell decision, so the bug affects every order.
#
# **6. Errors masked across files (orders.py)**
# The broad `except Exception` in `place_order` hides the bugs above (items 1, 2, and the `TypeError`) and returns `0.0` as if it were a valid charge amount. A caller cannot tell "out of stock" from "crashed." Catch the specific `ValueError` for stock failures and let other errors propagate.
