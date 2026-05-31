import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vitepress";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const sidebarFile = path.resolve(__dirname, "../../scripts/sidebar-data.json");

type SidebarItem = { text: string; link: string };
type SidebarCategory = { title: string; items: SidebarItem[] };

function loadSidebar(): Record<string, SidebarItem[]> {
  if (!fs.existsSync(sidebarFile)) return {};
  const raw = JSON.parse(fs.readFileSync(sidebarFile, "utf-8")) as {
    categories: Record<string, SidebarCategory>;
  };
  const sidebar: Record<string, SidebarItem[]> = {};
  for (const [slug, cat] of Object.entries(raw.categories)) {
    sidebar[`/${slug}/`] = [
      { text: cat.title, link: `/${slug}/` },
      ...cat.items,
    ];
  }
  return sidebar;
}

const sidebar = loadSidebar();

/** 站点部署在 GitHub Pages 项目路径 /JinSystem/ */
const SITE_BASE = "/JinSystem/";

function resolveBase(): string {
  if (process.env.VP_BASE_URL) {
    const base = process.env.VP_BASE_URL.trim();
    if (base === "/") return "/";
    return base.endsWith("/") ? base : `${base}/`;
  }
  const repo = process.env.GITHUB_REPOSITORY?.split("/")[1];
  if (repo && !repo.endsWith(".github.io")) {
    return `/${repo}/`;
  }
  if (process.env.GITHUB_ACTIONS === "true") {
    return SITE_BASE;
  }
  return "/";
}

export default defineConfig({
  lang: "zh-CN",
  title: "JinSystem",
  description: "JinSystem · 物质低配 · 认知高配 · 心态顶配",
  base: resolveBase(),
  appearance: "dark",
  cleanUrls: true,
  lastUpdated: true,
  themeConfig: {
    nav: [
      { text: "首页", link: "/" },
      {
        text: "认知",
        items: [
          { text: "格局提升", link: "/cognition/mindset/" },
          { text: "人性洞察", link: "/cognition/insight/" },
        ],
      },
      {
        text: "工具箱",
        items: [
          { text: "AI 工具库", link: "/tools/ai/" },
          { text: "Excel", link: "/tools/excel/" },
          { text: "Word", link: "/tools/word/" },
          { text: "PPT", link: "/tools/ppt/" },
        ],
      },
      {
        text: "生活",
        items: [
          { text: "日常生活", link: "/life/daily/" },
          { text: "旅游攻略", link: "/life/travel/" },
        ],
      },
      { text: "关于", link: "/about" },
    ],
    sidebar,
    socialLinks: [],
    footer: {
      message: "JinSystem · 2025–2035 · 物质低配 · 认知高配 · 心态顶配",
      copyright: "JinSystem",
    },
    search: {
      provider: "local",
    },
    outline: { level: [2, 3] },
  },
  head: [
    ["meta", { name: "theme-color", content: "#080809" }],
    ["link", { rel: "preconnect", href: "https://fonts.googleapis.com" }],
    ["link", { rel: "preconnect", href: "https://fonts.gstatic.com", crossorigin: "" }],
  ],
});
