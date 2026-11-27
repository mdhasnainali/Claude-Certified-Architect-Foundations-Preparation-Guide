# 3_5_tdd_slug.py — Python 3.13+, offline. Tests first: concrete input → output examples Claude must satisfy.
import re

TEST_CASES = [  # (input, expected) — written BEFORE the implementation
    ("Hello World", "hello-world"),
    ("  Café crème  ", "cafe-creme"),
    ("C++ & Rust: 2026!", "c-rust-2026"),
    ("already-a-slug", "already-a-slug"),
    ("", ""),
]


def slugify(text: str) -> str:  # first attempt (pretend Claude wrote it)
    text = text.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


failures = [
    (text, expected, actual)
    for text, expected in TEST_CASES
    if (actual := slugify(text)) != expected
]
print(f"{len(TEST_CASES) - len(failures)}/{len(TEST_CASES)} passing")
for text, expected, actual in failures:  # paste exactly this back to Claude
    print(f"FAIL slugify({text!r}) → {actual!r}, expected {expected!r}")
