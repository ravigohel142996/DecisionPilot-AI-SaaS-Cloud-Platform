from pathlib import Path

MARKERS = ("<<<<<<<", "=======", ">>>>>>>")
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv"}


def has_marker(line: str) -> bool:
    return any(line.startswith(marker) for marker in MARKERS)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures: list[str] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for idx, line in enumerate(text.splitlines(), start=1):
            if has_marker(line):
                failures.append(f"{path.relative_to(root)}:{idx}: {line}")

    if failures:
        print("Found unresolved merge conflict markers:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("No merge conflict markers found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
