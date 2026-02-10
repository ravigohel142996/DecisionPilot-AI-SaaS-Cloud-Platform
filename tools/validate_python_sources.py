"""Repository-wide Python validation.

Checks all tracked Python files for syntax errors and accidental standalone branch-label lines
that sometimes get pasted during conflict resolution.
"""

from __future__ import annotations

import py_compile
import re
import subprocess
from pathlib import Path

BRANCH_LABEL_RE = re.compile(r"^(codex/[\w.-]+|main)$")


def tracked_python_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "*.py"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    files = [root / line.strip() for line in result.stdout.splitlines() if line.strip()]
    return [path for path in files if path.exists()]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures: list[str] = []

    for file_path in tracked_python_files(root):
        relative = file_path.relative_to(root)

        source = file_path.read_text(encoding="utf-8")
        for idx, line in enumerate(source.splitlines(), start=1):
            if BRANCH_LABEL_RE.match(line.strip()):
                failures.append(f"{relative}:{idx}: suspicious standalone branch label: {line.strip()}")

        try:
            py_compile.compile(str(file_path), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append(f"{relative}: syntax error: {exc.msg}")

    if failures:
        print("Python source validation failed:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("Python source validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
