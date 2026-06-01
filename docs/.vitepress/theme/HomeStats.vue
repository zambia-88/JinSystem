<script setup lang="ts">
import postsData from "../posts.json";

const total = postsData.posts.length;
const aiCount = postsData.posts.filter((p) => p.category === "AI 工具库").length;
const mindsetCount = postsData.posts.filter(
  (p) => p.category === "格局提升" || p.category === "人性洞察"
).length;

const stats = [
  { value: `${total}+`, label: "知识条目", en: "Articles & Notes" },
  { value: `${mindsetCount}+`, label: "认知笔记", en: "Growth Notes" },
  { value: `${aiCount}+`, label: "AI 工具研究", en: "AI Research" },
  { value: "10+", label: "矿业项目实践", en: "Mining Projects" },
];
</script>

<template>
  <section class="home-stats" aria-label="数据概览">
    <div class="home-stats-grid">
      <div v-for="s in stats" :key="s.label" class="home-stat-card">
        <div class="home-stat-value">{{ s.value }}</div>
        <div class="home-stat-label">{{ s.label }}</div>
        <div class="home-stat-en">{{ s.en }}</div>
      </div>
    </div>
  </section>
</template>
