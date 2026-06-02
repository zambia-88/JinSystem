<script setup lang="ts">
import { withBase } from "vitepress";
import postsData from "../posts.json";

type Post = {
  title: string;
  link: string;
  excerpt: string;
  category: string;
  date: string;
  cover: string;
};

const PILLAR_MAP: Record<string, string> = {
  格局提升: "财富认知",
  人性洞察: "财富认知",
  "AI 工具库": "AI 工作流",
  "Excel 技巧": "AI 工作流",
  "Word 技巧": "AI 工作流",
  "PPT 技巧": "AI 工作流",
};

const posts = postsData.posts as Post[];
const featured = posts.filter((p) => p.cover).slice(0, 6);

function postLink(link: string) {
  return withBase(link);
}

function coverStyle(post: Post) {
  if (!post.cover) return {};
  const src = post.cover.startsWith("http") ? post.cover : withBase(post.cover);
  return { backgroundImage: `url(${src})` };
}

function tag(post: Post) {
  return PILLAR_MAP[post.category] ?? post.category;
}
</script>

<template>
  <section v-if="featured.length" class="home-featured" aria-label="精选文章">
    <div class="home-section-head">
      <h2 class="home-section-title">精选文章</h2>
      <span class="home-section-sub">Featured</span>
    </div>
    <div class="home-featured-grid">
      <a
        v-for="post in featured"
        :key="post.link"
        :href="postLink(post.link)"
        class="home-featured-card"
      >
        <div class="home-featured-cover" :style="coverStyle(post)">
          <span class="home-featured-tag">{{ tag(post) }}</span>
        </div>
        <div class="home-featured-body">
          <h3>{{ post.title }}</h3>
          <p>{{ post.excerpt }}</p>
          <time v-if="post.date">{{ post.date }}</time>
        </div>
      </a>
    </div>
  </section>
</template>
