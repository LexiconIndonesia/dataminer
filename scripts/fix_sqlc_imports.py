#!/usr/bin/env python3
"""Fix SQLC-generated import paths.

SQLC generates relative imports like 'from queries import models'
which should be 'from dataminer.db.queries import models'.
"""

import re
from pathlib import Path


def fix_sqlc_imports(queries_dir: Path) -> None:
    """Fix import statements in SQLC-generated files."""
    pattern = re.compile(r"^from queries import models$", re.MULTILINE)
    replacement = "from dataminer.db.queries import models"

    fixed_count = 0
    for file_path in queries_dir.glob("*.py"):
        if file_path.name == "__init__.py":
            continue

        content = file_path.read_text()
        if pattern.search(content):
            new_content = pattern.sub(replacement, content)
            file_path.write_text(new_content)
            fixed_count += 1
            print(f"✓ Fixed imports in {file_path.name}")

    if fixed_count == 0:
        print("✓ No import fixes needed")
    else:
        print(f"✓ Fixed imports in {fixed_count} file(s)")


if __name__ == "__main__":
    queries_dir = Path(__file__).parents[1] / "src" / "dataminer" / "db" / "queries"
    fix_sqlc_imports(queries_dir)
