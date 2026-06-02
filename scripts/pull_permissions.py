#!/usr/bin/env python3
"""从私有仓库拉取 permissions.json（Web Admin 为唯一权威）。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PERMISSIONS_FILE = ROOT / "permissions.json"
REMOTE = "private"
BRANCH = "main"


def pull() -> bool:
    try:
        subprocess.run(
            ["git", "fetch", REMOTE, BRANCH],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"  无法 fetch {REMOTE}: {e.stderr or e}")
        return False

    try:
        data = subprocess.check_output(
            ["git", "show", f"{REMOTE}/{BRANCH}:permissions.json"],
            cwd=ROOT,
        )
    except subprocess.CalledProcessError:
        print("  私有库尚无 permissions.json，跳过拉取")
        return False

    PERMISSIONS_FILE.write_bytes(data)
    print(f"  已拉取 permissions.json <- {REMOTE}/{BRANCH}")
    return True


def main() -> None:
    ok = pull()
    sys.exit(0 if ok or PERMISSIONS_FILE.exists() else 1)


if __name__ == "__main__":
    main()
