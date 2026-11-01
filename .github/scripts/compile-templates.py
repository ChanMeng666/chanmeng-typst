#!/usr/bin/env python3
"""Compile every Typst block in references/typst-templates.md.

Templates are copied verbatim by users, so a broken one is a broken product.
The other references hold fragments that are not meant to compile alone.
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

TEMPLATES = Path("skills/chanmeng-typst/references/typst-templates.md")
BIB_STUB = """@article{example2024,
  title = {Example Article},
  author = {Doe, Jane},
  year = {2024},
  journal = {Example Journal},
}
"""


def main():
    blocks = re.findall(r"```typst\n(.*?)^```", TEMPLATES.read_text(encoding="utf-8"), re.S | re.M)
    if not blocks:
        sys.exit(f"no Typst blocks found in {TEMPLATES}")

    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "refs.bib").write_text(BIB_STUB, encoding="utf-8")
        for index, block in enumerate(blocks, 1):
            source = Path(tmp) / f"template-{index}.typ"
            source.write_text(block, encoding="utf-8")
            result = subprocess.run(
                ["typst", "compile", str(source)],
                capture_output=True, text=True, encoding="utf-8",
            )
            first_line = block.strip().splitlines()[0][:60]
            if result.returncode:
                failed += 1
                print(f"FAIL template {index} ({first_line})\n{result.stderr}")
            else:
                print(f"ok   template {index} ({first_line})")

    print(f"{len(blocks) - failed}/{len(blocks)} templates compiled")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
