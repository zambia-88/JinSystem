#!/usr/bin/env python3
"""权限与内容清单：公开 / 非公开（Web 开关为唯一权威）。"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DOCS = ROOT / "source" / "docs"
PUBLIC_DOCS = ROOT / "docs"
PERMISSIONS_FILE = ROOT / "permissions.json"
MANIFEST_FILE = ROOT / "content-manifest.json"
POSTS_JSON = PUBLIC_DOCS / ".vitepress" / "posts.json"

# 7b：Excel 新条目默认非公开；8b：手工页默认公开
DEFAULTS = {"excel": False, "manual": True}

# 手工栏目（非 Excel 同步），8b 默认公开
MANUAL_SECTIONS = {
    "about.md": ("关于", "站点"),
    "index.md": ("首页", "站点"),
    "now/index.md": ("Now", "站点"),
    "growth/index.md": ("Growth", "站点"),
    "investing/index.md": ("Investing", "财富"),
    "resources/index.md": ("资源中心", "AI 知识库"),
    "community/index.md": ("社区", "站点"),
    "mining/index.md": ("矿业研究", "矿业"),
    "mining/kenya/index.md": ("肯尼亚矿业报告", "矿业"),
    "mining/zambia/index.md": ("赞比亚国情资料", "矿业"),
    "mining/odi/index.md": ("境外投资流程", "矿业"),
}

EXCEL_SLUG_PREFIXES = (
    "cognition/mindset",
    "cognition/insight",
    "tools/ai",
    "tools/excel",
    "tools/word",
    "tools/ppt",
    "life/daily",
    "life/travel",
)


def slug_from_path(rel_path: str) -> str:
    """life/daily/060-foo.md -> /life/daily/060-foo"""
    p = rel_path.replace("\\", "/")
    if p.endswith(".md"):
        p = p[:-3]
    if p.endswith("/index"):
        p = p[: -len("/index")]
    return f"/{p}" if p else "/"


def path_from_slug(slug: str) -> Path:
    s = slug.strip("/")
    if not s:
        return SOURCE_DOCS / "index.md"
    candidate = SOURCE_DOCS / f"{s}.md"
    if candidate.exists():
        return candidate
    return SOURCE_DOCS / s / "index.md"


def content_type_for_path(rel: str) -> str:
    rel = rel.replace("\\", "/")
    for prefix in EXCEL_SLUG_PREFIXES:
        if rel.startswith(prefix + "/") or rel == prefix + "/index.md":
            if rel.endswith("/index.md"):
                return "manual"
            return "excel"
    return "manual"


def load_permissions() -> dict[str, Any]:
    if not PERMISSIONS_FILE.exists():
        return {
            "version": 1,
            "updatedAt": None,
            "defaults": dict(DEFAULTS),
            "entries": {},
        }
    data = json.loads(PERMISSIONS_FILE.read_text(encoding="utf-8"))
    data.setdefault("defaults", dict(DEFAULTS))
    data.setdefault("entries", {})
    return data


def save_permissions(data: dict[str, Any]) -> None:
    data["updatedAt"] = datetime.now().isoformat()
    PERMISSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PERMISSIONS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_FILE.exists():
        return {"generatedAt": None, "entries": []}
    return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))


def save_manifest(data: dict[str, Any]) -> None:
    data["generatedAt"] = datetime.now().isoformat()
    MANIFEST_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def normalize_slug(slug: str) -> str:
    s = (slug or "").strip()
    if not s or s == "/":
        return "/"
    if not s.startswith("/"):
        s = f"/{s}"
    return s.rstrip("/") if s != "/" else s


def is_public(slug: str, perms: dict[str, Any], manifest_entry: dict | None) -> bool:
    slug = normalize_slug(slug)
    entries = perms.get("entries", {})

    # 父路径任一显式设为 false → 整棵子树非公开
    parts = [p for p in slug.strip("/").split("/") if p]
    for i in range(len(parts)):
        prefix = f"/{'/'.join(parts[: i + 1])}"
        if prefix in entries and entries[prefix] is False:
            return False
    if slug in entries:
        return bool(entries[slug])

    defaults = perms.get("defaults", DEFAULTS)
    if manifest_entry:
        ctype = manifest_entry.get("type", "manual")
    else:
        rel = slug.strip("/") + ".md"
        ctype = content_type_for_path(rel)
    return bool(defaults.get(ctype, defaults.get("manual", True)))


def read_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, parts[2]


def iter_source_markdown() -> list[tuple[str, Path]]:
    if not SOURCE_DOCS.is_dir():
        return []
    out: list[tuple[str, Path]] = []
    for md in SOURCE_DOCS.rglob("*.md"):
        rel = md.relative_to(SOURCE_DOCS).as_posix()
        if rel.startswith(".vitepress"):
            continue
        out.append((rel, md))
    return sorted(out, key=lambda x: x[0])


def manifest_index(manifest: dict[str, Any]) -> dict[str, dict]:
    return {e["slug"]: e for e in manifest.get("entries", [])}


def upsert_manifest_entry(
    manifest: dict[str, Any], slug: str, title: str, category: str, ctype: str, source_path: str
) -> None:
    entries = manifest.setdefault("entries", [])
    idx = manifest_index(manifest)
    if slug in idx:
        e = idx[slug]
        e["title"] = title or e.get("title", slug)
        e["category"] = category or e.get("category", "")
        e["type"] = ctype
        e["sourcePath"] = source_path
        return
    entries.append(
        {
            "slug": slug,
            "title": title or slug,
            "category": category,
            "type": ctype,
            "sourcePath": source_path,
        }
    )


def ensure_permission_entry(
    perms: dict[str, Any], slug: str, ctype: str, explicit: bool | None = None
) -> None:
    entries = perms.setdefault("entries", {})
    if slug in entries:
        return
    if explicit is not None:
        entries[slug] = explicit
        return
    defaults = perms.get("defaults", DEFAULTS)
    entries[slug] = bool(defaults.get(ctype, True))
