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

/** 自定义域名 jinsystem.cn（根路径部署） */
const SITE_URL = "https://jinsystem.cn";

function resolveBase(): string {
  if (process.env.VP_BASE_URL) {
    const base = process.env.VP_BASE_URL.trim();
    if (base === "/") return "/";
    return base.endsWith("/") ? base : `${base}/`;
  }
  if (process.env.GITHUB_ACTIONS === "true") {
    return "/";
  }
  return "/";
}

export default defineConfig({
  lang: "zh-CN",
  title: "JinSystem",
  description: "JinSystem · 物质低配 · 认知高配 · 心态顶配",
  base: resolveBase(),
  appearance: { initialValue: "dark" },
  cleanUrls: true,
  lastUpdated: true,
  themeConfig: {
    nav: [
      { text: "首页", link: "/" },
      { text: "关于", link: "/about" },
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
    ],
    sidebar,
    socialLinks: [],
    footer: {
      message: "2025–2035 · 物质低配 · 认知高配 · 心态顶配",
      copyright: "JinSystem",
    },
    search: {
      provider: "local",
    },
    outline: { level: [2, 3] },
    darkModeSwitchLabel: "主题",
    lightModeSwitchTitle: "切换浅色模式",
    darkModeSwitchTitle: "切换深色模式",
    /** 页眉状态栏：默认武汉，浏览器定位成功则显示「本地」 */
    statusBar: {
      city: "武汉",
      latitude: 30.5928,
      longitude: 114.3055,
    },
  },
  head: [
    [
      "meta",
      {
        name: "viewport",
        content:
          "width=device-width, initial-scale=1.0, maximum-scale=5.0, viewport-fit=cover",
      },
    ],
    ["meta", { name: "theme-color", content: "#080809" }],
    ["meta", { name: "apple-mobile-web-app-capable", content: "yes" }],
    ["meta", { name: "format-detection", content: "telephone=no" }],
    ["link", { rel: "canonical", href: `${SITE_URL}/` }],
    ["link", { rel: "preconnect", href: "https://api.open-meteo.com" }],
    ["link", { rel: "preconnect", href: "https://fonts.googleapis.com" }],
    ["link", { rel: "preconnect", href: "https://fonts.gstatic.com", crossorigin: "" }],
  ],
});
