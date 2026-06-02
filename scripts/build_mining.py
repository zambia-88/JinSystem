#!/usr/bin/env python3
"""将个人知识库矿业专题资料同步到 VitePress（复制媒体 + docx 转 Markdown）。"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT.parent
DOCS = ROOT / "source" / "docs"
MEDIA = DOCS / "public" / "media" / "mining"
MINING = DOCS / "mining"

KENYA_DOCX = Path(r"F:\我的桌面{F盘}\Kenya\肯尼亚矿业投资市场分析报告（整理版）.docx")
KENYA_PDF = KB / "肯尼亚矿业投资市场分析报告（整理版）.pdf"
ODI_DIR = KB / "企业境外投资流程"
ZAMBIA_DIR = KB / "赞比亚国情资料整理"

ZAMBIA_DOCX_SLUGS: dict[str, str] = {
    "1-基本国情篇.docx": "zh/01-basic-country",
    "2-贸易投资公司设立篇.docx": "zh/02-trade-investment",
    "3-财务税收篇.docx": "zh/03-finance-tax",
    "4-综合劳务篇.docx": "zh/04-labor",
    "5-工程土地篇.docx": "zh/05-engineering-land",
    "6-便民知识篇.docx": "zh/06-daily-guide",
    "赞比亚国情资料整理全篇.docx": "zh/00-full-collection",
    "赞比亚.docx": "zh/zambia-overview",
    "赞比亚重点投资领域整理.docx": "zh/key-sectors",
    "赞比亚重点熟知事项.docx": "zh/key-notes",
    "赞比亚矿产和矿业法.docx": "zh/mining-law-notes",
    "Lands Act赞比亚土地法.docx": "zh/land-law-notes",
    "The Mines and Minerals Act, 2015.docx": "zh/mines-act-2015",
    "The Mines and Minerals Act, 2015 (2).docx": "zh/mines-act-2015-alt",
    "Act No. 29 The Mines and Mineral Act, 2022.docx": "zh/mines-act-2022",
    "矿产开发部.docx": "zh/mining-dept",
    "赞比亚政府部门和相关机构一览表.docx": "zh/gov-agencies",
}

ODI_IMAGES = [
    ("企业境外投资备案相关政策.png", "备案相关政策"),
    ("企业境外直接投资（ODI）.png", "境外直接投资（ODI）"),
    ("国内公司实施路径.png", "国内公司实施路径"),
    ("境外投资办理所需资料.png", "办理所需资料"),
    ("境外投资办理时间和流程.png", "办理时间与流程"),
]


def esc_yaml(value: str) -> str:
    return value.replace('"', "'").replace("\n", " ")


def esc_md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def para_to_md(para: Paragraph) -> str:
    parts: list[str] = []
    for run in para.runs:
        text = run.text
        if not text:
            continue
        if run.bold and run.italic:
            parts.append(f"***{text}***")
        elif run.bold:
            parts.append(f"**{text}**")
        elif run.italic:
            parts.append(f"*{text}*")
        else:
            parts.append(text)
    return "".join(parts).strip()


def heading_level(style_name: str) -> int | None:
    if not style_name:
        return None
    if style_name.startswith("Heading"):
        try:
            return int(style_name.replace("Heading", "").strip())
        except ValueError:
            return 2
    if "标题" in style_name:
        m = re.search(r"(\d)", style_name)
        return int(m.group(1)) if m else 2
    return None


def table_to_md(table: Table) -> str:
    rows: list[list[str]] = []
    for row in table.rows:
        rows.append([esc_md_cell(cell.text.strip()) for cell in row.cells])
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    header = rows[0]
    body = rows[1:] if len(rows) > 1 else []
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def iter_block_items(doc: Document):
    body = doc.element.body
    for child in body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            yield ("p", Paragraph(child, doc))
        elif tag == "tbl":
            yield ("t", Table(child, doc))


def docx_to_markdown(docx_path: Path) -> str:
    doc = Document(docx_path)
    blocks: list[str] = []
    for kind, item in iter_block_items(doc):
        if kind == "p":
            text = para_to_md(item)
            if not text:
                blocks.append("")
                continue
            level = heading_level(item.style.name if item.style else "")
            if level:
                blocks.append("#" * min(level, 4) + " " + text)
            elif re.match(r"^[\d一二三四五六七八九十]+[、.)．]", text):
                blocks.append(f"- {text}")
            else:
                blocks.append(text)
        else:
            md = table_to_md(item)
            if md:
                blocks.append(md)
    content = "\n\n".join(blocks)
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content.strip() + "\n"


def write_md(path: Path, frontmatter: dict[str, str], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fm = "\n".join(f"{k}: {v}" for k, v in frontmatter.items())
    path.write_text(f"---\n{fm}\n---\n\n{body}", encoding="utf-8")


def copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def media_url(category: str, filename: str) -> str:
    from urllib.parse import quote
    return f"/media/mining/{category}/{quote(filename)}"


def build_kenya() -> None:
    if not KENYA_DOCX.exists():
        raise SystemExit(f"缺少肯尼亚 docx: {KENYA_DOCX}")
    if not KENYA_PDF.exists():
        raise SystemExit(f"缺少肯尼亚 PDF: {KENYA_PDF}")

    copy_file(KENYA_PDF, MEDIA / "kenya" / KENYA_PDF.name)
    body = docx_to_markdown(KENYA_DOCX)
    write_md(
        MINING / "kenya" / "report.md",
        {
            "title": "肯尼亚矿业投资市场分析报告",
            "description": "肯尼亚矿业投资市场分析 — 国家概况、矿业政策与投资环境。",
        },
        f"# 肯尼亚矿业投资市场分析报告\n\n"
        f'<div class="reading-prose">\n\n{body}\n\n</div>\n\n'
        f"---\n\n"
        f"[下载 PDF 版](/media/mining/kenya/{KENYA_PDF.name}){{ target=\"_blank\" }}\n",
    )
    write_md(
        MINING / "kenya" / "index.md",
        {
            "title": "肯尼亚矿业投资",
            "description": "肯尼亚矿业投资市场分析报告 — 东非矿业门户与投资环境研究。",
        },
        """# 肯尼亚矿业投资

> 东非重要矿业与贸易枢纽，铜、金、钛、宝石等资源禀赋突出。

## 专题说明

本专题发布 **《肯尼亚矿业投资市场分析报告（整理版）》**，涵盖国家与宏观背景、矿业法律框架、投资激励、重点矿种与区域、风险与合规要点等，供矿业出海研究参考。

::: tip 公开边界
本站仅发布整理版市场分析报告，不含实地坐标、探矿核实等内部敏感资料。
:::

## 阅读报告

[进入完整报告 →](/mining/kenya/report)

[下载 PDF](/media/mining/kenya/肯尼亚矿业投资市场分析报告（整理版）.pdf){ target="_blank" }

---

<p class="pillar-cta">
  <a href="/mining/">← 返回矿业研究</a>
</p>
""",
    )


def build_odi() -> None:
    if not ODI_DIR.exists():
        raise SystemExit(f"缺少 ODI 目录: {ODI_DIR}")

    images_md = []
    for filename, caption in ODI_IMAGES:
        src = ODI_DIR / filename
        if not src.exists():
            raise SystemExit(f"缺少 ODI 图片: {src}")
        copy_file(src, MEDIA / "odi" / filename)
        url = media_url("odi", filename)
        images_md.append(
            f"### {caption}\n\n"
            f"![{caption}]({url})\n"
        )

    pdf_name = "境外投资核准备案百问百答.pdf"
    pdf_src = ODI_DIR / pdf_name
    if not pdf_src.exists():
        raise SystemExit(f"缺少 ODI PDF: {pdf_src}")
    copy_file(pdf_src, MEDIA / "odi" / pdf_name)

    write_md(
        MINING / "odi" / "index.md",
        {
            "title": "企业境外投资流程",
            "description": "中国企业境外直接投资（ODI）备案流程、所需资料与政策要点。",
        },
        """# 企业境外投资流程 · ODI

> 中国企业「走出去」开展境外投资，须履行发改委、商务、外汇等部门规定的 **核准备案** 程序。本专题整理常用流程图与政策问答，便于项目前期合规梳理。

## 适用场景

- 境内企业赴境外新设、并购或增资 **非金融类** 投资项目
- 涉及 **敏感行业/敏感地区** 时，核准要求更严，须提前研判
- 与非洲矿业、资源类项目相关的 ODI，通常需同步关注 **行业主管部门** 与 **驻外使领馆** 要求

## 流程概览

下列五张流程图按 **政策框架 → ODI 定义 → 实施路径 → 材料清单 → 时间与步骤** 顺序排列，建议结合文末 PDF 问答一并阅读。

"""
        + "\n".join(images_md)
        + f"""

## 政策问答 PDF

[下载《境外投资核准备案百问百答》](/media/mining/odi/{pdf_name}){{ target="_blank" }}

::: info 说明
流程图与 PDF 来源于公开政策整理，具体以主管部门最新规定为准；涉及大额或敏感项目请咨询专业律师与顾问。
:::

---

<p class="pillar-cta">
  <a href="/mining/">← 返回矿业研究</a>
</p>
""",
    )


def build_zambia() -> None:
    if not ZAMBIA_DIR.exists():
        raise SystemExit(f"缺少赞比亚目录: {ZAMBIA_DIR}")

    zh_links: list[tuple[str, str]] = []
    pdf_items: list[tuple[str, str, str]] = []
    xlsx_items: list[tuple[str, str]] = []

    for src in sorted(ZAMBIA_DIR.iterdir()):
        if not src.is_file():
            continue
        name = src.name
        ext = src.suffix.lower()
        if ext == ".docx":
            slug = ZAMBIA_DOCX_SLUGS.get(name)
            if not slug:
                slug = "zh/" + re.sub(r"[^\w\u4e00-\u9fff\-]", "-", src.stem)
            title = src.stem
            md_path = MINING / "zambia" / f"{slug}.md"
            body = docx_to_markdown(src)
            write_md(
                md_path,
                {
                    "title": esc_yaml(title),
                    "description": esc_yaml(f"赞比亚国情资料 — {title}"),
                },
                f"# {title}\n\n<div class=\"reading-prose\">\n\n{body}\n\n</div>\n",
            )
            link = f"/mining/zambia/{slug.replace(chr(92), '/')}"
            zh_links.append((title, link))
        elif ext == ".pdf":
            copy_file(src, MEDIA / "zambia" / name)
            size_mb = src.stat().st_size / 1024 / 1024
            pdf_items.append((name, media_url("zambia", name), f"{size_mb:.1f} MB"))
        elif ext == ".xlsx":
            copy_file(src, MEDIA / "zambia" / name)
            xlsx_items.append((name, media_url("zambia", name)))

    zh_links.sort(key=lambda x: x[0])
    pdf_items.sort(key=lambda x: x[0])
    xlsx_items.sort(key=lambda x: x[0])

    zh_section = "\n".join(f"- [{t}]({l})" for t, l in zh_links)
    pdf_section = "\n".join(
        f"- [{n}]({u}){{ target=\"_blank\" }} · {s}" for n, u, s in pdf_items
    )
    xlsx_section = "\n".join(
        f"- [{n}]({u}){{ target=\"_blank\" }}" for n, u in xlsx_items
    )

    write_md(
        MINING / "zambia" / "index.md",
        {
            "title": "赞比亚国情资料",
            "description": "赞比亚投资、土地、矿业法规与国情整理 — 中文笔记与官方法规 PDF。",
        },
        f"""# 赞比亚国情资料

> 非洲重要产铜国，投资、土地与矿业法规体系完备。本专题收录中文整理稿与官方法规 PDF，供赴赞投资与矿业研究参考。

## 中文整理稿

{zh_section}

## 官方法规与指南（PDF 下载）

{pdf_section}

## 参考表格

{xlsx_section}

::: tip 大文件提示
部分 PDF 体积较大（如《赞比亚投资指南》），建议 Wi-Fi 环境下下载阅读。
:::

---

<p class="pillar-cta">
  <a href="/mining/">← 返回矿业研究</a>
</p>
""",
    )


def build_mining_index() -> None:
    write_md(
        MINING / "index.md",
        {
            "title": "矿业研究",
            "description": "JinSystem 矿业研究平台 — 非洲矿区、境外投资合规与行业洞察。",
        },
        """# 矿业研究 · Mining Research

> 深研行业本质，跟踪周期与供需，在不确定中寻找结构性机会。

JinSystem 矿业研究板块聚焦 **基础金属（尤其铜矿）** 与全球资源行业的长期研究，结合行业框架、区域资料与合规流程，形成可复用的认知体系。

## 专题资料

| 专题 | 内容 | 入口 |
|------|------|------|
| **肯尼亚矿业投资** | 市场分析报告（整理版） | [进入 →](/mining/kenya/) |
| **赞比亚国情资料** | 中文整理稿 + 官方法规 PDF（34 份） | [进入 →](/mining/zambia/) |
| **企业境外投资流程** | ODI 备案流程图 + 政策百问百答 | [进入 →](/mining/odi/) |

## 研究原则

1. **框架优先** — 法律、土地、税收与行业政策先厘清  
2. **周期思维** — 尊重大宗商品的长周期属性  
3. **长期跟踪** — 同一区域与主题持续迭代  
4. **公开边界** — 仅发布可公开分享的研究与整理资料  

## 相关阅读

- [财富成长](/investing/) — 从行业认知到资产配置  
- [格局提升](/cognition/mindset/) — 长期主义与元认知  

---

<p class="pillar-cta">
  <a href="/">← 返回首页</a> ·
  <a href="/investing/">财富成长框架 →</a>
</p>
""",
    )


def main() -> None:
    print("Building mining content...")
    build_kenya()
    print("  [ok] Kenya")
    build_odi()
    print("  [ok] ODI")
    build_zambia()
    print("  [ok] Zambia")
    build_mining_index()
    print("  [ok] Mining index")
    print("Done.")


if __name__ == "__main__":
    main()
