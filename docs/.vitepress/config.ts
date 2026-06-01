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

const miningSidebar = [
  { text: "矿业研究", link: "/mining/" },
  { text: "肯尼亚矿业报告", link: "/mining/kenya/" },
  { text: "赞比亚国情资料", link: "/mining/zambia/" },
  { text: "境外投资流程", link: "/mining/odi/" },
];

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

const SITE_DESC =
  "JinSystem · 个人品牌官网 · AI 知识库 · 矿业研究 · 财富成长社区。Think Deep. Act Long.";

export default defineConfig({
  lang: "zh-CN",
  title: "JinSystem",
  description: SITE_DESC,
  base: resolveBase(),
  appearance: { initialValue: "dark" },
  cleanUrls: true,
  lastUpdated: true,
  sitemap: {
    hostname: SITE_URL,
  },
  /** 本地 dev 首选 5201，避免与 stock-sentiment 等 Vite 默认 5173 冲突 */
  vite: {
    server: {
      port: 5201,
      strictPort: false,
    },
    preview: {
      port: 4201,
      strictPort: false,
    },
  },
  themeConfig: {
    nav: [
      { text: "首页", link: "/" },
      { text: "关于", link: "/about" },
      { text: "Now", link: "/now/" },
      { text: "矿业", link: "/mining/" },
      {
        text: "AI",
        items: [
          { text: "AI 工具库", link: "/tools/ai/" },
          { text: "资源中心", link: "/resources/" },
        ],
      },
      {
        text: "Investing",
        items: [
          { text: "财富认知", link: "/investing/" },
          { text: "格局提升", link: "/cognition/mindset/" },
          { text: "人性洞察", link: "/cognition/insight/" },
        ],
      },
      { text: "Growth", link: "/growth/" },
      { text: "社区", link: "/community/" },
    ],
    sidebar: {
      ...sidebar,
      "/mining/": miningSidebar,
      "/mining/kenya/": miningSidebar,
      "/mining/zambia/": miningSidebar,
      "/mining/odi/": miningSidebar,
    },
    footer: {
      message:
        "Think Deep. Act Long. · 2025–2035 · 物质低配 · 认知高配 · 心态顶配",
      copyright: "JinSystem · Knowledge · Wealth · Growth",
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
    [
      "meta",
      {
        name: "keywords",
        content:
          "JinSystem,个人品牌,AI知识库,矿业研究,铜矿,财富成长,投资认知,长期主义,Think Deep Act Long",
      },
    ],
    ["meta", { property: "og:type", content: "website" }],
    ["meta", { property: "og:site_name", content: "JinSystem" }],
    ["meta", { property: "og:title", content: "JinSystem | Think Deep. Act Long." }],
    ["meta", { property: "og:description", content: SITE_DESC }],
    ["meta", { property: "og:url", content: `${SITE_URL}/` }],
    ["meta", { property: "og:locale", content: "zh_CN" }],
    ["meta", { name: "twitter:card", content: "summary" }],
    ["meta", { name: "twitter:title", content: "JinSystem | Think Deep. Act Long." }],
    ["meta", { name: "twitter:description", content: SITE_DESC }],
    [
      "script",
      {
        type: "application/ld+json",
      },
      JSON.stringify({
        "@context": "https://schema.org",
        "@type": "WebSite",
        name: "JinSystem",
        url: SITE_URL,
        description: SITE_DESC,
        inLanguage: "zh-CN",
        publisher: {
          "@type": "Person",
          name: "JinSystem",
        },
      }),
    ],
    ["link", { rel: "preconnect", href: "https://api.open-meteo.com" }],
    ["link", { rel: "preconnect", href: "https://fonts.googleapis.com" }],
    ["link", { rel: "preconnect", href: "https://fonts.gstatic.com", crossorigin: "" }],
    [
      "link",
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap",
      },
    ],
  ],
});
