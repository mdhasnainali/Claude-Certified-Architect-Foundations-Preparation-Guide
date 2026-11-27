# 2_5_explore.py — part 1: Glob, Grep and wrapper tracing on a tiny fake repo. Python 3.13+, offline.
import pathlib, re, tempfile

root = pathlib.Path(tempfile.mkdtemp())
for name, text in {
    "src/billing/refund.py": "def issue_refund(order, amount):\n    return gateway.pay(-amount)\n",
    "src/billing/__init__.py": "from .refund import issue_refund as refund_order\n",
    "src/api/routes.py": "from billing import refund_order\n\ndef post_refund(req):\n    return refund_order(req.order, req.amount)\n",
    "src/api/routes.test.py": "def test_post_refund():\n    assert True\n",
    "src/jobs/nightly.py": "from billing.refund import issue_refund\nissue_refund(o, 5)\nissue_refund(o, 7)\n",
}.items():
    (root / name).parent.mkdir(parents=True, exist_ok=True)
    (root / name).write_text(text)

glob = lambda pattern: sorted(
    str(p.relative_to(root)) for p in root.glob(pattern)
)  # names
grep = lambda rx: sorted(
    {
        str(p.relative_to(root))
        for p in root.rglob("*.py")
        if re.search(rx, p.read_text())
    }
)  # contents

print("Glob **/*.test.py   →", glob("**/*.test.py"))
print("Grep issue_refund\\( →", grep(r"issue_refund\("))
aliases = re.findall(
    r"issue_refund as (\w+)", (root / "src/billing/__init__.py").read_text()
)
print("Wrapper exports     →", aliases, "| Grep each:", grep(rf"{aliases[0]}\("))


# 2_5_explore.py — part 2: Edit's "exact and unique" rule
def edit(path: str, old: str, new: str) -> None:
    text = (root / path).read_text()
    if (n := text.count(old)) != 1:
        raise ValueError(f"{n} matches for {old!r}: add more context, or Read + Write")
    (root / path).write_text(text.replace(old, new))


try:
    edit("src/jobs/nightly.py", "issue_refund(o, ", "issue_refund(order=o, amount=")
except ValueError as e:
    print("Edit                →", e)
edit("src/jobs/nightly.py", "issue_refund(o, 7)", "issue_refund(o, 8)")
print("Edit with context   → ok")
