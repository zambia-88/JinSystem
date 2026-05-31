#!/usr/bin/env python3
"""将个人知识库 Excel 导出为 VitePress Markdown 文档（仅公开内容）。"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

try:
    import openpyxl
except ImportError:
    raise SystemExit("请先安装: pip install openpyxl")

ROOT = Path(__file__).resolve().parents[1]
EXCEL = ROOT.parent / "个人知识库2025-2035.xlsx"
DOCS = ROOT / "docs"

# 公开栏目：slug -> (sheet名, 中文标题, 描述)
PUBLIC_SHEETS: dict[str, tuple[str, str, str]] = {
    "cognition/mindset": ("格局提升", "格局提升", "修行、长期主义与内心秩序"),
    "cognition/insight": ("人性洞察", "人性洞察", "人际、职场与自我认知"),
    "tools/ai": ("人工智能", "AI 工具库", "实用 AI 工具与资源链接"),
    "tools/excel": ("Excel", "Excel 技巧", "表格处理与效率技巧"),
    "tools/word": ("Word", "Word 技巧", "文档排版与审阅技巧"),
    "tools/ppt": ("PPT", "PPT 技巧", "演示文稿制作与 AI 辅助"),
    "life/daily": ("日常生活", "日常生活", "居家、健康与生活窍门"),
    "life/travel": ("旅游", "旅游攻略", "路线规划与小众目的地"),
}

SKIP_TITLE_KEYWORDS = re.compile(
    r"wifi|密码|破解|regedit|WeChat|微信存储|netsh",
    re.IGNORECASE,
)


def slugify(text: str, index: int) -> str:
    text = (text or "").strip().split("\n")[0][:40]
    text = re.sub(r"[^\w\u4e00-\u9fff\-]", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return f"{index:03d}-{text}" if text else f"{index:03d}-entry"


def fmt_date(value) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    return str(value).split()[0]


def cell_str(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def is_valid_row(title: str, content: str) -> bool:
    if not title and not content:
        return False
    if title in ("序号", "主题/标题"):
        return False
    combined = f"{title} {content}"
    if SKIP_TITLE_KEYWORDS.search(combined):
        return False
    return bool(title or content)


def parse_sheet(ws) -> list[dict]:
    rows = list(ws.iter_rows(values_only=True))
    entries: list[dict] = []
    header_idx = None

    for i, row in enumerate(rows):
        cells = [cell_str(c) for c in row]
        if "主题/标题" in cells or "主题" in cells:
            header_idx = i
            break

    if header_idx is None:
        return entries

    header = [cell_str(c) for c in rows[header_idx]]
    col = {name: idx for idx, name in enumerate(header) if name}

    def get(row, *names: str) -> str:
        for name in names:
            if name in col and col[name] < len(row):
                v = cell_str(row[col[name]])
                if v:
                    return v
        return ""

    for row in rows[header_idx + 1 :]:
        cells = [cell_str(c) for c in row]
        if not any(cells):
            continue
        title = get(cells, "主题/标题", "主题")
        content = get(cells, "核心内容简述", "核心内容", "主要事件")
        if not is_valid_row(title, content):
            continue
        date_val = ""
        if "记录日期" in col and col["记录日期"] < len(row):
            date_val = fmt_date(row[col["记录日期"]])
        elif "时间" in col and col["时间"] < len(row):
            date_val = fmt_date(row[col["时间"]])
        entries.append(
            {
                "index": get(cells, "序号") or str(len(entries) + 1),
                "title": title or f"条目 {len(entries) + 1}",
                "content": content,
                "source": get(cells, "来源/出处", "来源"),
                "date": date_val,
                "reflection": get(cells, "个人感悟"),
                "note": get(cells, "说明"),
            }
        )
    return entries


def write_entry(path: Path, entry: dict, category: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        f'title: "{entry["title"].replace(chr(34), "'")}"',
        f"category: {category}",
    ]
    if entry["date"]:
        lines.append(f"date: {entry['date']}")
    if entry["source"]:
        lines.append(f'source: "{entry["source"].replace(chr(34), "'")}"')
    lines.extend(["---", "", f"# {entry['title']}", ""])
    if entry["content"]:
        lines.append(entry["content"])
        lines.append("")
    if entry["reflection"]:
        lines.append("## 个人感悟")
        lines.append("")
        lines.append(f"> {entry['reflection']}")
        lines.append("")
    if entry["source"]:
        src = entry["source"]
        if src.startswith("http"):
            lines.append(f"**来源：** [{src}]({src})")
        else:
            lines.append(f"**来源：** {src}")
        lines.append("")
    if entry["note"] and entry["note"] != entry["reflection"]:
        lines.append(f"*{entry['note']}*")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_index(path: Path, title: str, desc: str, items: list[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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
    path.write_text("\n".join(lines), encoding="utf-8")


def build_sidebar_manifest(categories: dict) -> None:
    manifest = {"generatedAt": datetime.now().isoformat(), "categories": categories}
    out = ROOT / "scripts" / "sidebar-data.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    if not EXCEL.exists():
        raise SystemExit(f"找不到 Excel: {EXCEL}")

    wb = openpyxl.load_workbook(EXCEL, read_only=True, data_only=True)
    stats: dict[str, int] = {}
    sidebar: dict = {}

    for slug, (sheet_name, cn_title, desc) in PUBLIC_SHEETS.items():
        if sheet_name not in wb.sheetnames:
            continue
        ws = wb[sheet_name]
        entries = parse_sheet(ws)
        cat_dir = DOCS / slug.replace("/", "/")
        items: list[tuple[str, str]] = []

        for i, entry in enumerate(entries, start=1):
            fname = slugify(entry["title"], i) + ".md"
            rel = f"/{slug}/{fname.replace('.md', '')}"
            write_entry(cat_dir / fname, entry, cn_title)
            items.append((entry["title"].split("\n")[0], rel))

        write_index(cat_dir / "index.md", cn_title, desc, items)
        stats[slug] = len(entries)
        sidebar[slug] = {"title": cn_title, "items": [{"text": t, "link": l} for t, l in items]}

    wb.close()
    build_sidebar_manifest(sidebar)

    # 首页
    total = sum(stats.values())
    index_lines = [
        "---",
        "layout: home",
        "title: JinSystem",
        "titleTemplate: 个人知识库",
        "",
        "hero:",
        "  name: JinSystem",
        '  text: "物质低配 · 认知高配 · 心态顶配"',
        "  tagline: 2025–2035 个人知识操作系统",
        "  actions:",
        "    - theme: brand",
        "      text: 进入格局提升",
        "      link: /cognition/mindset/",
        "    - theme: alt",
        "      text: AI 工具库",
        "      link: /tools/ai/",
        "",
        "features:",
        "  - icon: 🧭",
        "    title: 格局 · 认知",
        "    details: 长期主义、情绪管理与向内生长",
        "    link: /cognition/mindset/",
        "  - icon: 🛠",
        "    title: 工具箱",
        "    details: AI、Office 与效率技巧",
        "    link: /tools/ai/",
        "  - icon: 🌿",
        "    title: 生活 · 旅途",
        "    details: 日常窍门与小众旅行路线",
        "    link: /life/travel/",
        "---",
        "",
        "## 栏目概览",
        "",
    ]
    for slug, (_, cn_title, desc) in PUBLIC_SHEETS.items():
        count = stats.get(slug, 0)
        if count:
            index_lines.append(f"- **[{cn_title}](/{slug}/)** — {desc}（{count} 篇）")
    index_lines.extend(["", f"*共 {total} 篇公开内容，由 Excel 自动生成于 {datetime.now():%Y-%m-%d}*", ""])
    (DOCS / "index.md").write_text("\n".join(index_lines), encoding="utf-8")

    print("导出完成:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"  合计: {total}")


if __name__ == "__main__":
    main()
