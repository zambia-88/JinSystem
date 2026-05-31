#!/usr/bin/env python3
"""从免费图库（Pixabay / Pexels）为文章批量下载封面图。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import quote

try:
    import requests
except ImportError:
    raise SystemExit("请先安装: pip install requests python-dotenv")

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
POSTS_JSON = DOCS / ".vitepress" / "posts.json"
COVERS_DIR = DOCS / "public" / "media" / "images" / "covers"
ENV_FILE = ROOT / ".env"

# 鎏金墨黑抽象 — 按分类匹配英文搜索词
CATEGORY_QUERIES: dict[str, str] = {
    "格局提升": "abstract dark gold black zen minimal texture",
    "人性洞察": "abstract dark mood silhouette minimal black gold",
    "AI 工具库": "abstract dark technology neural network minimal",
    "Excel 技巧": "abstract dark grid pattern minimal gold",
    "Word 技巧": "abstract dark paper ink minimal texture",
    "PPT 技巧": "abstract dark gradient presentation minimal",
    "日常生活": "abstract dark warm minimal lifestyle texture",
    "旅游攻略": "abstract dark landscape mood minimal horizon",
}
DEFAULT_QUERY = "abstract dark gold black minimal texture moody"

PEXELS_INTERVAL = 2.0  # 免费额度约 200/小时
PIXABAY_INTERVAL = 0.6


def load_env() -> None:
    if load_dotenv and ENV_FILE.exists():
        load_dotenv(ENV_FILE)


def link_to_md(link: str) -> Path:
    clean = link.strip("/")
    return DOCS / f"{clean}.md"


def link_to_filename(link: str) -> str:
    name = link.strip("/").replace("/", "-")
    name = re.sub(r"[^\w\u4e00-\u9fff\-]", "-", name)
    return re.sub(r"-+", "-", name).strip("-")


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


def update_md_cover(md_path: Path, cover_url: str) -> None:
    text = md_path.read_text(encoding="utf-8")
    fm, body = read_frontmatter(text)
    fm["cover"] = cover_url
    lines = ["---"]
    order = ["title", "category", "excerpt", "date", "source", "cover", "mediaType", "mediaUrl"]
    done = set()
    for key in order:
        if key in fm:
            val = fm[key]
            if key in ("title", "excerpt", "source", "cover", "mediaUrl"):
                lines.append(f'{key}: "{val}"')
            else:
                lines.append(f"{key}: {val}")
            done.add(key)
    for key, val in fm.items():
        if key not in done:
            lines.append(f'{key}: "{val}"' if " " in val else f"{key}: {val}")
    lines.append("---")
    md_path.write_text("\n".join(lines) + body, encoding="utf-8")


def search_query(post: dict) -> str:
    base = CATEGORY_QUERIES.get(post.get("category", ""), DEFAULT_QUERY)
    return base


def pick_page(seed: str, max_page: int = 15) -> int:
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    return (h % max_page) + 1


def fetch_pixabay(query: str, page: int, api_key: str) -> str | None:
    url = (
        "https://pixabay.com/api/"
        f"?key={api_key}&q={quote(query)}&image_type=photo"
        f"&orientation=horizontal&safesearch=true&per_page=3&page={page}"
    )
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    hits = r.json().get("hits", [])
    if not hits:
        return None
    idx = page % len(hits)
    return hits[idx].get("webformatURL") or hits[idx].get("largeImageURL")


def fetch_pexels(query: str, page: int, api_key: str) -> str | None:
    url = (
        "https://api.pexels.com/v1/search"
        f"?query={quote(query)}&orientation=landscape&per_page=1&page={page}"
    )
    headers = {"Authorization": api_key}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    photos = r.json().get("photos", [])
    if not photos:
        return None
    src = photos[0].get("src", {})
    return src.get("landscape") or src.get("large") or src.get("medium")


def download_image(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=60, stream=True)
    r.raise_for_status()
    dest.write_bytes(r.content)


def resolve_image(post: dict, pixabay_key: str, pexels_key: str) -> tuple[str | None, str]:
    query = search_query(post)
    page = pick_page(post["link"] + post["title"])
    source = ""

    if pixabay_key:
        try:
            url = fetch_pixabay(query, page, pixabay_key)
            if url:
                return url, "pixabay"
        except Exception as e:
            print(f"    Pixabay 失败: {e}")
        time.sleep(PIXABAY_INTERVAL)

    if pexels_key:
        try:
            url = fetch_pexels(query, page, pexels_key)
            if url:
                return url, "pexels"
        except Exception as e:
            print(f"    Pexels 失败: {e}")
        time.sleep(PEXELS_INTERVAL)

    # 降级：更通用的抽象词
    if pixabay_key:
        try:
            url = fetch_pixabay(DEFAULT_QUERY, page, pixabay_key)
            if url:
                return url, "pixabay(fallback)"
        except Exception:
            pass

    return None, ""


def main() -> None:
    import os

    parser = argparse.ArgumentParser(description="为 JinSystem 文章批量下载封面图")
    parser.add_argument("--force", action="store_true", help="覆盖已有封面")
    parser.add_argument("--limit", type=int, default=0, help="仅处理前 N 篇（测试用）")
    args = parser.parse_args()

    load_env()
    pixabay_key = os.environ.get("PIXABAY_API_KEY", "").strip()
    pexels_key = os.environ.get("PEXELS_API_KEY", "").strip()

    if not pixabay_key and not pexels_key:
        raise SystemExit(
            "请在 .env 中配置至少一个免费 API Key：\n"
            "  PIXABAY_API_KEY  → https://pixabay.com/api/docs/\n"
            "  PEXELS_API_KEY   → https://www.pexels.com/api/（可选备用）"
        )

    if not POSTS_JSON.exists():
        raise SystemExit("找不到 posts.json，请先运行: npm run sync")

    data = json.loads(POSTS_JSON.read_text(encoding="utf-8"))
    posts: list[dict] = data["posts"]

    todo = []
    for post in posts:
        md_path = link_to_md(post["link"])
        if not md_path.exists():
            continue
        fm, _ = read_frontmatter(md_path.read_text(encoding="utf-8"))
        has_cover = bool(fm.get("cover") or post.get("cover"))
        if has_cover and not args.force:
            continue
        todo.append(post)

    if args.limit:
        todo = todo[: args.limit]

    print(f"待处理: {len(todo)} 篇（共 {len(posts)} 篇）")
    if not todo:
        print("全部已有封面，使用 --force 可重新下载")
        return

    ok = skip = fail = 0

    for i, post in enumerate(todo, 1):
        title = post["title"][:30]
        md_path = link_to_md(post["link"])
        fname = link_to_filename(post["link"]) + ".jpg"
        dest = COVERS_DIR / fname
        cover_web = f"/media/images/covers/{fname}"

        print(f"[{i}/{len(todo)}] {title}…", end=" ", flush=True)

        if dest.exists() and not args.force:
            update_md_cover(md_path, cover_web)
            post["cover"] = cover_web
            print("已有文件，已关联")
            skip += 1
            continue

        img_url, src = resolve_image(post, pixabay_key, pexels_key)
        if not img_url:
            print("未找到图片")
            fail += 1
            continue

        try:
            download_image(img_url, dest)
            update_md_cover(md_path, cover_web)
            post["cover"] = cover_web
            print(f"OK ({src})")
            ok += 1
        except Exception as e:
            print(f"下载失败: {e}")
            fail += 1

    # 同步 posts.json
    for post in posts:
        md_path = link_to_md(post["link"])
        if md_path.exists():
            fm, _ = read_frontmatter(md_path.read_text(encoding="utf-8"))
            if fm.get("cover"):
                post["cover"] = fm["cover"]

    data["posts"] = posts
    POSTS_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"\n完成: 成功 {ok} · 跳过 {skip} · 失败 {fail}")
    print(f"封面目录: {COVERS_DIR}")
    print("下一步: git add . && git commit && git push")


if __name__ == "__main__":
    main()
