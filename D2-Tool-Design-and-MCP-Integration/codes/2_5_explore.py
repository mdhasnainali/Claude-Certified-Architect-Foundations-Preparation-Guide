# 2_5_explore.py — part 1: Glob, Grep and wrapper tracing on a tiny fake repo. Python 3.13+, offline.
import pathlib, re, tempfile

repo_root = pathlib.Path(tempfile.mkdtemp())
for relative_path, content in {
    "src/billing/refund.py": "def issue_refund(order, amount):\n    return gateway.pay(-amount)\n",
    "src/billing/__init__.py": "from .refund import issue_refund as refund_order\n",
    "src/api/routes.py": "from billing import refund_order\n\ndef post_refund(req):\n    return refund_order(req.order, req.amount)\n",
    "src/api/routes.test.py": "def test_post_refund():\n    assert True\n",
    "src/jobs/nightly.py": "from billing.refund import issue_refund\nissue_refund(o, 5)\nissue_refund(o, 7)\n",
}.items():
    (repo_root / relative_path).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / relative_path).write_text(content)


def glob_files(pattern: str) -> list[str]:  # matches file NAMES
    return sorted(str(path.relative_to(repo_root)) for path in repo_root.glob(pattern))


def grep_files(regex: str) -> list[str]:  # matches file CONTENTS
    return sorted(
        str(path.relative_to(repo_root))
        for path in repo_root.rglob("*.py")
        if re.search(regex, path.read_text())
    )


print("Glob **/*.test.py   →", glob_files("**/*.test.py"))
print("Grep issue_refund\\( →", grep_files(r"issue_refund\("))
aliases = re.findall(
    r"issue_refund as (\w+)", (repo_root / "src/billing/__init__.py").read_text()
)
print("Wrapper exports     →", aliases, "| Grep each:", grep_files(rf"{aliases[0]}\("))


# 2_5_explore.py — part 2: Edit's "exact and unique" rule
def edit_file(path: str, old_text: str, new_text: str) -> None:
    content = (repo_root / path).read_text()
    if (match_count := content.count(old_text)) != 1:
        raise ValueError(
            f"{match_count} matches for {old_text!r}: add more context, or Read + Write"
        )
    (repo_root / path).write_text(content.replace(old_text, new_text))


try:
    edit_file(
        "src/jobs/nightly.py", "issue_refund(o, ", "issue_refund(order=o, amount="
    )
except ValueError as error:
    print("Edit                →", error)
edit_file("src/jobs/nightly.py", "issue_refund(o, 7)", "issue_refund(o, 8)")
print("Edit with context   → ok")
