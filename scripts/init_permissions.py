#!/usr/bin/env python3
"""扫描 source/docs，生成 content-manifest.json 与 permissions.json。"""

from __future__ import annotations

import sys

from permissions_lib import (
    DEFAULTS,
    MANUAL_SECTIONS,
    content_type_for_path,
    ensure_permission_entry,
    iter_source_markdown,
    load_manifest,
    load_permissions,
    manifest_index,
    read_frontmatter,
    save_manifest,
    save_permissions,
    slug_from_path,
    upsert_manifest_entry,
)


def main() -> None:
    perms = load_permissions()
    perms.setdefault("version", 1)
    perms.setdefault("defaults", dict(DEFAULTS))

    manifest = load_manifest()
    idx = manifest_index(manifest)
    added_perm = 0
    added_manifest = 0

    for rel, path in iter_source_markdown():
        slug = slug_from_path(rel)
        fm, _ = read_frontmatter(path.read_text(encoding="utf-8"))
        title = fm.get("title", slug)
        category = fm.get("category", "")

        if rel in MANUAL_SECTIONS:
            title, category = MANUAL_SECTIONS[rel]
            ctype = "manual"
        else:
            ctype = content_type_for_path(rel)

        before = slug in idx
        upsert_manifest_entry(manifest, slug, title, category, ctype, rel)
        if not before:
            added_manifest += 1
            idx = manifest_index(manifest)

        before_p = slug in perms.get("entries", {})
        ensure_permission_entry(perms, slug, ctype)
        if not before_p:
            added_perm += 1

    # 已有线上内容：首次初始化时全部设为公开，避免站点突然清空
    if not perms.get("updatedAt"):
        for e in manifest.get("entries", []):
            perms["entries"][e["slug"]] = True
        print("首次初始化：已将现有内容全部标记为「公开」（之后新 Excel 条目默认非公开）。")

    save_manifest(manifest)
    save_permissions(perms)
    print(f"manifest: {len(manifest.get('entries', []))} 条（新增 {added_manifest}）")
    print(f"permissions: {len(perms.get('entries', {}))} 条（新增 {added_perm}）")
    print("下一步: python scripts/build_public.py")


if __name__ == "__main__":
    main()
    sys.exit(0)
