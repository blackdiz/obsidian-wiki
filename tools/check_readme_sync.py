from __future__ import annotations

import sys
from typing import Iterable, Optional


PAIRED_READMES = frozenset({"README.md", "README_TW.md"})


def validation_error(changed_paths: Iterable[str]) -> Optional[str]:
    normalized_paths = {
        path[2:] if path.startswith("./") else path
        for path in changed_paths
        if path
    }
    changed_readmes = normalized_paths & PAIRED_READMES

    if changed_readmes == {"README.md"}:
        return (
            "README.md changed without README_TW.md. "
            "Update both files in the same change set."
        )
    if changed_readmes == {"README_TW.md"}:
        return (
            "README_TW.md changed without README.md. "
            "Update both files in the same change set."
        )
    return None


def main() -> int:
    error = validation_error(sys.stdin.read().splitlines())
    if error is not None:
        print(f"README sync check failed: {error}", file=sys.stderr)
        return 1

    print("README sync check passed: both README files changed or neither changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
