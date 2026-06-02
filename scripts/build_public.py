#!/usr/bin/env python3
"""按 permissions.json 从 source/docs 生成公开 docs/（仅含 public=true）。"""

from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

from permissions_lib import (
    PUBLIC_DOCS,
    POSTS_JSON,
    SOURCE_DOCS,
    content_type_for_path,
    is_public,
    iter_source_markdown,
    load_manifest,
    load_permissions,
    manifest_index,
    read_frontmatter,
    slug_from_path,
)

ROOT = Path(__file__).resolve().parents[1]
SIDEBAR_JSON = ROOT / "scripts" / "sidebar-data.json"

# 始终保留的静态资源（不含私密正文）
ALWAYS_COPY_PREFIXES = ("public/",)

# 这些 slug 即使 permissions 关闭也保留（站点骨架）；可在 Web 关闭单篇
SITE_CORE = {"/", "/about", "/community"}


def make_excerpt(text: str, max_len: int = 120) -> str:
    t = re.sub(r"\s+", " ", (text or "")).strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"


def write_category_index(
    cat_dir: Path, title: str, desc: str, items: list[tuple[str, str]]
) -> None:
    lines = [
        "---",
        f"title: {title}",
        "---",
        "",
        f"# {title}",
        "",
        desc,
        "",
    ]
    for name, link in items:
        lines.append(f"- [{name}]({link})")
    lines.append("")
    cat_dir.mkdir(parents=True, exist_ok=True)
    (cat_dir / "index.md").write_text("\n".join(lines), encoding="utf-8")


def remove_stale_public_md(keep_rel: set[str]) -> int:
    removed = 0
    if not PUBLIC_DOCS.is_dir():
        return removed
    for md in PUBLIC_DOCS.rglob("*.md"):
        rel = md.relative_to(PUBLIC_DOCS).as_posix()
        if rel.startswith(".vitepress"):
            continue
        if rel not in keep_rel:
            md.unlink()
            print(f"  移除非公开: docs/{rel}")
            removed += 1
    return removed


def copy_public_file(rel: str, src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def rebuild_sidebar_and_posts(
    public_articles: list[dict], sidebar_categories: dict[str, dict]
) -> None:
    SIDEBAR_JSON.write_text(
        json.dumps(
            {"generatedAt": datetime.now().isoformat(), "categories": sidebar_categories},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    def sort_key(p: dict) -> str:
        return p.get("date") or "0000-00-00"

    public_articles.sort(key=sort_key, reverse=True)
    POSTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    POSTS_JSON.write_text(
        json.dumps(
            {"generatedAt": datetime.now().isoformat(), "posts": public_articles},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> None:
    if not SOURCE_DOCS.is_dir():
        raise SystemExit(
            f"找不到 source/docs。请先运行: python scripts/init_source.py"
        )

    perms = load_permissions()
    manifest = load_manifest()
    midx = manifest_index(manifest)

    keep_rel: set[str] = set()
    public_articles: list[dict] = []
    sidebar_categories: dict[str, dict] = {}

    # 静态资源
    public_media = SOURCE_DOCS / "public"
    if public_media.is_dir():
        dst_media = PUBLIC_DOCS / "public"
        if dst_media.exists():
            shutil.rmtree(dst_media)
        shutil.copytree(public_media, dst_media)
        print(f"  同步媒体: source/docs/public -> docs/public")

    for rel, src in iter_source_markdown():
        if rel.startswith("public/"):
            continue
        slug = slug_from_path(rel)
        entry = midx.get(slug)
        public = is_public(slug, perms, entry)
        if slug in SITE_CORE:
            public = True
        if not public:
            continue

        dst = PUBLIC_DOCS / rel
        copy_public_file(rel, src, dst)
        keep_rel.add(rel)

        fm, body = read_frontmatter(src.read_text(encoding="utf-8"))
        ctype = entry.get("type") if entry else content_type_for_path(rel)
        if ctype != "excel" or rel.endswith("/index.md"):
            continue

        # Excel 文章 -> posts + sidebar
        category = fm.get("category", entry.get("category", "") if entry else "")
        link = slug if slug.startswith("/") else f"/{slug}"
        title = fm.get("title", entry.get("title", slug) if entry else slug)
        public_articles.append(
            {
                "title": title,
                "link": link,
                "excerpt": fm.get("excerpt") or make_excerpt(body),
                "category": category,
                "date": fm.get("date", ""),
                "cover": fm.get("cover", ""),
                "mediaType": fm.get("mediaType", ""),
                "mediaUrl": fm.get("mediaUrl", ""),
            }
        )

        # sidebar slug key: /cognition/mindset/
        parts = slug.strip("/").split("/")
        if len(parts) >= 2:
            cat_key = "/".join(parts[:2])
        else:
            cat_key = parts[0]
        cat_slug = f"/{cat_key}/"
        if cat_slug not in sidebar_categories:
            sidebar_categories[cat_slug] = {"title": category, "items": []}
        sidebar_categories[cat_slug]["items"].append({"text": title, "link": link})

    removed = remove_stale_public_md(keep_rel)

    # 按 Excel 栏目重写 index.md（仅公开条目）
    CAT_META = {
        "cognition/mindset": ("格局提升", "修行、长期主义与内心秩序"),
        "cognition/insight": ("人性洞察", "人际、职场与自我认知"),
        "tools/ai": ("AI 工具库", "实用 AI 工具与资源链接"),
        "tools/excel": ("Excel 技巧", "表格处理与效率技巧"),
        "tools/word": ("Word 技巧", "文档排版与审阅技巧"),
        "tools/ppt": ("PPT 技巧", "演示文稿制作与 AI 辅助"),
        "life/daily": ("日常生活", "居家、健康与生活窍门"),
        "life/travel": ("旅游攻略", "路线规划与小众目的地"),
    }

    for cat_key, (cn_title, desc) in CAT_META.items():
        cat_slug = f"/{cat_key}/"
        items_data = sidebar_categories.get(cat_slug, {}).get("items", [])
        items = [(i["text"], i["link"]) for i in items_data]
        write_category_index(PUBLIC_DOCS / cat_key, cn_title, desc, items)
        keep_rel.add(f"{cat_key}/index.md")

    rebuild_sidebar_and_posts(public_articles, sidebar_categories)

    print("公开构建完成:")
    print(f"  公开 Markdown: {len(keep_rel)} 个")
    print(f"  移除非公开: {removed} 个")
    print(f"  posts.json: {len(public_articles)} 条")
    print(f"  sidebar 栏目: {len(sidebar_categories)}")


if __name__ == "__main__":
    main()
    sys.exit(0)
