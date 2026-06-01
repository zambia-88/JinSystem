<script setup lang="ts">
import { withBase } from "vitepress";

const pillars = [
  {
    title: "矿业投资",
    en: "Mining",
    desc: "赞比亚矿业项目实践、矿权研究、矿业政策分析",
    link: "/mining/",
    icon: "◆",
  },
  {
    title: "AI 工作流",
    en: "AI Workflow",
    desc: "ChatGPT、Claude、Gemini、Cursor 等工具实战应用",
    link: "/tools/ai/",
    icon: "◇",
  },
  {
    title: "财富认知",
    en: "Investing",
    desc: "投资研究、商业思维、财富增长逻辑",
    link: "/investing/",
    icon: "◎",
  },
  {
    title: "长期主义",
    en: "Growth",
    desc: "个人成长、执行力建设、认知升级",
    link: "/growth/",
    icon: "◈",
  },
];
</script>

<template>
  <section class="home-pillars" aria-label="核心专题">
    <div class="home-pillars-inner">
      <div class="home-section-head home-section-head--inset">
        <h2 class="home-section-title">核心专题</h2>
        <span class="home-section-sub">Topics</span>
      </div>
      <div class="pillar-grid">
        <a
          v-for="p in pillars"
          :key="p.link"
          :href="withBase(p.link)"
          class="pillar-card"
        >
          <span class="pillar-icon" aria-hidden="true">{{ p.icon }}</span>
          <div class="pillar-body">
            <h3 class="pillar-title">{{ p.title }}</h3>
            <span class="pillar-en">{{ p.en }}</span>
            <p class="pillar-desc">{{ p.desc }}</p>
          </div>
          <span class="pillar-arrow" aria-hidden="true">→</span>
        </a>
      </div>
    </div>
  </section>
</template>
