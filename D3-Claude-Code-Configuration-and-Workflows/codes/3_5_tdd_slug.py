# 3_5_tdd_slug.py — Python 3.13+, offline. Tests first: concrete input → output examples Claude must satisfy.
import re

CASES = [  # (input, expected) — written BEFORE the implementation
    ("Hello World", "hello-world"),
    ("  Café crème  ", "cafe-creme"),
    ("C++ & Rust: 2026!", "c-rust-2026"),
    ("already-a-slug", "already-a-slug"),
    ("", ""),
]


def slugify(text: str) -> str:  # first attempt (pretend Claude wrote it)
    text = text.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


failures = [(i, exp, got) for i, exp in CASES if (got := slugify(i)) != exp]
print(f"{len(CASES) - len(failures)}/{len(CASES)} passing")
for i, exp, got in failures:  # paste exactly this back to Claude
    print(f"FAIL slugify({i!r}) → {got!r}, expected {exp!r}")
