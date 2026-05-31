<script setup lang="ts">
import { ref, computed } from "vue";
import { withBase } from "vitepress";
import postsData from "../posts.json";

type Post = {
  title: string;
  link: string;
  excerpt: string;
  category: string;
  date: string;
  cover: string;
  mediaType: string;
  mediaUrl: string;
};

const PAGE_SIZE = 12;
const posts = postsData.posts as Post[];

const currentPage = ref(1);
const activeCategory = ref("全部");

const categories = computed(() => {
  const set = new Set(posts.map((p) => p.category));
  return ["全部", ...Array.from(set)];
});

const filtered = computed(() => {
  if (activeCategory.value === "全部") return posts;
  return posts.filter((p) => p.category === activeCategory.value);
});

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filtered.value.length / PAGE_SIZE))
);

const paged = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE;
  return filtered.value.slice(start, start + PAGE_SIZE);
});

function selectCategory(cat: string) {
  activeCategory.value = cat;
  currentPage.value = 1;
}

function prevPage() {
  if (currentPage.value > 1) currentPage.value--;
}

function nextPage() {
  if (currentPage.value < totalPages.value) currentPage.value++;
}

function postLink(link: string) {
  return withBase(link.endsWith("/") ? link : `${link}/`);
}

function coverStyle(post: Post) {
  if (post.cover) {
    const src = post.cover.startsWith("http")
      ? post.cover
      : withBase(post.cover);
    return { backgroundImage: `url(${src})` };
  }
  return { backgroundImage: categoryGradient(post.category) };
}

function categoryGradient(category: string) {
  const map: Record<string, string> = {
    格局提升: "linear-gradient(135deg, #1a1a2e 0%, #4a3728 100%)",
    人性洞察: "linear-gradient(135deg, #1c2620 0%, #3d5a4a 100%)",
    AI工具库: "linear-gradient(135deg, #1a2030 0%, #2a3a5a 100%)",
    "AI 工具库": "linear-gradient(135deg, #1a2030 0%, #2a3a5a 100%)",
    Excel技巧: "linear-gradient(135deg, #1f1a28 0%, #3a3050 100%)",
    "Excel 技巧": "linear-gradient(135deg, #1f1a28 0%, #3a3050 100%)",
    Word技巧: "linear-gradient(135deg, #201a1a 0%, #4a3535 100%)",
    "Word 技巧": "linear-gradient(135deg, #201a1a 0%, #4a3535 100%)",
    PPT技巧: "linear-gradient(135deg, #1a2020 0%, #354848 100%)",
    "PPT 技巧": "linear-gradient(135deg, #1a2020 0%, #354848 100%)",
    日常生活: "linear-gradient(135deg, #1a2218 0%, #3a4a30 100%)",
    旅游攻略: "linear-gradient(135deg, #1a1820 0%, #403050 100%)",
  };
  return map[category] || "linear-gradient(135deg, #141414 0%, #2a2a2a 100%)";
}

function mediaIcon(post: Post) {
  if (post.mediaType === "video") return "▶";
  if (post.mediaType === "audio") return "♫";
  if (post.cover || post.mediaType === "image") return "◉";
  return "";
}
</script>

<template>
  <section class="post-grid-section">
    <div class="post-grid-header">
      <div class="post-grid-stats">
        共 <strong>{{ filtered.length }}</strong> 篇
        <span v-if="activeCategory !== '全部'">· {{ activeCategory }}</span>
      </div>
      <div class="category-tabs">
        <button
          v-for="cat in categories"
          :key="cat"
          class="category-tab"
          :class="{ active: activeCategory === cat }"
          @click="selectCategory(cat)"
        >
          {{ cat }}
        </button>
      </div>
    </div>

    <div class="post-card-grid">
      <a
        v-for="post in paged"
        :key="post.link"
        :href="postLink(post.link)"
        class="post-card"
      >
        <div class="post-card-cover" :style="coverStyle(post)">
          <span v-if="mediaIcon(post)" class="post-media-badge">{{
            mediaIcon(post)
          }}</span>
          <span class="post-card-category">{{ post.category }}</span>
        </div>
        <div class="post-card-body">
          <h3 class="post-card-title">{{ post.title }}</h3>
          <p class="post-card-excerpt">{{ post.excerpt }}</p>
          <div class="post-card-meta">
            <time v-if="post.date">{{ post.date }}</time>
            <span v-else class="post-no-date">持续更新</span>
          </div>
        </div>
      </a>
    </div>

    <div v-if="totalPages > 1" class="post-pagination">
      <button :disabled="currentPage <= 1" @click="prevPage">上一页</button>
      <span>{{ currentPage }} / {{ totalPages }}</span>
      <button :disabled="currentPage >= totalPages" @click="nextPage">
        下一页
      </button>
    </div>
  </section>
</template>
