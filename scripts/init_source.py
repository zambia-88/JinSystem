#!/usr/bin/env python3
"""一次性：将当前 docs/ 复制到 source/docs/（全量私有内容库）。"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "docs"
DOCS = ROOT / "docs"

SKIP = {".vitepress/dist", ".vitepress/cache"}


def should_skip(path: Path) -> bool:
    parts = path.relative_to(DOCS).as_posix()
    for s in SKIP:
        if s in parts:
            return True
    return False


def main() -> None:
    if not DOCS.is_dir():
        raise SystemExit(f"找不到 docs: {DOCS}")
    if SOURCE.exists() and any(SOURCE.rglob("*.md")):
        print(f"source/docs 已存在且含 Markdown，跳过复制。")
        print(f"  路径: {SOURCE}")
        return

    SOURCE.mkdir(parents=True, exist_ok=True)
    copied = 0
    for src in DOCS.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(DOCS)
        if should_skip(src):
            continue
        dst = SOURCE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1

    print(f"已复制 {copied} 个文件到 source/docs/")
    print("下一步: python scripts/init_permissions.py")


if __name__ == "__main__":
    main()
    sys.exit(0)
